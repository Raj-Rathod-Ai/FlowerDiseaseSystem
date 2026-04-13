import os

# MUST be set before any keras import — use TensorFlow backend
# The model was saved with Keras 3.3.3 + TF backend; JAX backend causes get_tensor() errors
os.environ["KERAS_BACKEND"] = "tensorflow"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
from hashlib import sha512
import uuid
import cv2
import numpy as np
import json

app = Flask(__name__)
CORS(app)

BASE_DIR       = Path(__file__).resolve().parent
LABEL_MAP_PATH = BASE_DIR / "manifests" / "label_map.json"
MODEL_DIR      = BASE_DIR / "models"
MODEL_PATH     = MODEL_DIR / "multitask_finetuned.keras"

HF_REPO_ID    = "rathodraj/flower-disease-models"
HF_MODEL_FILE = "multitask_finetuned.keras"

model = None


def download_model():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    if MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 10_000_000:
        print(f"[MODEL] Already cached ({MODEL_PATH.stat().st_size / 1e6:.1f} MB)", flush=True)
        return True
    print("[MODEL] Downloading from HuggingFace...", flush=True)
    try:
        from huggingface_hub import hf_hub_download
        hf_hub_download(
            repo_id=HF_REPO_ID,
            filename=HF_MODEL_FILE,
            local_dir=str(MODEL_DIR),
            local_dir_use_symlinks=False,
        )
        size_mb = MODEL_PATH.stat().st_size / 1e6
        print(f"[MODEL] Downloaded ({size_mb:.1f} MB)", flush=True)
        return size_mb > 10
    except Exception as e:
        print(f"[MODEL] Download failed: {e}", flush=True)
        return False


def ensure_model():
    global model
    if model is not None:
        return True
    if not download_model():
        return False
    print(f"[MODEL] Loading...", flush=True)
    try:
        import keras
        print(f"[MODEL] Keras {keras.__version__} | Backend: {keras.backend.backend()}", flush=True)
        model = keras.models.load_model(str(MODEL_PATH), compile=False)
        print("[MODEL] Loaded successfully ✅", flush=True)
        return True
    except Exception as e:
        print(f"[MODEL] Load failed ❌: {e}", flush=True)
        return False


# Load label map
try:
    with open(LABEL_MAP_PATH, "r") as f:
        label_map = json.load(f)
    print("[LABEL] Label map loaded ✅", flush=True)
except Exception as e:
    print(f"[LABEL] Error: {e}", flush=True)
    label_map = {"idx2species": {}, "idx2health": {}}

species_idx_to_name = {int(k): v for k, v in label_map.get("idx2species", {}).items()}
health_idx_to_name  = {int(k): v for k, v in label_map.get("idx2health",  {}).items()}

# Pre-load at startup
print("[STARTUP] Pre-loading model...", flush=True)
ensure_model()


@app.route("/")
def home():
    return "FloraScan Backend Running ✅"


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "model_loaded":    model is not None,
        "species_classes": list(species_idx_to_name.values()),
        "health_classes":  list(health_idx_to_name.values()),
    })


@app.route("/image/upload", methods=["POST"])
def image_upload():
    try:
        if not ensure_model():
            return jsonify({"error": "Model not loaded. Check server logs."}), 500

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded. Use key 'file'."}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp", ".bmp"]:
            return jsonify({"error": f"Unsupported file type: {ext}. Use jpg/png/webp."}), 400

        filename  = sha512(uuid.uuid4().hex.encode()).hexdigest() + ext
        images_dir = BASE_DIR / "images"
        images_dir.mkdir(exist_ok=True)
        file_path = images_dir / filename
        file.save(str(file_path))

        img = cv2.imread(str(file_path))
        if img is None:
            return jsonify({"error": "Could not decode image."}), 400

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (256, 256))
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)

        preds = model.predict(img, verbose=0)

        if isinstance(preds, dict):
            species_pred = np.array(preds.get("species"))
            health_pred  = np.array(preds.get("health"))
        elif isinstance(preds, (list, tuple)) and len(preds) == 2:
            species_pred = np.array(preds[0])
            health_pred  = np.array(preds[1])
        else:
            return jsonify({"error": "Unexpected model output format"}), 500

        species_idx = int(np.argmax(species_pred, axis=1)[0])
        health_idx  = int(np.argmax(health_pred,  axis=1)[0])

        # Build all class probabilities
        all_species = {
            species_idx_to_name.get(i, f"class_{i}"): round(float(species_pred[0][i]) * 100, 1)
            for i in range(len(species_pred[0]))
        }
        all_health = {
            health_idx_to_name.get(i, f"class_{i}"): round(float(health_pred[0][i]) * 100, 1)
            for i in range(len(health_pred[0]))
        }

        return jsonify({
            "species":              species_idx_to_name.get(species_idx, f"unknown"),
            "species_confidence":   round(float(np.max(species_pred)) * 100, 1),
            "species_all":          all_species,
            "health":               health_idx_to_name.get(health_idx, f"unknown"),
            "health_confidence":    round(float(np.max(health_pred))  * 100, 1),
            "health_all":           all_health,
        })

    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
