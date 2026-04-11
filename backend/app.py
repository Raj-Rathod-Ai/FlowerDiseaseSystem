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

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "multitask_finetuned.keras"
LABEL_MAP_PATH = BASE_DIR / "manifests" / "label_map.json"

# Google Drive file ID for multitask_finetuned.keras
# Get this from your sharing link: drive.google.com/file/d/<FILE_ID>/view
GDRIVE_FILE_ID = "1ClzyqzqoZBlp7dcNlnX_xBQvUFtt29QL"

model = None


def safe_load_model(path):
    """Try loading model with compile=False first, then fallback."""
    try:
        print("Loading model (compile=False)...")
        return load_model(path, compile=False)
    except Exception as e:
        print(f"Load with compile=False failed: {e}")

    try:
        print("Loading model (compile=True)...")
        return load_model(path)
    except Exception as e:
        print(f"Load with compile=True failed: {e}")

    return None


def ensure_model():
    """Download model from Google Drive if missing, then load it."""
    global model

    if model is not None:
        return True

    # Create models directory if it doesn't exist
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Download model if file is missing
    if not MODEL_PATH.exists():
        print("Model file not found. Downloading from Google Drive...")
        try:
            # Use id= parameter — avoids virus-scan redirect issues with large files
            gdown.download(
                id=GDRIVE_FILE_ID,
                output=str(MODEL_PATH),
                quiet=False,
                fuzzy=True
            )
        except Exception as e:
            print(f"Download failed: {e}")
            return False

    if not MODEL_PATH.exists():
        print("Model file still missing after download attempt.")
        return False

    print(f"Model file size: {MODEL_PATH.stat().st_size / 1e6:.1f} MB")

    loaded = safe_load_model(str(MODEL_PATH))
    if loaded is None:
        print("Model failed to load.")
        return False

    model = loaded
    print("Model loaded successfully.")
    return True


# Load label map at startup
try:
    with open(LABEL_MAP_PATH, "r") as f:
        label_map = json.load(f)
    print("Label map loaded.")
except Exception as e:
    print(f"Label map load error: {e}")
    label_map = {"idx2species": {}, "idx2health": {}}

species_idx_to_name = {int(k): v for k, v in label_map.get("idx2species", {}).items()}
health_idx_to_name = {int(k): v for k, v in label_map.get("idx2health", {}).items()}


@app.route("/")
def home():
    return "Backend Running ✅"


@app.route("/health")
def health():
    """Health check endpoint — also warms up the model."""
    ready = ensure_model()
    return jsonify({"status": "ok", "model_loaded": ready})


@app.route("/image/upload", methods=["POST"])
def image_upload():
    try:
        if not ensure_model():
            return jsonify({"error": "Model not loaded. Check server logs."}), 500

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        # Save uploaded file
        ext = os.path.splitext(file.filename)[1].lower()
        filename = sha512(uuid.uuid4().hex.encode()).hexdigest() + ext

        images_dir = BASE_DIR / "images"
        images_dir.mkdir(exist_ok=True)

        file_path = images_dir / filename
        file.save(str(file_path))

        # Read and preprocess image
        img = cv2.imread(str(file_path))
        if img is None:
            return jsonify({"error": "Could not read image. Make sure it is a valid image file."}), 400

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (256, 256))
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)

        # Run prediction
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
        print(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
