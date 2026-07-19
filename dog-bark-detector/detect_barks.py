#!/usr/bin/env python3
"""CLI: rileva sequenze di abbaio in file WAV lunghi e le concatena in output.

Esempio:
    python detect_barks.py registrazione.wav -o output/combined.wav --export-segments

Per iterare velocemente sui parametri senza tagliare l'audio ogni volta:
    python detect_barks.py registrazione.wav --dry-run
"""

import argparse
import os
from pathlib import Path

import librosa
import soundfile as sf

from src.detection import detect_candidates_streaming
from src.postprocess import merge_and_pad
from src.segments import extract_and_concatenate


def parse_band(value):
    low, high = value.split("-")
    return float(low), float(high)


def build_parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("inputs", nargs="+", help="File WAV da analizzare (uno o più)")
    p.add_argument("-o", "--output", default="output/combined_barks.wav", help="File audio finale concatenato")
    p.add_argument("--export-segments", action="store_true", help="Salva anche i singoli segmenti separati")
    p.add_argument("--dry-run", action="store_true", help="Analizza e stampa il report senza tagliare l'audio")
    p.add_argument("--sort", choices=["name", "mtime"], default="name", help="Ordine cronologico dei file in input")
    p.add_argument("--block-seconds", type=float, default=600.0,
                   help="Dimensione (s) dei blocchi letti dal disco durante l'analisi (file letti a chunk, mai tutti in RAM)")
    p.add_argument("--block-overlap-seconds", type=float, default=10.0,
                   help="Margine di contesto (s) letto attorno a ogni blocco")

    p.add_argument("--pad", type=float, default=3.0, help="Margine in secondi prima/dopo ogni sequenza")
    p.add_argument("--gap", type=float, default=5.0, help="Gap massimo (s) tra abbai per unirli in una sequenza")

    p.add_argument("--band", type=parse_band, default="1000-4000", help="Banda di frequenza dell'abbaio, es. 1000-4000")
    p.add_argument("--floor-window", type=float, default=3.0, help="Finestra (s) per stimare il rumore di fondo")
    p.add_argument("--floor-percentile", type=float, default=20.0, help="Percentile usato come rumore di fondo")
    p.add_argument("--threshold-factor", type=float, default=3.0, help="Moltiplicatore sopra il rumore di fondo")
    p.add_argument("--min-duration", type=float, default=0.06, help="Durata minima (s) di un candidato abbaio")
    p.add_argument("--max-duration", type=float, default=1.0, help="Durata massima (s) di un singolo abbaio")
    p.add_argument("--internal-merge-gap", type=float, default=0.15, help="Gap (s) per unire picchi dello stesso abbaio")
    p.add_argument("--min-dominant-freq", type=float, default=700.0, help="Frequenza dominante minima accettata (Hz)")
    p.add_argument("--max-dominant-freq", type=float, default=3500.0, help="Frequenza dominante massima accettata (Hz)")
    p.add_argument("--min-band-energy-ratio", type=float, default=0.35, help="Frazione minima di energia in banda")
    p.add_argument("--min-peak-concentration", type=float, default=0.35,
                   help="Frazione minima di energia concentrata attorno al picco (scarta rumori a banda larga tipo passi)")

    p.add_argument("--use-yamnet", action="store_true", help="Conferma i candidati con YAMNet (richiede tensorflow)")
    p.add_argument("--yamnet-threshold", type=float, default=0.1, help="Soglia di confidenza minima per YAMNet")

    p.add_argument("--normalize-dbfs", type=float, default=-1.0, help="Picco target (dBFS) di normalizzazione dell'output")
    p.add_argument("--no-normalize", action="store_true", help="Disabilita la normalizzazione del volume in output")

    p.add_argument("--enhance", action="store_true",
                    help="Esalta l'abbaio rispetto al rumore di fondo (taglia sotto --enhance-highpass, "
                         "rinforza la banda --enhance-boost-band). Attiva anche il gate di rumore, salvo --no-gate")
    p.add_argument("--enhance-highpass", type=float, default=600.0, help="Frequenza (Hz) sotto cui tagliare il rumore di fondo")
    p.add_argument("--enhance-boost-band", type=parse_band, default="1200-2500", help="Banda da rinforzare, es. 1200-2500")
    p.add_argument("--enhance-boost-db", type=float, default=9.0, help="Guadagno (dB) applicato alla banda rinforzata")

    p.add_argument("--gate", action="store_true",
                    help="Abbassa il rumore di fondo fuori dalle finestre di abbaio effettive (attivo di default con --enhance)")
    p.add_argument("--no-gate", action="store_true", help="Disabilita il gate anche se --enhance è attivo")
    p.add_argument("--gate-attack", type=float, default=0.15,
                   help="Margine (s) di piena apertura del gate prima/dopo ogni abbaio, con transizione ammorbidita")
    p.add_argument("--gate-noise-floor-db", type=float, default=-20.0,
                   help="Attenuazione (dB) applicata al rumore di fondo fuori dalle finestre di abbaio")

    return p


