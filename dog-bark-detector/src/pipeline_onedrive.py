"""Come src.pipeline ma con i file su OneDrive invece che su disco locale.

Scarica i WAV della cartella OneDrive in una cartella temporanea sul
server, riusa esattamente la stessa pipeline di rilevamento/estrazione
della versione locale/CLI (nessuna differenza negli algoritmi), poi
carica il risultato su OneDrive e sposta gli originali in FileAnalizzati/
tramite Graph API (senza ri-scaricarli/ri-caricarli: lo spostamento è
solo un cambio di cartella lato Microsoft).
"""

import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from . import onedrive_client as odc
from .detection import detect_candidates_streaming
from .pipeline import ANALYZED_SUBDIR, DENOISE_PARAMS, ENHANCE_PARAMS, SOUND_TYPES, _is_previous_output
from .postprocess import merge_and_pad
from .segments import extract_and_concatenate


@dataclass
class OneDriveFileResult:
    name: str
    duration_s: float
    candidate_count: int
    sequence_count: int


@dataclass
class OneDrivePipelineResult:
    output_name: str
    files: list
    total_sequences: int
    moved_count: int


def run_onedrive_pipeline(access_token, folder_path, sound_type="dog_bark", progress=None, pad_s=3.0, gap_s=5.0):
    def report(msg):
        if progress:
            progress(msg)

    if sound_type not in SOUND_TYPES or not SOUND_TYPES[sound_type]["available"]:
        raise ValueError(f"Tipo di suono non disponibile: {sound_type}")
    config = SOUND_TYPES[sound_type]

    wav_items = odc.list_wav_files(access_token, folder_path)
    wav_items = [item for item in wav_items if not _is_previous_output(Path(item["name"]))]
    if not wav_items:
        raise FileNotFoundError(f"Nessun file .wav trovato in {folder_path}")

    report(f"Trovati {len(wav_items)} file WAV da analizzare")

    tmp_dir = Path(tempfile.mkdtemp(prefix="onedrive_barks_"))
    try:
        sources = []
        file_results = []
        local_paths = []

        for item in wav_items:
            local_path = tmp_dir / item["name"]
            report(f"Scarico {item['name']}...")
            odc.download_file(access_token, item["id"], local_path)
            local_paths.append(local_path)

            report(f"Analizzo {item['name']}...")
            candidates, sr, duration_s = detect_candidates_streaming(str(local_path), **config["detection_params"])
            sequences = merge_and_pad(candidates, gap_threshold_s=gap_s, padding_s=pad_s, duration_s=duration_s)
            report(f"  {item['name']}: {duration_s:.1f}s, {len(candidates)} candidati, {len(sequences)} sequenze")

            sources.append({"path": str(local_path), "sequences": sequences})
            file_results.append(OneDriveFileResult(item["name"], duration_s, len(candidates), len(sequences)))

        total_sequences = sum(len(s["sequences"]) for s in sources)

        report(f"Creo la sottocartella {ANALYZED_SUBDIR} su OneDrive (se non esiste)...")
        analyzed_folder = odc.ensure_subfolder(access_token, folder_path, ANALYZED_SUBDIR)
        analyzed_path = f"{folder_path.strip('/')}/{ANALYZED_SUBDIR}"

        output_name = None
        if total_sequences > 0:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"{config['output_prefix']}_{timestamp}.wav"
            local_output = tmp_dir / output_name
            report(f"Creo il file combinato con {total_sequences} sequenze totali...")
            extract_and_concatenate(
                sources, local_output,
                enhance=True, enhance_kwargs=ENHANCE_PARAMS,
                denoise=True, denoise_kwargs=DENOISE_PARAMS,
            )
            report(f"Carico {output_name} su OneDrive...")
            odc.upload_file(access_token, folder_path, output_name, local_output)

            report_base = local_output.with_suffix("")
            for suffix in ("_report.json", "_report.csv", "_labels.txt"):
                report_file = Path(f"{report_base}{suffix}")
                if report_file.exists():
                    odc.upload_file(access_token, analyzed_path, report_file.name, report_file)
        else:
            report("Nessuna sequenza trovata in nessun file: nessun output generato")

        moved_count = 0
        for item in wav_items:
            report(f"Sposto {item['name']} in {ANALYZED_SUBDIR}/...")
            odc.move_item(access_token, item["id"], analyzed_folder["id"])
            moved_count += 1

        return OneDrivePipelineResult(
            output_name=output_name,
            files=file_results,
            total_sequences=total_sequences,
            moved_count=moved_count,
        )
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
