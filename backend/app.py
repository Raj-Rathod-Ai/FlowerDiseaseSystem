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

# ✅ Allow all origins (important for deployment)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent

# ✅ Correct paths (ensure these folders exist in GitHub)
MODEL_PATH = BASE_DIR.parent / "models" / "multitask_finetuned.keras"
FALLBACK_MODEL_PATH = BASE_DIR.parent / "models" / "multitask_best.keras"
LABEL_MAP_PATH = BASE_DIR.parent / "manifests" / "label_map.json"

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

# ✅ Load model (important: compile=False for speed & fewer errors)
model = load_model(str(MODEL_PATH), compile=False)

species_idx_to_name = {int(k): v for k, v in label_map['idx2species'].items()}
health_idx_to_name = {int(k): v for k, v in label_map['idx2health'].items()}


@app.route("/")
def home():
    return "Backend Running ✅"


@app.route("/image/upload", methods=["POST"])
def image_upload():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        # ✅ Secure unique filename
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

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (256, 256))
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)

        # ✅ Prediction
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
    app.run(host="0.0.0.0", port=10000)@app.route("/")
def home():
    return "Hello"

@app.route("/image/upload", methods=["GET", "POST"])
def image_upload():
    if request.method == "POST":
        try:
            if "file" not in request.files:
                return jsonify({"error": "No file uploaded"}), 400

            file = request.files["file"]
            file_extension = os.path.splitext(file.filename)[1]
            file_name = str(file.filename) + uuid.uuid4().hex
            file_name = file_name.encode("utf-8")
            hash_filename = sha512(file_name).hexdigest() + str(file_extension)
            images_dir = BASE_DIR / "images"
            images_dir.mkdir(exist_ok=True)
            file_path = images_dir / hash_filename
            file.save(str(file_path))

            img_test = cv2.imread(str(file_path))
            if img_test is None:
                return jsonify({"error": "Unable to read uploaded image"}), 400

            img_rgb = cv2.cvtColor(img_test, cv2.COLOR_BGR2RGB)
            img_resize = cv2.resize(img_rgb, (256, 256))
            img_scaled = img_resize.astype(np.float32) / 255.0
            img_reshaped = np.expand_dims(img_scaled, axis=0)

            preds = model.predict(img_reshaped)
            if isinstance(preds, dict):
                species_pred = preds["species"]
                health_pred = preds["health"]
            else:
                species_pred, health_pred = preds

            species_idx = int(np.argmax(species_pred, axis=1)[0])
            health_idx = int(np.argmax(health_pred, axis=1)[0])
            species_name = species_idx_to_name.get(species_idx, "unknown")
            health_name = health_idx_to_name.get(health_idx, "unknown")

            return jsonify({"species": species_name, "health": health_name})
        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"message": "Running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

