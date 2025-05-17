from flask import Flask, request, jsonify, send_from_directory
import os
from datetime import datetime
from deepface import DeepFace

app = Flask(__name__)

# Foldere pentru imagini
UPLOAD_FOLDER = 'uploads'
KNOWN_FOLDER = 'known_faces'

# Creăm folderele dacă nu există
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(KNOWN_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return "✅ Serverul de recunoaștere facială funcționează."

@app.route('/upload', methods=['POST'])
def upload():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"visitor_{timestamp}.jpg"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(file_path, 'wb') as f:
        f.write(request.data)

    print(f"[📸] Imagine primită și salvată: {file_path}")

    try:
        result = DeepFace.find(
            img_path=file_path,
            db_path=KNOWN_FOLDER,
            model_name="VGG-Face",
            enforce_detection=False
        )

        match_found = len(result) > 0 and not result[0].empty
        print(f"[🤖] Acces {'PERMIS' if match_found else 'REFUZAT'}")

        return jsonify({"access_granted": match_found})
    except Exception as e:
        print(f"[❌ EROARE] {str(e)}")
        return jsonify({"access_granted": False, "error": str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/gallery')
def gallery():
    files = sorted(os.listdir(UPLOAD_FOLDER), reverse=True)
    links = [
        f"<a href='/uploads/{f}' target='_blank'>"
        f"<img src='/uploads/{f}?t={datetime.now().timestamp()}' width='200' style='margin: 10px;'></a>"
        for f in files if f.lower().endswith(".jpg")
    ]
    return "<h2>Galerie vizitatori</h2>" + "<br>".join(links)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)