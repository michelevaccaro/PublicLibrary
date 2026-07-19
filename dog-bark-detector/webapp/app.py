#!/usr/bin/env python3
"""Web app (OneDrive): rileva abbai nei file WAV di una cartella OneDrive.

In locale (per sviluppo):
    python webapp/app.py
In produzione (Render): gunicorn -w 2 -b 0.0.0.0:$PORT webapp.app:app

Richiede le variabili d'ambiente ONEDRIVE_CLIENT_ID, ONEDRIVE_CLIENT_SECRET,
ONEDRIVE_TENANT_ID (vedi src/onedrive_auth.py).
"""

import os
import secrets
import sys
import traceback
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import onedrive_auth
from src.onedrive_client import OneDriveError, list_folder_children
from src.pipeline import SOUND_TYPES
from src.pipeline_onedrive import run_onedrive_pipeline

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)


@app.route("/")
def index():
    sound_types = [
        {"id": key, "label": cfg["label"], "available": cfg["available"]}
        for key, cfg in SOUND_TYPES.items()
    ]
    return render_template("index.html", sound_types=sound_types, logged_in=onedrive_auth.is_logged_in())


@app.route("/auth/login")
def auth_login():
    state = secrets.token_hex(16)
    session["oauth_state"] = state
    redirect_uri = url_for("auth_callback", _external=True)
    return redirect(onedrive_auth.get_auth_url(redirect_uri, state))


@app.route("/auth/callback")
def auth_callback():
    if request.args.get("state") != session.get("oauth_state"):
        return "Stato OAuth non valido, riprova il login dalla home.", 400

    error = request.args.get("error_description")
    if error:
        return f"Login fallito: {error}", 400

    code = request.args.get("code")
    if not code:
        return "Login fallito: nessun codice ricevuto da Microsoft.", 400

    redirect_uri = url_for("auth_callback", _external=True)
    try:
        onedrive_auth.acquire_token_by_auth_code(code, redirect_uri)
    except RuntimeError as e:
        return str(e), 400

    return redirect(url_for("index"))


@app.route("/auth/logout")
def auth_logout():
    onedrive_auth.logout()
    return redirect(url_for("index"))


@app.route("/api/validate-folder", methods=["POST"])
def validate_folder():
    token = onedrive_auth.get_access_token()
    if not token:
        return jsonify({"valid": False, "message": "Devi prima collegare OneDrive"}), 200

    folder = (request.json or {}).get("folder", "").strip()
    if not folder:
        return jsonify({"valid": False, "message": "Inserisci il percorso della cartella su OneDrive"}), 200

    try:
        children = list_folder_children(token, folder)
    except OneDriveError as e:
        return jsonify({"valid": False, "message": f"Cartella non trovata o errore: {e}"}), 200

    wav_files = [c["name"] for c in children if "file" in c and c["name"].lower().endswith(".wav")]
    if not wav_files:
        return jsonify({"valid": False, "message": "Nessun file .wav trovato in questa cartella"}), 200

    return jsonify({"valid": True, "message": f"{len(wav_files)} file WAV trovati", "files": wav_files})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    token = onedrive_auth.get_access_token()
    if not token:
        return jsonify({"error": "Devi prima collegare OneDrive"}), 401

    data = request.json or {}
    folder = data.get("folder", "").strip()
    sound_type = data.get("sound_type", "dog_bark")
    if not folder:
        return jsonify({"error": "Cartella mancante"}), 400

    log_lines = []

    def progress(msg):
        log_lines.append(msg)

    try:
        result = run_onedrive_pipeline(token, folder, sound_type=sound_type, progress=progress)
    except (FileNotFoundError, ValueError) as e:
        return jsonify({"error": str(e), "log": log_lines}), 400
    except OneDriveError as e:
        return jsonify({"error": f"Errore OneDrive: {e}", "log": log_lines}), 502
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Errore imprevisto durante l'analisi, controlla i log del server", "log": log_lines}), 500

    return jsonify({
        "output_name": result.output_name,
        "total_sequences": result.total_sequences,
        "moved_count": result.moved_count,
        "files": [
            {
                "name": f.name,
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
