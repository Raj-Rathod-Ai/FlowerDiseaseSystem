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

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "multitask_finetuned.keras"
LABEL_MAP_PATH = BASE_DIR / "manifests" / "label_map.json"

HF_REPO_ID = "rathodraj/flower-disease-models"
HF_MODEL_FILENAME = "multitask_finetuned.keras"

model = None

# Keys to strip from layer configs that were added in newer Keras
# but don't exist in the installed Keras 3.x version
LEGACY_KEYS = {
    "keras.layers.BatchNormalization": ["renorm", "renorm_clipping", "renorm_momentum"],
    "keras.layers.Dense": ["quantization_config"],
}


def patch_keras_layers():
    """
    Monkey-patch Keras layer __init__ methods to silently drop
    config keys that don't exist in the installed Keras version.
    """
    import keras

    patches = [
        (keras.layers.BatchNormalization, ["renorm", "renorm_clipping", "renorm_momentum"]),
        (keras.layers.Dense, ["quantization_config"]),
    ]

    originals = {}
    for layer_cls, keys_to_strip in patches:
        orig = layer_cls.__init__

        def make_patched(original, strip_keys):
            def patched_init(self, **kwargs):
                for k in strip_keys:
                    kwargs.pop(k, None)
                original(self, **kwargs)
            return patched_init

        originals[layer_cls] = orig
        layer_cls.__init__ = make_patched(orig, keys_to_strip)

    return originals


def restore_keras_layers(originals):
    for layer_cls, orig in originals.items():
        layer_cls.__init__ = orig


def load_model_with_patch(path):
    import keras
    originals = patch_keras_layers()
    try:
        print("[MODEL] Loading model with compat patches...", flush=True)
        loaded = keras.models.load_model(path, compile=False)
        print("[MODEL] Model loaded successfully ✅", flush=True)
        return loaded
    except Exception as e:
        print(f"[MODEL] Load failed ❌: {e}", flush=True)
        return None
    finally:
        restore_keras_layers(originals)


def ensure_model():
    global model

    if model is not None:
        return True

    print("[MODEL] ensure_model() called", flush=True)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not MODEL_PATH.exists():
        print("[MODEL] Downloading from Hugging Face...", flush=True)
        try:
            hf_hub_download(
                repo_id=HF_REPO_ID,
                filename=HF_MODEL_FILENAME,
                local_dir=str(MODEL_PATH.parent),
                local_dir_use_symlinks=False
            )
        except Exception as e:
            print(f"[MODEL] Download failed ❌: {e}", flush=True)
            return False

    if not MODEL_PATH.exists():
        print("[MODEL] File missing after download ❌", flush=True)
        return False

    size_mb = MODEL_PATH.stat().st_size / 1e6
    print(f"[MODEL] File size: {size_mb:.1f} MB", flush=True)

    loaded = load_model_with_patch(str(MODEL_PATH))
    if loaded is None:
        return False

    model = loaded
    return True


# Load label map
try:
    with open(LABEL_MAP_PATH, "r") as f:
        label_map = json.load(f)
    print("[LABEL] Label map loaded ✅", flush=True)
except Exception as e:
    print(f"[LABEL] Error ❌: {e}", flush=True)
    label_map = {"idx2species": {}, "idx2health": {}}

species_idx_to_name = {int(k): v for k, v in label_map.get("idx2species", {}).items()}
health_idx_to_name = {int(k): v for k, v in label_map.get("idx2health", {}).items()}

# Pre-load model at startup
print("[STARTUP] Pre-loading model...", flush=True)
ensure_model()


@app.route("/")
def home():
    return "Backend Running ✅"


@app.route("/health")
def health():
    return jsonify({"status": "ok", "model_loaded": model is not None})


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

        ext = os.path.splitext(file.filename)[1].lower()
        filename = sha512(uuid.uuid4().hex.encode()).hexdigest() + ext

        images_dir = BASE_DIR / "images"
        images_dir.mkdir(exist_ok=True)

        file_path = images_dir / filename
        file.save(str(file_path))

        img = cv2.imread(str(file_path))
        if img is None:
            return jsonify({"error": "Could not read image file"}), 400

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
        print(f"[PREDICT] Error: {e}", flush=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
