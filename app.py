import os
import threading
import uuid
import glob
import json
import subprocess
from flask import Flask, request, jsonify, send_file, render_template

app = Flask(__name__)
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

jobs = {}

def run_download(job_id, url, format_choice, format_id):
    job = jobs[job_id]
    out_template = os.path.join(DOWNLOAD_DIR, f"{job_id}.%(ext)s")

    # Comando base con cookies incluido
    cmd = ["yt-dlp", "--no-playlist", "--cookies", "cookies.txt", "-o", out_template]

    if format_choice == "audio":
        cmd += ["-x", "--audio-format", "mp3"]
    elif format_id:
        cmd += ["-f", f"{format_id}+bestaudio/best", "--merge-output-format", "mp4"]
    else:
        cmd += ["-f", "bestvideo+bestaudio/best", "--merge-output-format", "mp4"]

    cmd.append(url)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            job["status"] = "error"
            job["error"] = result.stderr.strip().split("\n")[-1]
            return

        files = glob.glob(os.path.join(DOWNLOAD_DIR, f"{job_id}.*"))
        if not files:
            job["status"] = "error"
            job["error"] = "Download completed but no file was found"
            return

        if format_choice == "audio":
            target = [f for f in files if f.endswith(".mp3")]
            chosen = target[0] if target else files[0]
        else:
            target = [f for f in files if f.endswith(".mp4")]
            chosen = target[0] if target else files[0]

        # Eliminar otros archivos temporales (si los hay)
        for f in files:
            if f != chosen:
                try:
                    os.remove(f)
                except OSError:
                    pass

        job["status"] = "done"
        job["file"] = chosen
        ext = os.path.splitext(chosen)[1]
        title = job.get("title", "").strip()
        if title:
            safe_title = "".join(c for c in title if c not in r'\/:*?"<>|').strip()[:20].strip()
            job["filename"] = f"{safe_title}{ext}" if safe_title else os.path.basename(chosen)
        else:
            job["filename"] = os.path.basename(chosen)
    except subprocess.TimeoutExpired:
        job["status"] = "error"
        job["error"] = "Download timed out (5 min limit)"
    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/info", methods=["POST"])
def get_info():
    data = request.json
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # La adición de '--cookies' es crucial para evitar bloqueos
    cmd = ["yt-dlp", "--no-playlist", "--cookies", "cookies.txt", "-j", url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip().split("\n")[-1]}), 400

        info = json.loads(result.stdout)

        # --- Nueva lógica de filtrado y formateo ---
        best_by_resolution = {}
        for f in info.get("formats", []):
            # Filtramos para quedarnos solo con los formatos de video que tengan resolución
            height = f.get("height")
            if height and f.get("vcodec", "none") != "none":
                # Usamos la tasa de bits total (tbr) para elegir el mejor formato por resolución
                tbr = f.get("tbr") or 0
                if height not in best_by_resolution or tbr > (best_by_resolution[height].get("tbr") or 0):
                    best_by_resolution[height] = f

        # Construimos la lista de formatos que se enviará al frontend
        formats_to_send = []
        for height, f in best_by_resolution.items():
            # Formateamos el nombre de la calidad (ej: "1080p")
            label = f"{height}p"
            # Obtenemos el tamaño del archivo, aproximado si no es exacto
            file_size = f.get("filesize") or f.get("filesize_approx")
            size_mb = round(file_size / (1024 * 1024), 1) if file_size else None

            format_data = {
                "id": f["format_id"],
                "label": label,
                "height": height,
                "size_mb": size_mb
            }
            # Si no se pudo calcular el tamaño, lo indicamos en la interfaz más tarde
            if not file_size:
                format_data["size_mb"] = None
            formats_to_send.append(format_data)

        # Ordenamos las calidades de mayor a menor (ej: 1080p, 720p...)
        formats_to_send.sort(key=lambda x: x["height"], reverse=True)
        # ---------------------------------------

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "formats": formats_to_send  # <-- Ahora esto tiene la info que necesitamos
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Timeout fetching video info"}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid response from yt-dlp"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/download", methods=["POST"])
def start_download():
    data = request.json
    url = data.get("url", "").strip()
    format_choice = data.get("format_choice", "video")  # 'video' o 'audio'
    format_id = data.get("format_id", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "pending",
        "title": data.get("title", ""),
        "error": None,
        "file": None,
        "filename": None
    }

    thread = threading.Thread(target=run_download, args=(job_id, url, format_choice, format_id))
    thread.daemon = True
    thread.start()

    return jsonify({"job_id": job_id}), 202

@app.route("/api/status/<job_id>")
def check_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify({
        "status": job["status"],
        "error": job.get("error"),
        "filename": job.get("filename"),
    })

@app.route("/api/file/<job_id>")
def download_file(job_id):
    job = jobs.get(job_id)
    if not job or job["status"] != "done":
        return jsonify({"error": "File not ready"}), 404
    return send_file(job["file"], as_attachment=True, download_name=job["filename"])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8899))
    app.run(host='0.0.0.0', port=port, debug=False)
