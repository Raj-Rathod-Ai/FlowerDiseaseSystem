from flask import Flask, request, jsonify
from pathlib import Path
import os
from hashlib import sha512
import uuid
import cv2
import numpy as np
import json
from flask_cors import CORS
from huggingface_hub import hf_hub_download
import gdown

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "multitask_finetuned.keras"
LABEL_MAP_PATH = BASE_DIR / "manifests" / "label_map.json"

HF_REPO_ID = "rathodraj/flower-disease-models"
HF_MODEL_FILENAME = "multitask_finetuned.keras"

GDRIVE_URL = "https://drive.google.com/uc?export=download&id=1ClzyqzqoZBlp7dcNlnX_xBQvUFtt29QL"

model = None


# 🔧 SAFE MODEL LOAD
def safe_load_model(path):
    from tensorflow.keras.models import load_model
    try:
        print("[MODEL] Trying normal load...", flush=True)
        return load_model(path, compile=False)
    except Exception as e:
        print("[MODEL] Normal load failed:", e, flush=True)

    try:
        print("[MODEL] Trying compile=True...", flush=True)
        return load_model(path)
    except Exception as e:
        print("[MODEL] Compile load failed:", e, flush=True)

    return None


# 🔁 DOWNLOAD MODEL (HF → GDRIVE fallback)
def download_model():
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Remove corrupted file
    if MODEL_PATH.exists():
        size_mb = MODEL_PATH.stat().st_size / 1e6
        if size_mb < 10:  # corrupted or HTML
            print("[MODEL] Removing corrupted file...", flush=True)
            os.remove(MODEL_PATH)

    # Try HuggingFace first
    if not MODEL_PATH.exists():
        print("[MODEL] Trying HuggingFace download...", flush=True)
        try:
            hf_hub_download(
                repo_id=HF_REPO_ID,
                filename=HF_MODEL_FILENAME,
                local_dir=str(MODEL_PATH.parent),
                local_dir_use_symlinks=False
            )
        except Exception as e:
            print("[MODEL] HF download failed:", e, flush=True)

    # If still not exists → use Google Drive
    if not MODEL_PATH.exists():
        print("[MODEL] Trying Google Drive download...", flush=True)
        try:
            gdown.download(GDRIVE_URL, str(MODEL_PATH), quiet=False)
        except Exception as e:
            print("[MODEL] GDrive download failed:", e, flush=True)

    # Final check
    if MODEL_PATH.exists():
        size_mb = MODEL_PATH.stat().st_size / 1e6
        print(f"[MODEL] File size: {size_mb:.1f} MB", flush=True)

        if size_mb < 10:
            print("[MODEL] File still corrupted ❌", flush=True)
            return False

        return True

    return False


# 🔁 ENSURE MODEL
def ensure_model():
    global model

    if model is not None:
        return True

    print("[MODEL] ensure_model() called", flush=True)

    if not download_model():
        print("[MODEL] Download failed ❌", flush=True)
        return False

    print("[MODEL] Loading model...", flush=True)
    loaded = safe_load_model(str(MODEL_PATH))

    if loaded is None:
        print("[MODEL] Load failed ❌", flush=True)
        return False

    model = loaded
    print("[MODEL] Model loaded ✅", flush=True)
    return True


# 📄 LOAD LABEL MAP
try:
    with open(LABEL_MAP_PATH, "r") as f:
        label_map = json.load(f)
    print("[LABEL] Loaded ✅", flush=True)
except Exception as e:
    print("[LABEL] Error:", e, flush=True)
    label_map = {"idx2species": {}, "idx2health": {}}

species_idx_to_name = {int(k): v for k, v in label_map.get("idx2species", {}).items()}
health_idx_to_name = {int(k): v for k, v in label_map.get("idx2health", {}).items()}


# 🚀 PRELOAD (optional)
print("[STARTUP] Preloading model...", flush=True)
ensure_model()


@app.route("/")
def home():
    return "Backend Running ✅"


@app.route("/health")
def health():
    return jsonify({"model_loaded": model is not None})


@app.route("/image/upload", methods=["POST"])
def image_upload():
    try:
        if not ensure_model():
            return jsonify({"error": "Model not loaded"}), 500

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        ext = os.path.splitext(file.filename)[1]
        filename = sha512(uuid.uuid4().hex.encode()).hexdigest() + ext

        images_dir = BASE_DIR / "images"
        images_dir.mkdir(exist_ok=True)

        file_path = images_dir / filename
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
        print("[ERROR]", e, flush=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
