"""Taglio, concatenazione e reportistica dei segmenti di abbaio."""

import csv
import json
from pathlib import Path

import numpy as np
import soundfile as sf
import librosa

from .enhance import enhance_bark_presence, denoise_background


def _read_range(path, start_s, end_s):
    info = sf.info(path)
    start_frame = max(0, int(start_s * info.samplerate))
    end_frame = min(info.frames, int(end_s * info.samplerate))
    data, sr = sf.read(path, start=start_frame, frames=end_frame - start_frame, dtype="float32", always_2d=True)
    return data, sr


def _to_mono_if_needed(data, target_channels):
    if data.shape[1] == target_channels:
        return data
    if target_channels == 1:
        return np.mean(data, axis=1, keepdims=True)
    return np.repeat(np.mean(data, axis=1, keepdims=True), target_channels, axis=1)


def extract_and_concatenate(
    sources, output_path, segments_dir=None, target_sr=None, target_channels=1,
    normalize_target_dbfs=-1.0, enhance=False, enhance_kwargs=None,
    denoise=False, denoise_kwargs=None,
):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if segments_dir is not None:
        segments_dir = Path(segments_dir)
        segments_dir.mkdir(parents=True, exist_ok=True)

    chunks = []
    clip_names = []
    report_rows = []
    output_offset_s = 0.0
    segment_index = 0

    for source in sources:
        path = source["path"]
        source_sr = sf.info(path).samplerate
        this_target_sr = target_sr or source_sr

        for seq in source["sequences"]:
            data, sr = _read_range(path, seq.start, seq.end)
            data = _to_mono_if_needed(data, target_channels)

            if sr != this_target_sr:
                data = np.stack(
                    [librosa.resample(data[:, ch], orig_sr=sr, target_sr=this_target_sr) for ch in range(data.shape[1])],
                    axis=1,
                )
                sr = this_target_sr

            if denoise:
                data = denoise_background(data, sr, **(denoise_kwargs or {}))

            if enhance:
                data = enhance_bark_presence(data, sr, **(enhance_kwargs or {}))

            segment_index += 1
            duration_s = len(data) / sr

            clip_names.append(f"{segment_index:03d}_{Path(path).stem}_{seq.start:.1f}-{seq.end:.1f}.wav")
            report_rows.append({
                "segment_index": segment_index,
                "source_file": str(path),
                "original_start_s": round(seq.start, 3),
                "original_end_s": round(seq.end, 3),
                "duration_s": round(duration_s, 3),
                "bark_count": seq.bark_count,
                "bark_starts_s": [round(b, 3) for b in seq.bark_starts],
                "output_offset_s": round(output_offset_s, 3),
            })

            chunks.append(data)
            output_offset_s += duration_s

    if not chunks:
        return report_rows

    final_sr = target_sr or sf.info(sources[0]["path"]).samplerate

    gain = _normalization_gain(chunks, normalize_target_dbfs)
    if gain != 1.0:
        chunks = [np.clip(chunk * gain, -1.0, 1.0) for chunk in chunks]

    if segments_dir is not None:
        for clip_name, data in zip(clip_names, chunks):
            sf.write(segments_dir / clip_name, data, final_sr, subtype="PCM_16")

    concatenated = np.concatenate(chunks, axis=0)
    sf.write(output_path, concatenated, final_sr, subtype="PCM_16")

    _write_reports(report_rows, output_path)
    return report_rows


def _normalization_gain(chunks, target_dbfs):
    if target_dbfs is None:
        return 1.0
    peak = max((float(np.max(np.abs(chunk))) for chunk in chunks if chunk.size), default=0.0)
    if peak <= 0:
        return 1.0
    target_peak = 10 ** (target_dbfs / 20.0)
    return target_peak / peak


def _write_reports(report_rows, output_path):
    base = output_path.with_suffix("")

    with open(f"{base}_report.json", "w", encoding="utf-8") as f:
        json.dump(report_rows, f, indent=2, ensure_ascii=False)

    with open(f"{base}_report.csv", "w", newline="", encoding="utf-8") as f:
        if report_rows:
            writer = csv.DictWriter(f, fieldnames=list(report_rows[0].keys()))
            writer.writeheader()
            for row in report_rows:
                writer.writerow(row)

    with open(f"{base}_labels.txt", "w", encoding="utf-8") as f:
        for row in report_rows:
            label = f"seg{row['segment_index']:03d} ({row['bark_count']} bark)"
            end = row["output_offset_s"] + row["duration_s"]
            f.write(f"{row['output_offset_s']:.3f}\t{end:.3f}\t{label}\n")
