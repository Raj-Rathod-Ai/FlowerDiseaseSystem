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

# ✅ TensorFlow (needed for .keras)
from tensorflow.keras.models import load_model

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models/multitask_finetuned.keras"
LABEL_MAP_PATH = BASE_DIR / "manifests/label_map.json"

model = None

# ─────────────────────────────────────────────
# LOAD LABEL MAP
# ─────────────────────────────────────────────
try:
    with open(LABEL_MAP_PATH, "r") as f:
        label_map = json.load(f)
except Exception as e:
    print("❌ Label map error:", e)
    label_map = {"idx2species": {}, "idx2health": {}}

species_map = {int(k): v for k, v in label_map.get("idx2species", {}).items()}
health_map = {int(k): v for k, v in label_map.get("idx2health", {}).items()}

# ─────────────────────────────────────────────
# LOAD MODEL
# ─────────────────────────────────────────────
def load_model_once():
    global model

    if model is not None:
        return True

    if not MODEL_PATH.exists():
        print("❌ Model file not found:", MODEL_PATH)
        return False

    try:
        print("🔄 Loading model...")
        model = load_model(str(MODEL_PATH), compile=False)
        print("✅ Model loaded")
        return True
    except Exception as e:
        print("❌ Model load error:", e)
        return False


# ─────────────────────────────────────────────
# HOME ROUTE
# ─────────────────────────────────────────────
@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "FloraScan Backend Running ✅"
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
        print("✅ File received:", file.filename, flush=True)

        # Save image
        filename = sha512(uuid.uuid4().hex.encode()).hexdigest() + ".jpg"
        filepath = BASE_DIR / filename
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

        print("✅ Preprocessing done", flush=True)

        # Predict
        preds = model.predict(img)

        # Handle multi-output model
        if isinstance(preds, dict):
            species_pred = preds.get("species")
            health_pred = preds.get("health")
        else:
            species_pred, health_pred = preds

        species_idx = int(np.argmax(species_pred))
        health_idx = int(np.argmax(health_pred))

        print("✅ Prediction done", flush=True)

        return jsonify({
            "species": species_map.get(species_idx, "unknown"),
            "health": health_map.get(health_idx, "unknown")
        })

    except Exception as e:
        print("🔥 ERROR:", e, flush=True)
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# START SERVER
# ─────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