def sort_inputs(paths, mode):
    if mode == "mtime":
        return sorted(paths, key=lambda p: os.path.getmtime(p))
    return sorted(paths)


def maybe_confirm_with_yamnet(path, sr, candidates, threshold):
    from src.yamnet_confirm import confirm_segment

    confirmed = []
    for c in candidates:
        segment, _ = sf.read(path, start=int(c.start * sr), frames=int((c.end - c.start) * sr),
                              dtype="float32", always_2d=False)
        if segment.ndim > 1:
            segment = segment.mean(axis=1)
        segment_16k = librosa.resample(segment, orig_sr=sr, target_sr=16000)
        is_dog, score, top = confirm_segment(segment_16k, threshold=threshold)
        print(f"    yamnet: score={score:.3f} top={top[:3]} -> {'OK' if is_dog else 'scartato'}")
        if is_dog:
            confirmed.append(c)
    return confirmed


def main():
    args = build_parser().parse_args()
    inputs = sort_inputs(args.inputs, args.sort)

    sources = []
    for path in inputs:
        print(f"\n=== {path} ===")

        candidates, sr, duration_s = detect_candidates_streaming(
            path,
            block_seconds=args.block_seconds,
            overlap_seconds=args.block_overlap_seconds,
            band=args.band,
            floor_window_s=args.floor_window,
            floor_percentile=args.floor_percentile,
            threshold_factor=args.threshold_factor,
            min_duration_s=args.min_duration,
            max_duration_s=args.max_duration,
            internal_merge_gap_s=args.internal_merge_gap,
            min_dominant_freq_hz=args.min_dominant_freq,
            max_dominant_freq_hz=args.max_dominant_freq,
            min_band_energy_ratio=args.min_band_energy_ratio,
            min_peak_concentration=args.min_peak_concentration,
        )
        print(f"durata: {duration_s:.1f}s, sample rate: {sr}Hz")
        print(f"candidati grezzi (energia+spettro): {len(candidates)}")
        for c in candidates:
            print(f"  [{c.start:7.2f}s -> {c.end:7.2f}s] freq_dom={c.dominant_freq_hz:6.0f}Hz "
                  f"band_ratio={c.band_energy_ratio:.2f} concentration={c.peak_concentration:.2f} rms={c.peak_rms:.4f}")

        if args.use_yamnet and candidates:
            print("conferma con YAMNet...")
            candidates = maybe_confirm_with_yamnet(path, sr, candidates, args.yamnet_threshold)
            print(f"candidati confermati da YAMNet: {len(candidates)}")

        sequences = merge_and_pad(candidates, gap_threshold_s=args.gap, padding_s=args.pad, duration_s=duration_s)
        print(f"sequenze finali (dopo padding {args.pad}s e merge gap<{args.gap}s): {len(sequences)}")
        for s in sequences:
            print(f"  [{s.start:7.2f}s -> {s.end:7.2f}s] {s.bark_count} abbai: {[round(b, 1) for b in s.bark_starts]}")

        sources.append({"path": path, "sequences": sequences})

    total_sequences = sum(len(s["sequences"]) for s in sources)
    if total_sequences == 0:
        print("\nNessuna sequenza di abbaio rilevata. Prova ad allentare i parametri di soglia.")
        return

    if args.dry_run:
        print("\n--dry-run: nessun file audio scritto.")
        return

    segments_dir = Path(args.output).with_suffix("") if args.export_segments else None
    normalize_target = None if args.no_normalize else args.normalize_dbfs
    enhance_kwargs = {
        "highpass_hz": args.enhance_highpass,
        "boost_band": args.enhance_boost_band,
        "boost_gain_db": args.enhance_boost_db,
    }
    gate_enabled = (args.gate or args.enhance) and not args.no_gate
    gate_kwargs = {
        "attack_s": args.gate_attack,
        "noise_floor_db": args.gate_noise_floor_db,
    }
    report = extract_and_concatenate(
        sources, args.output, segments_dir=segments_dir, normalize_target_dbfs=normalize_target,
        enhance=args.enhance, enhance_kwargs=enhance_kwargs,
        gate=gate_enabled, gate_kwargs=gate_kwargs,
    )
    print(f"\nOutput scritto: {args.output}")
    print(f"Report: {Path(args.output).with_suffix('')}_report.csv / .json / _labels.txt")
    print(f"Segmenti totali nel file finale: {len(report)}")


if __name__ == "__main__":
    main()
