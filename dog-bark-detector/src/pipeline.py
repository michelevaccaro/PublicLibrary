"""Orchestrazione ad alto livello per la web app: analizza tutti i WAV di una
cartella, produce un unico file con gli spezzoni identificati, sposta i file
sorgente in una sottocartella e lascia solo l'output nella cartella originale.

Usa gli stessi moduli (src.detection/postprocess/segments/enhance) della CLI
detect_barks.py, con i parametri di default già tarati sui file reali
dell'utente. --denoise ed --enhance sono attivi di default qui perché è la
combinazione risultata migliore nei test.
"""

import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .detection import detect_candidates_streaming
from .postprocess import merge_and_pad
from .segments import extract_and_concatenate

ANALYZED_SUBDIR = "FileAnalizzati"

DOG_BARK_DETECTION_PARAMS = dict(
    band=(1000.0, 4000.0),
    floor_window_s=3.0,
    floor_percentile=20.0,
    threshold_factor=3.0,
    min_duration_s=0.06,
    max_duration_s=1.0,
    internal_merge_gap_s=0.15,
    min_dominant_freq_hz=700.0,
    max_dominant_freq_hz=3500.0,
    min_band_energy_ratio=0.35,
    min_peak_concentration=0.35,
)

ENHANCE_PARAMS = dict(highpass_hz=400.0, boost_band=(1200.0, 2500.0), boost_gain_db=6.0)
DENOISE_PARAMS = dict(prop_decrease=0.9, stationary=False)

SOUND_TYPES = {
    "dog_bark": {
        "label": "Abbaiare di Cani",
        "available": True,
        "detection_params": DOG_BARK_DETECTION_PARAMS,
        "output_prefix": "abbai",
    },
    "human_speech": {
        "label": "Parlato delle persone",
        "available": False,
        "detection_params": None,
        "output_prefix": "voci",
    },
}


@dataclass
class FileResult:
    path: str
    duration_s: float
    candidate_count: int
    sequence_count: int


@dataclass
class PipelineResult:
    output_path: str
    files: list
    total_sequences: int
    analyzed_dir: str
    moved_files: list


def _is_previous_output(path):
    prefixes = tuple(f"{cfg['output_prefix']}_" for cfg in SOUND_TYPES.values())
    return path.stem.startswith(prefixes) and path.stem.rsplit("_", 2)[-2:][0].isdigit()


def list_wav_files(folder):
    folder = Path(folder)
    return sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() == ".wav" and not _is_previous_output(p)
    )


def run_folder_pipeline(folder, sound_type="dog_bark", progress=None, pad_s=3.0, gap_s=5.0):
    def report(msg):
        if progress:
            progress(msg)

    if sound_type not in SOUND_TYPES or not SOUND_TYPES[sound_type]["available"]:
        raise ValueError(f"Tipo di suono non disponibile: {sound_type}")

    config = SOUND_TYPES[sound_type]
    folder = Path(folder)
    if not folder.is_dir():
        raise NotADirectoryError(f"Cartella non trovata: {folder}")

    wav_files = list_wav_files(folder)
    if not wav_files:
        raise FileNotFoundError(f"Nessun file .wav trovato in {folder}")

    report(f"Trovati {len(wav_files)} file WAV da analizzare")

    sources = []
    file_results = []
    for path in wav_files:
        report(f"Analizzo {path.name}...")
        candidates, sr, duration_s = detect_candidates_streaming(str(path), **config["detection_params"])
        sequences = merge_and_pad(candidates, gap_threshold_s=gap_s, padding_s=pad_s, duration_s=duration_s)
        report(f"  {path.name}: {duration_s:.1f}s, {len(candidates)} candidati, {len(sequences)} sequenze")
        sources.append({"path": str(path), "sequences": sequences})
        file_results.append(FileResult(str(path), duration_s, len(candidates), len(sequences)))

    total_sequences = sum(len(s["sequences"]) for s in sources)
    analyzed_dir = folder / ANALYZED_SUBDIR
    analyzed_dir.mkdir(exist_ok=True)

    output_path = None
    if total_sequences > 0:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{config['output_prefix']}_{timestamp}.wav"
        output_path = folder / output_filename
        report(f"Creo il file combinato con {total_sequences} sequenze totali...")
        extract_and_concatenate(
            sources, output_path,
            enhance=True, enhance_kwargs=ENHANCE_PARAMS,
            denoise=True, denoise_kwargs=DENOISE_PARAMS,
        )
        report(f"Output scritto: {output_filename}")
    else:
        report("Nessuna sequenza trovata in nessun file: nessun output generato")

    moved_files = []
    report_base = output_path.with_suffix("") if output_path else None
    for path in wav_files:
        destination = _unique_destination(analyzed_dir / path.name)
        shutil.move(str(path), str(destination))
        moved_files.append(str(destination))
    if report_base is not None:
        for suffix in ("_report.json", "_report.csv", "_labels.txt"):
            report_file = Path(f"{report_base}{suffix}")
            if report_file.exists():
                shutil.move(str(report_file), str(analyzed_dir / report_file.name))

    report(f"{len(moved_files)} file spostati in {ANALYZED_SUBDIR}/")

    return PipelineResult(
        output_path=str(output_path) if output_path else None,
        files=file_results,
        total_sequences=total_sequences,
        analyzed_dir=str(analyzed_dir),
        moved_files=moved_files,
    )


def _unique_destination(path):
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    counter = 1
    while True:
        candidate = path.with_name(f"{stem}_{counter}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1
