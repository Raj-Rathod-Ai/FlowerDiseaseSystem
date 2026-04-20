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
FALLBACK_MODEL_PATH = MODEL_DIR / "fallback.keras"

LABEL_MAP_PATH = BASE_DIR / "manifests/label_map.json"

model = None

# ✅ YOUR DRIVE FILE IDs
MAIN_ID = "1ClzyqzqoZBlp7dcNlnX_xBQvUFtt29QL"
FALLBACK_ID = "1sHSBOzRgDfr0ZLgMBnU2-PVLpy_vCM3-"

# ─────────────────────────────
# LOAD LABEL MAP
# ─────────────────────────────
try:
    with open(LABEL_MAP_PATH, "r") as f:
        label_map = json.load(f)
except:
    label_map = {"idx2species": {}, "idx2health": {}}

species_map = {int(k): v for k, v in label_map.get("idx2species", {}).items()}
health_map = {int(k): v for k, v in label_map.get("idx2health", {}).items()}

# ─────────────────────────────
# LOAD MODEL
# ─────────────────────────────
def load_model_once():
    global model

    if model is not None:
        return True

    # 🔽 Download main model
    if not MODEL_PATH.exists():
        print("⬇️ Downloading main model...")
        gdown.download(f"https://drive.google.com/uc?id={MAIN_ID}", str(MODEL_PATH), quiet=False)

    # 🔽 Download fallback
    if not FALLBACK_MODEL_PATH.exists():
        print("⬇️ Downloading fallback model...")
        gdown.download(f"https://drive.google.com/uc?id={FALLBACK_ID}", str(FALLBACK_MODEL_PATH), quiet=False)

    # 🔄 Try loading main model
    try:
        print("🔄 Loading main model...")
        model = load_model(str(MODEL_PATH), compile=False)
        print("✅ Main model loaded")
        return True
    except Exception as e:
        print("❌ Main model failed:", e)

    # 🔄 Try fallback model
    try:
        print("🔄 Loading fallback model...")
        model = load_model(str(FALLBACK_MODEL_PATH), compile=False)
        print("✅ Fallback model loaded")
        return True
    except Exception as e:
        print("❌ Fallback model failed:", e)

    return False


# ─────────────────────────────
# ROUTES
# ─────────────────────────────
@app.route("/")
def home():
    return {"status": "ok", "message": "Backend running"}

@app.route("/image/upload", methods=["POST"])
def upload():
    try:
        if not load_model_once():
            return {"error": "Model not loaded"}, 500

        if "file" not in request.files:
            return {"error": "No file"}, 400

        file = request.files["file"]

        # Save image
        name = sha512(uuid.uuid4().hex.encode()).hexdigest() + ".jpg"
        path = BASE_DIR / name
        file.save(str(path))

        img = cv2.imread(str(path))
        if img is None:
            return {"error": "Invalid image"}, 400

        # preprocess
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (256, 256))
        img = img / 255.0
        img = np.expand_dims(img, axis=0)

        preds = model.predict(img)

        if isinstance(preds, dict):
            s = preds["species"]
            h = preds["health"]
        else:
            s, h = preds

        return {
            "species": species_map.get(int(np.argmax(s)), "unknown"),
            "health": health_map.get(int(np.argmax(h)), "unknown")
        }

    except Exception as e:
        print("ERROR:", e)
        return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
