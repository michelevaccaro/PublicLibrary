"""Rilevamento dei candidati abbaio: energia in banda + forma spettrale.

Non usa modelli ML: lavora sul segnale filtrato in banda (1-4kHz, dove
si concentra l'abbaio del Chihuahua secondo l'analisi spettrale fatta
sui file di test) e cerca picchi di energia sostenuti rispetto al
rumore di fondo locale, poi li conferma controllando che la forma
spettrale assomigli a un abbaio (frequenza dominante ed energia in
banda) invece che a un rumore a banda larga (treno, traffico).
"""

from dataclasses import dataclass

import numpy as np
import librosa
from scipy.ndimage import percentile_filter

from .filters import bandpass_filter


@dataclass
class Candidate:
    start: float
    end: float
    peak_rms: float
    dominant_freq_hz: float
    band_energy_ratio: float


def _rms_envelope(audio, sr, frame_length_s=0.05, hop_length_s=0.01):
    frame_length = int(frame_length_s * sr)
    hop_length = int(hop_length_s * sr)
    rms = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)
    return rms, times, hop_length_s


def _spectral_shape(raw_segment, filtered_segment, sr, band=(1000.0, 4000.0)):
    """Frequenza dominante presa dal segnale filtrato (il grezzo è dominato
    dal rumore a bassa frequenza anche su finestre brevi); il rapporto di
    energia in banda è invece calcolato sul segnale grezzo, perché confrontare
    il filtrato con sé stesso darebbe sempre ~100%."""
    if len(raw_segment) < 32:
        return 0.0, 0.0

    raw_spectrum = np.abs(np.fft.rfft(raw_segment))
    total_energy = np.sum(raw_spectrum ** 2)
    if total_energy <= 0:
        return 0.0, 0.0
    freqs = np.fft.rfftfreq(len(raw_segment), d=1.0 / sr)
    band_mask = (freqs >= band[0]) & (freqs <= band[1])
    band_energy_ratio = float(np.sum(raw_spectrum[band_mask] ** 2) / total_energy)

    filtered_spectrum = np.abs(np.fft.rfft(filtered_segment))
    dominant_freq = float(freqs[np.argmax(filtered_spectrum)])

    return dominant_freq, band_energy_ratio


def detect_candidates(
    audio,
    sr,
    band=(1000.0, 4000.0),
    floor_window_s=3.0,
    floor_percentile=20,
    threshold_factor=3.0,
    min_duration_s=0.06,
    max_duration_s=1.0,
    internal_merge_gap_s=0.15,
    min_dominant_freq_hz=700.0,
    max_dominant_freq_hz=3500.0,
    min_band_energy_ratio=0.35,
):
    filtered = bandpass_filter(audio, sr, band[0], band[1])
    rms, times, hop_length_s = _rms_envelope(filtered, sr)

    window_frames = max(3, int(floor_window_s / hop_length_s))
    floor = percentile_filter(rms, percentile=floor_percentile, size=window_frames, mode="nearest")
    threshold = np.maximum(floor * threshold_factor, 1e-6)

    above = rms > threshold
    regions = _contiguous_regions(above, times, min_duration_s, internal_merge_gap_s)

    candidates = []
    for start, end in regions:
        if end - start > max_duration_s:
            end = start + max_duration_s
        start_sample = max(0, int(start * sr))
        end_sample = min(len(audio), int(end * sr))
        raw_segment = audio[start_sample:end_sample]
        filtered_segment = filtered[start_sample:end_sample]
        dominant_freq, band_energy_ratio = _spectral_shape(raw_segment, filtered_segment, sr, band)

        if not (min_dominant_freq_hz <= dominant_freq <= max_dominant_freq_hz):
            continue
        if band_energy_ratio < min_band_energy_ratio:
            continue

        peak_rms = float(np.max(rms[(times >= start) & (times <= end)])) if end > start else 0.0
        candidates.append(Candidate(start, end, peak_rms, dominant_freq, band_energy_ratio))

    return candidates


def _contiguous_regions(mask, times, min_duration_s, merge_gap_s):
    if not np.any(mask):
        return []

    edges = np.diff(mask.astype(int))
    starts = list(np.where(edges == 1)[0] + 1)
    ends = list(np.where(edges == -1)[0] + 1)
    if mask[0]:
        starts.insert(0, 0)
    if mask[-1]:
        ends.append(len(mask))

    raw_regions = [(float(times[s]), float(times[min(e, len(times) - 1)])) for s, e in zip(starts, ends)]

    merged = []
    for start, end in raw_regions:
        if merged and start - merged[-1][1] < merge_gap_s:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    return [(s, e) for s, e in merged if e - s >= min_duration_s]
