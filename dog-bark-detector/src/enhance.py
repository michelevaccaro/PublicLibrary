"""Esalta la presenza dell'abbaio rispetto al rumore di fondo nell'output.

Il registratore, fermo e non direzionale a 60 metri, cattura il rumore a
bassa frequenza (treni, traffico) molto più forte di quanto lo si percepisca
a orecchio dal balcone, dove l'abbaio risulta relativamente più presente e
fastidioso. Per avvicinare l'ascolto all'esperienza reale: si taglia il
rumore sotto la frequenza dell'abbaio (passa-alto) e si somma un boost
parallelo nella banda dove si concentra l'abbaio, invece di isolarlo del
tutto con un passa-banda stretto (che lo farebbe suonare innaturale/sottile).
"""

import numpy as np
from scipy.signal import butter, sosfiltfilt

from .filters import bandpass_filter


def enhance_bark_presence(audio, sr, highpass_hz=400.0, boost_band=(1200.0, 2500.0), boost_gain_db=6.0):
    single_channel = audio.ndim == 1
    data = audio[:, None] if single_channel else audio

    hp_sos = butter(2, highpass_hz / (sr / 2.0), btype="highpass", output="sos")
    boost_gain = 10 ** (boost_gain_db / 20.0)

    out = np.zeros_like(data)
    for ch in range(data.shape[1]):
        channel = data[:, ch]
        highpassed = sosfiltfilt(hp_sos, channel)
        boosted = bandpass_filter(channel, sr, boost_band[0], boost_band[1])
        out[:, ch] = highpassed + boost_gain * boosted

    return out[:, 0] if single_channel else out


def build_gate_envelope(n_samples, sr, bark_windows, attack_s=0.15, noise_floor_db=-18.0):
    """Inviluppo di guadagno: pieno volume attorno a ogni abbaio, rumore di
    fondo abbassato di noise_floor_db altrove (padding, gap tra abbai).
    Le transizioni sono ammorbidite con una finestra di Hann per evitare
    click, con un margine (attack_s) prima/dopo ogni abbaio per non
    tagliarne l'attacco o la coda."""
    noise_gain = 10 ** (noise_floor_db / 20.0)
    mask = np.full(n_samples, noise_gain, dtype=np.float64)
    attack_samples = max(1, int(attack_s * sr))

    for start_s, end_s in bark_windows:
        start_sample = max(0, int(start_s * sr) - attack_samples)
        end_sample = min(n_samples, int(end_s * sr) + attack_samples)
        if end_sample > start_sample:
            mask[start_sample:end_sample] = 1.0

    smooth_samples = attack_samples if attack_samples % 2 == 1 else attack_samples + 1
    if smooth_samples > 1 and n_samples > smooth_samples:
        kernel = np.hanning(smooth_samples)
        kernel /= kernel.sum()
        mask = np.convolve(mask, kernel, mode="same")
        mask = np.clip(mask, noise_gain, 1.0)

    return mask.astype(np.float32)


def apply_noise_gate(audio, sr, bark_windows, attack_s=0.15, noise_floor_db=-18.0):
    single_channel = audio.ndim == 1
    data = audio[:, None] if single_channel else audio

    envelope = build_gate_envelope(data.shape[0], sr, bark_windows, attack_s, noise_floor_db)
    gated = data * envelope[:, None]

    return gated[:, 0] if single_channel else gated
