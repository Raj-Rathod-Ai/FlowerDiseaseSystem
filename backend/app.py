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

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent

# ✅ Paths
MODEL_PATH = BASE_DIR / "models/multitask_finetuned.keras"
LABEL_MAP_PATH = BASE_DIR / "manifests/label_map.json"

print("MODEL PATH:", MODEL_PATH)
print("MODEL EXISTS:", MODEL_PATH.exists())
print("LABEL MAP EXISTS:", LABEL_MAP_PATH.exists())

# ✅ Load label map
try:
    with open(LABEL_MAP_PATH, 'r') as f:
        label_map = json.load(f)
except Exception as e:
    print("Label map load error ❌:", e)
    label_map = None

# ✅ Load model safely
try:
    model = load_model(str(MODEL_PATH), compile=False)
    print("Model loaded successfully ✅")
except Exception as e:
    print("Model load error ❌:", e)
    model = None

# ✅ Prepare mappings
if label_map:
    species_idx_to_name = {int(k): v for k, v in label_map['idx2species'].items()}
    health_idx_to_name = {int(k): v for k, v in label_map['idx2health'].items()}
else:
    species_idx_to_name = {}
    health_idx_to_name = {}

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return "Backend Running ✅"

@app.route("/image/upload", methods=["POST"])
def image_upload():
    try:
        # ✅ Check model
        if model is None:
            return jsonify({"error": "Model not loaded"}), 500

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        # ✅ Unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_name = uuid.uuid4().hex
        hash_filename = sha512(unique_name.encode()).hexdigest() + file_extension

        images_dir = BASE_DIR / "images"
        images_dir.mkdir(exist_ok=True)

        file_path = images_dir / hash_filename
        file.save(str(file_path))

        # ✅ Read image
        img = cv2.imread(str(file_path))
        if img is None:
            return jsonify({"error": "Invalid image"}), 400

        # ✅ Preprocess
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (256, 256))
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)

        # ✅ Prediction
        preds = model.predict(img)

        if isinstance(preds, dict):
            species_pred = preds.get("species")
            health_pred = preds.get("health")
        else:
            species_pred, health_pred = preds

        species_idx = int(np.argmax(species_pred, axis=1)[0])
        health_idx = int(np.argmax(health_pred, axis=1)[0])

        return jsonify({
            "species": species_idx_to_name.get(species_idx, "unknown"),
            "health": health_idx_to_name.get(health_idx, "unknown")
        })

    except Exception as e:
        print("Prediction error ❌:", e)
        return jsonify({"error": str(e)}), 500


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
