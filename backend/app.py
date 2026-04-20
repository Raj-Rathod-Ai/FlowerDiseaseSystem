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

from tensorflow.keras.models import load_model
import gdown

app = Flask(__name__)
CORS(app)

# ─────────────────────────────
# PATHS
# ─────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

MODEL_PATH = MODEL_DIR / "model.keras"
FALLBACK_PATH = MODEL_DIR / "fallback.keras"
LABEL_MAP_PATH = BASE_DIR / "manifests/label_map.json"

model = None

# ✅ YOUR GOOGLE DRIVE FILE IDs
MAIN_ID = "1ClzyqzqoZBlp7dcNlnX_xBQvUFtt29QL"
FALLBACK_ID = "1sHSBOzRgDfr0ZLgMBnU2-PVLpy_vCM3-"

# ─────────────────────────────
# LABEL MAP
# ─────────────────────────────
try:
    with open(LABEL_MAP_PATH, "r") as f:
        label_map = json.load(f)
    print("✅ Label map loaded")
except Exception as e:
    print("❌ Label map error:", e)
    label_map = {"idx2species": {}, "idx2health": {}}

species_map = {int(k): v for k, v in label_map.get("idx2species", {}).items()}
health_map = {int(k): v for k, v in label_map.get("idx2health", {}).items()}

# ─────────────────────────────
# MODEL LOADER
# ─────────────────────────────
def load_model_once():
    global model

    if model is not None:
        return True

    try:
        # 🔽 Download main model
        if not MODEL_PATH.exists():
            print("⬇️ Downloading main model...")
            gdown.download(
                f"https://drive.google.com/uc?id={MAIN_ID}",
                str(MODEL_PATH),
                quiet=False
            )

        # 🔽 Download fallback model
        if not FALLBACK_PATH.exists():
            print("⬇️ Downloading fallback model...")
            gdown.download(
                f"https://drive.google.com/uc?id={FALLBACK_ID}",
                str(FALLBACK_PATH),
                quiet=False
            )

        # 🔄 Try loading main
        try:
            print("🔄 Loading main model...")
            model = load_model(str(MODEL_PATH), compile=False)
            print("✅ Main model loaded")
            return True
        except Exception as e:
            print("❌ Main model failed:", e)

        # 🔄 Try fallback
        try:
            print("🔄 Loading fallback model...")
            model = load_model(str(FALLBACK_PATH), compile=False)
            print("✅ Fallback model loaded")
            return True
        except Exception as e:
            print("❌ Fallback model failed:", e)

        return False

    except Exception as e:
        print("❌ Model download/load error:", e)
        return False


# ─────────────────────────────
# ROUTES
# ─────────────────────────────
@app.route("/")
def home():
    return {
        "status": "ok",
        "message": "FloraScan Backend Running ✅"
    }


@app.route("/image/upload", methods=["POST"])
def upload():
    try:
        print("🚀 Request received", flush=True)

        if not load_model_once():
            return {"error": "Model not loaded"}, 500

        if "file" not in request.files:
            return {"error": "No file uploaded"}, 400

        file = request.files["file"]

        # Save image
        filename = sha512(uuid.uuid4().hex.encode()).hexdigest() + ".jpg"
        filepath = BASE_DIR / filename
        file.save(str(filepath))

        img = cv2.imread(str(filepath))
        if img is None:
            return {"error": "Invalid image"}, 400

        # Preprocess
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (256, 256))
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)

        print("🧠 Predicting...", flush=True)

        preds = model.predict(img)

        if isinstance(preds, dict):
            species_pred = preds.get("species")
            health_pred = preds.get("health")
        else:
            species_pred, health_pred = preds

        species_idx = int(np.argmax(species_pred))
        health_idx = int(np.argmax(health_pred))

        print("✅ Prediction done", flush=True)

        return {
            "species": species_map.get(species_idx, "unknown"),
            "health": health_map.get(health_idx, "unknown")
        }

    except Exception as e:
        print("🔥 ERROR:", e, flush=True)
        return {"error": str(e)}, 500


# ─────────────────────────────
# START SERVER
# ─────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
