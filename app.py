from flask import Flask, request, jsonify
import os
from datetime import datetime
from deepface import DeepFace
from flask import send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
KNOWN_FOLDER = "known_faces"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(KNOWN_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return "✅ Serverul de recunoastere faciala este online."

@app.route("/upload", methods=["POST"])
def upload():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{UPLOAD_FOLDER}/visitor_{timestamp}.jpg"

    with open(filename, "wb") as f:
        f.write(request.data)

    print(f"[📸] Imagine primita: {filename}")

    try:
        result = DeepFace.find(
            img_path=filename,
            db_path=KNOWN_FOLDER,
            model_name="Facenet",
            enforce_detection=False
        )

        match_found = len(result) > 0 and not result[0].empty
        print(f"[🤖] Acces {'PERMIS' if match_found else 'REFUZAT'}")
        return jsonify({"access_granted": match_found})

    except Exception as e:
        print(f"[❌ EROARE] {str(e)}")
        return jsonify({"access_granted": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/gallery')
def gallery():
    files = os.listdir(UPLOAD_FOLDER)
    links = [f"<a href='/uploads/{f}' target='_blank'>{f}</a>" for f in files]
    return "<br>".join(links)