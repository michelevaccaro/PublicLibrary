#!/usr/bin/env python3
"""Web app locale per rilevare abbai (e in futuro voci) nei file WAV di una cartella.

Avvio:
    python webapp/app.py
Poi apri http://127.0.0.1:5000 nel browser.

Gira solo in locale: legge/scrive direttamente sul filesystem del PC su cui
viene avviata (es. la cartella OneDrive già sincronizzata localmente).
"""

import sys
import traceback
from pathlib import Path

from flask import Flask, jsonify, render_template, request

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pipeline import SOUND_TYPES, list_wav_files, run_folder_pipeline

app = Flask(__name__)


@app.route("/")
def index():
    sound_types = [
        {"id": key, "label": cfg["label"], "available": cfg["available"]}
        for key, cfg in SOUND_TYPES.items()
    ]
    return render_template("index.html", sound_types=sound_types)


@app.route("/api/validate-folder", methods=["POST"])
def validate_folder():
    folder = (request.json or {}).get("folder", "").strip()
    if not folder:
        return jsonify({"valid": False, "message": "Inserisci un percorso"}), 200

    path = Path(folder)
    if not path.is_dir():
        return jsonify({"valid": False, "message": "Cartella non trovata"}), 200

    wav_files = list_wav_files(path)
    if not wav_files:
        return jsonify({"valid": False, "message": "Nessun file .wav trovato in questa cartella"}), 200

    return jsonify({
        "valid": True,
        "message": f"{len(wav_files)} file WAV trovati",
        "files": [f.name for f in wav_files],
    })


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.json or {}
    folder = data.get("folder", "").strip()
    sound_type = data.get("sound_type", "dog_bark")

    if not folder:
        return jsonify({"error": "Cartella mancante"}), 400

    log_lines = []

    def progress(msg):
        log_lines.append(msg)

    try:
        result = run_folder_pipeline(folder, sound_type=sound_type, progress=progress)
    except (NotADirectoryError, FileNotFoundError, ValueError) as e:
        return jsonify({"error": str(e), "log": log_lines}), 400
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Errore imprevisto durante l'analisi, controlla i log del server", "log": log_lines}), 500

    return jsonify({
        "output_path": result.output_path,
        "total_sequences": result.total_sequences,
        "analyzed_dir": result.analyzed_dir,
        "moved_files_count": len(result.moved_files),
        "files": [
            {
                "path": f.path,
                "duration_s": round(f.duration_s, 1),
                "candidate_count": f.candidate_count,
                "sequence_count": f.sequence_count,
            }
            for f in result.files
        ],
        "log": log_lines,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
