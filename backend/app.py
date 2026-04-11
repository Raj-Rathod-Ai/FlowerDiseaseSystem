import os

# ✅ MUST be set before ANY keras/jax import
os.environ["KERAS_BACKEND"] = "jax"

from flask import Flask, request, jsonify
from pathlib import Path
from hashlib import sha512
import uuid
import cv2
import numpy as np
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR       = Path(__file__).resolve().parent
LABEL_MAP_PATH = BASE_DIR / "manifests" / "label_map.json"
MODEL_DIR      = BASE_DIR / "models"
MODEL_PATH     = MODEL_DIR / "multitask_finetuned.keras"

HF_REPO_ID       = "rathodraj/flower-disease-models"
HF_MODEL_FILE    = "multitask_finetuned.keras"   # filename inside the HF repo

model = None


def download_model_from_hf():
    """Download the .keras file from HuggingFace to local disk using huggingface_hub."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    if MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 10_000_000:
        print(f"[MODEL] Already cached locally ({MODEL_PATH.stat().st_size / 1e6:.1f} MB)", flush=True)
        return True

    print(f"[MODEL] Downloading from HuggingFace repo: {HF_REPO_ID} ...", flush=True)
    try:
        from huggingface_hub import hf_hub_download
        local_path = hf_hub_download(
            repo_id=HF_REPO_ID,
            filename=HF_MODEL_FILE,
            local_dir=str(MODEL_DIR),
            local_dir_use_symlinks=False,
        )
        size_mb = Path(local_path).stat().st_size / 1e6
        print(f"[MODEL] Downloaded to {local_path} ({size_mb:.1f} MB)", flush=True)
        return size_mb > 10
    except Exception as e:
        print(f"[MODEL] HuggingFace download failed: {e}", flush=True)
        return False


def ensure_model():
    global model

    if model is not None:
        return True

    if not download_model_from_hf():
        print("[MODEL] Could not download model ❌", flush=True)
        return False

    print(f"[MODEL] Loading from local path: {MODEL_PATH}", flush=True)
    try:
        import keras
        print(f"[MODEL] Keras version: {keras.__version__}", flush=True)
        # ✅ Load from local file — no gfile / tensorflow needed
        model = keras.models.load_model(str(MODEL_PATH), compile=False)
        print("[MODEL] Model loaded ✅", flush=True)
        return True
    except Exception as e:
        print(f"[MODEL] Load failed ❌: {e}", flush=True)
        return False


# 📄 Load label map
try:
    with open(LABEL_MAP_PATH, "r") as f:
        label_map = json.load(f)
    print("[LABEL] Loaded ✅", flush=True)
except Exception as e:
    print(f"[LABEL] Error: {e}", flush=True)
    label_map = {"idx2species": {}, "idx2health": {}}

species_idx_to_name = {int(k): v for k, v in label_map.get("idx2species", {}).items()}
health_idx_to_name  = {int(k): v for k, v in label_map.get("idx2health",  {}).items()}

# 🚀 Preload at startup
print("[STARTUP] Preloading model...", flush=True)
ensure_model()


@app.route("/")
def home():
    return "Backend Running ✅"


@app.route("/health")
def health():
    return jsonify({
        "model_loaded":    model is not None,
        "species_classes": len(species_idx_to_name),
        "health_classes":  len(health_idx_to_name),
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
            return jsonify({"error": f"Unsupported file type: {ext}"}), 400

        filename = sha512(uuid.uuid4().hex.encode()).hexdigest() + ext
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

        preds = model.predict(img)

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

        return jsonify({
            "species":            species_idx_to_name.get(species_idx, f"unknown (idx={species_idx})"),
            "species_confidence": round(float(np.max(species_pred)) * 100, 2),
            "health":             health_idx_to_name.get(health_idx,  f"unknown (idx={health_idx})"),
            "health_confidence":  round(float(np.max(health_pred))  * 100, 2),
        })

    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
