import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import numpy as np
import cv2
import json
import uuid
from hashlib import sha512

import gdown
from tensorflow.keras.models import load_model

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent

MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

MODEL_PATH = MODEL_DIR / "model.keras"
LABEL_MAP_PATH = BASE_DIR / "manifests/label_map.json"

MODEL_URL = "https://drive.google.com/uc?id=1ClzyqzqoZBlp7dcNlnX_xBQvUFtt29QL"

model = None

# ─────────────────────────────────────────────
# LOAD LABEL MAP
# ─────────────────────────────────────────────
try:
    with open(LABEL_MAP_PATH, "r") as f:
        label_map = json.load(f)
    print("✅ Label map loaded")
except Exception as e:
    print("❌ Label map error:", e)
    label_map = {"idx2species": {}, "idx2health": {}}

species_map = {int(k): v for k, v in label_map.get("idx2species", {}).items()}
health_map = {int(k): v for k, v in label_map.get("idx2health", {}).items()}

# ─────────────────────────────────────────────
# LOAD MODEL (ONLY ONCE)
# ─────────────────────────────────────────────
def load_model_once():
    global model

    if model is not None:
        return True

    try:
        # Download only if not exists
        if not MODEL_PATH.exists():
            print("⬇️ Downloading model...")
            gdown.download(MODEL_URL, str(MODEL_PATH), quiet=False)

        print("🔄 Loading model...")
        model = load_model(str(MODEL_PATH), compile=False)

        print("✅ Model loaded successfully")
        return True

    except Exception as e:
        print("❌ Model load error:", e)
        return False


# ─────────────────────────────────────────────
# PRELOAD MODEL (IMPORTANT)
# ─────────────────────────────────────────────
print("🚀 Preloading model at startup...")
load_model_once()

# ─────────────────────────────────────────────
# HOME
# ─────────────────────────────────────────────
@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "FloraScan Backend Running ✅",
        "model_loaded": model is not None
    })


# ─────────────────────────────────────────────
# IMAGE PREDICTION
# ─────────────────────────────────────────────
@app.route("/image/upload", methods=["POST"])
def upload():
    try:
        print("🚀 Request received", flush=True)

        if not load_model_once():
            return jsonify({"error": "Model not loaded"}), 500

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        print("📂 File:", file.filename)

        # Save image
        images_dir = BASE_DIR / "images"
        images_dir.mkdir(exist_ok=True)

        filename = sha512(uuid.uuid4().hex.encode()).hexdigest() + ".jpg"
        filepath = images_dir / filename
        file.save(str(filepath))

        # Read image
        img = cv2.imread(str(filepath))
        if img is None:
            return jsonify({"error": "Invalid image"}), 400

        # Preprocess
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (256, 256))
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)

        print("⚡ Running prediction...")

        preds = model.predict(img)

        # Multi-output handling
        if isinstance(preds, dict):
            species_pred = preds.get("species")
            health_pred = preds.get("health")
        else:
            species_pred, health_pred = preds

        species_idx = int(np.argmax(species_pred))
        health_idx = int(np.argmax(health_pred))

        result = {
            "species": species_map.get(species_idx, "unknown"),
            "health": health_map.get(health_idx, "unknown")
        }

        print("✅ Prediction:", result)

        return jsonify(result)

    except Exception as e:
        print("🔥 ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# START SERVER
# ─────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
