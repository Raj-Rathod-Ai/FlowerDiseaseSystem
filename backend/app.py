from flask import Flask, request, jsonify
from pathlib import Path
import os
from hashlib import sha512
import uuid
import cv2
import numpy as np
from tensorflow.keras.models import load_model
import json
from flask_cors import CORS
import gdown   # ✅ ADDED

app = Flask(__name__)

# ✅ Allow all origins (important for deployment)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent

# ✅ Correct paths (ensure these folders exist in GitHub)
MODEL_PATH = BASE_DIR / "models/multitask_finetuned.keras"
FALLBACK_MODEL_PATH = BASE_DIR / "models/multitask_best.keras"
LABEL_MAP_PATH = BASE_DIR / "manifests/label_map.json"

# ✅ ADDED DOWNLOAD BLOCK (IMPORTANT)
MODEL_PATH.parent.mkdir(exist_ok=True)

if not MODEL_PATH.exists():
    print("Downloading main model...")
    gdown.download("https://drive.google.com/uc?id=1ClzyqzqoZBlp7dcNlnX_xBQvUFtt29QL", str(MODEL_PATH), quiet=False)

if not FALLBACK_MODEL_PATH.exists():
    print("Downloading fallback model...")
    gdown.download("https://drive.google.com/uc?id=1sHSBOzRgDfr0ZLgMBnU2-PVLpy_vCM3-", str(FALLBACK_MODEL_PATH), quiet=False)

print("MODEL PATH:", MODEL_PATH)
print("EXISTS:", MODEL_PATH.exists())

print("Loading model now...")

# ✅ Model fallback
if not MODEL_PATH.exists() and FALLBACK_MODEL_PATH.exists():
    MODEL_PATH = FALLBACK_MODEL_PATH

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

if not LABEL_MAP_PATH.exists():
    raise FileNotFoundError(f"Label map not found: {LABEL_MAP_PATH}")

# ✅ Load label map
with open(LABEL_MAP_PATH, 'r') as f:
    label_map = json.load(f)

# ✅ SAFE MODEL LOAD
try:
    print("MODEL PATH:", MODEL_PATH)
    print("EXISTS:", MODEL_PATH.exists())
    model = load_model(str(MODEL_PATH), compile=False)
    print("Model loaded ✅")
except Exception as e:
    print("Model load error ❌:", e)
    model = None

species_idx_to_name = {int(k): v for k, v in label_map['idx2species'].items()}
health_idx_to_name = {int(k): v for k, v in label_map['idx2health'].items()}


@app.route("/image/upload", methods=["POST"])
def image_upload():
    try:
        # ✅ ADD SAFETY CHECK
        if model is None:
            return jsonify({"error": "Model not loaded"}), 500

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        file_extension = os.path.splitext(file.filename)[1]
        unique_name = uuid.uuid4().hex
        hash_filename = sha512(unique_name.encode()).hexdigest() + file_extension

        images_dir = BASE_DIR / "images"
        images_dir.mkdir(exist_ok=True)

        file_path = images_dir / hash_filename
        file.save(str(file_path))

        img = cv2.imread(str(file_path))
        if img is None:
            return jsonify({"error": "Invalid image"}), 400

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (256, 256))
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)

        preds = model.predict(img)

        if isinstance(preds, dict):
            species_pred = preds["species"]
            health_pred = preds["health"]
        else:
            species_pred, health_pred = preds

        species_idx = int(np.argmax(species_pred, axis=1)[0])
        health_idx = int(np.argmax(health_pred, axis=1)[0])

        return jsonify({
            "species": species_idx_to_name.get(species_idx, "unknown"),
            "health": health_idx_to_name.get(health_idx, "unknown")
        })

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
