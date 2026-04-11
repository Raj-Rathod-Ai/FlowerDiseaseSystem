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
import gdown

# Hide TensorFlow warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models/multitask_finetuned.keras"
LABEL_MAP_PATH = BASE_DIR / "manifests/label_map.json"

model = None  # global model


# ✅ SAFE LOAD FUNCTION
def safe_load_model(path):
    try:
        print("Trying normal load...")
        return load_model(path, compile=False)
    except Exception as e:
        print("Normal load failed ❌:", e)

    try:
        print("Trying compile=True...")
        return load_model(path)
    except Exception as e:
        print("Compile load failed ❌:", e)

    return None


# ✅ LOAD LABEL MAP
try:
    with open(LABEL_MAP_PATH, 'r') as f:
        label_map = json.load(f)
    print("Label map loaded ✅")
except Exception as e:
    print("Label map error ❌:", e)
    label_map = {"idx2species": {}, "idx2health": {}}

species_idx_to_name = {int(k): v for k, v in label_map.get('idx2species', {}).items()}
health_idx_to_name = {int(k): v for k, v in label_map.get('idx2health', {}).items()}


# ✅ ENSURE MODEL FUNCTION (MAIN FIX)
def ensure_model():
    global model

    if model is not None:
        return True

    print("Checking model...")

    MODEL_PATH.parent.mkdir(exist_ok=True)

    # Download model if not exists
    if not MODEL_PATH.exists():
        print("Downloading model...")
        try:
            gdown.download(
                "https://drive.google.com/uc?id=1ClzyqzqoZBlp7dcNlnX_xBQvUFtt29QL",
                str(MODEL_PATH),
                quiet=False
            )
        except Exception as e:
            print("Download error ❌:", e)
            return False

    print("Model exists:", MODEL_PATH.exists())

    if not MODEL_PATH.exists():
        return False

    # Load model safely
    print("Loading model...")
    loaded = safe_load_model(str(MODEL_PATH))

    if loaded is None:
        print("Model load failed ❌")
        return False

    model = loaded
    print("Model loaded ✅")
    return True


@app.route("/")
def home():
    return "Backend Running ✅"


@app.route("/image/upload", methods=["POST"])
def image_upload():
    try:
        # Ensure model loaded
        if not ensure_model():
            return jsonify({"error": "Model not loaded"}), 500

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        # Save file
        ext = os.path.splitext(file.filename)[1]
        filename = sha512(uuid.uuid4().hex.encode()).hexdigest() + ext

        images_dir = BASE_DIR / "images"
        images_dir.mkdir(exist_ok=True)

        file_path = images_dir / filename
        file.save(str(file_path))

        # Read image
        img = cv2.imread(str(file_path))
        if img is None:
            return jsonify({"error": "Invalid image"}), 400

        # Preprocess
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (256, 256))
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)

        # Predict
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
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


# Dynamic port for Railway / Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
