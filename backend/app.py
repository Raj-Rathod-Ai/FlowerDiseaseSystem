import os

# ── Environment ─────────────────────────────────────────────────────────────
# Must be set before any keras import — use TensorFlow backend.
os.environ["KERAS_BACKEND"]       = "tensorflow"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# Limit TF inter/intra parallelism so the server doesn't over-subscribe CPUs,
# which would otherwise cause spiky latency on shared hosts (e.g. Render free).
os.environ.setdefault("TF_NUM_INTRAOP_THREADS", "2")
os.environ.setdefault("TF_NUM_INTEROP_THREADS", "2")

import json
import uuid
from hashlib import sha512
from pathlib import Path
from datetime import datetime
import sqlite3

import cv2
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS

app  = Flask(__name__)
app.config["CORS_HEADERS"] = "Content-Type"
CORS(app, resources={r"/*": {"origins": "*"}})

BASE_DIR        = Path(__file__).resolve().parent
LABEL_MAP_PATH  = BASE_DIR / "manifests" / "label_map.json"
MODEL_DIR       = BASE_DIR / "models"
MODEL_PATH      = MODEL_DIR / "multitask_finetuned.keras"\nTFLITE_PATH    = MODEL_DIR / "multitask_finetuned.tflite"

# ── Global model + fast-call handle ─────────────────────────────────────────
model       = None\n_predict_fn = None   # compiled tf.function for ~2-3x faster repeated calls\ninterpreter  = None  # TFLite interpreter for optimized inference

IMG_SIZE    = 256

# ImageNet-style normalisation (mean/std) for better confidence calibration.
_IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_IMAGENET_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)


# ── Model load + JIT compilation ─────────────────────────────────────────────

def ensure_model():\n    global model, _predict_fn, interpreter\n    if interpreter is not None:\n        return True\n    if model is not None:\n        return True

    # Try TFLite first\n    if TFLITE_PATH.exists():\n        try:\n            import tflite_runtime.interpreter as tflite\n            interpreter = tflite.Interpreter(model_path=str(TFLITE_PATH))\n            interpreter.allocate_tensors()\n            global interpreter\n            interpreter = interpreter\n            dummy = np.zeros((1, IMG_SIZE, IMG_SIZE, 3), dtype=np.float32)\n            input_index = interpreter.get_input_details()[0]['index']\n            interpreter.set_tensor(input_index, dummy)\n            interpreter.invoke()\n            print(\"[MODEL] TFLite loaded and warmed up ✅\", flush=True)\n            def _predict_tflite(x):\n                input_index = interpreter.get_input_details()[0]['index']\n                species_output = interpreter.get_output_details()[0]['index']\n                health_output = interpreter.get_output_details()[1]['index']\n                interpreter.set_tensor(input_index, x)\n                interpreter.invoke()\n                return [\n                    interpreter.get_tensor(species_output),\n                    interpreter.get_tensor(health_output)\n                ]\n            global _predict_fn\n            _predict_fn = _predict_tflite\n            return True\n        except Exception as e:\n            print(f\"[TFLITE] Failed: {e}, falling back to Keras\", flush=True)\n\n    print(\"[MODEL] Loading Keras model ...\", flush=True)\n    try:\n        import tensorflow as tf
        keras = tf.keras

        print(f"[MODEL] Keras {keras.__version__} | TF {tf.__version__} | backend: {keras.backend.backend()}", flush=True)
        model = keras.models.load_model(str(MODEL_PATH), compile=False)

        # Warm-up: one dummy forward pass so the first real request is fast.
        dummy = np.zeros((1, IMG_SIZE, IMG_SIZE, 3), dtype=np.float32)
        _ = model(dummy, training=False)
        print("[MODEL] Warm-up complete", flush=True)

        # tf.function wrapper — skips Python overhead on repeated calls (~2-3x faster).
        @tf.function(
            input_signature=[tf.TensorSpec(shape=(None, IMG_SIZE, IMG_SIZE, 3), dtype=tf.float32)],
            reduce_retracing=True,
        )
        def _fast_predict(x):
            return model(x, training=False)

        _predict_fn = _fast_predict
        _ = _predict_fn(dummy)   # trace + compile now, not on first request
        print("[MODEL] tf.function compiled and ready ✅", flush=True)
        return True

    except Exception as e:
        print(f"[MODEL] Load failed: {e}", flush=True)
        import traceback; traceback.print_exc()
        return False


# ── Label map ────────────────────────────────────────────────────────────────

try:
    with open(LABEL_MAP_PATH) as f:
        label_map = json.load(f)
    print("[LABEL] Label map loaded ✅", flush=True)
except Exception as e:
    print(f"[LABEL] Error: {e}", flush=True)
    label_map = {"idx2species": {}, "idx2health": {}}

species_idx_to_name = {int(k): v for k, v in label_map.get("idx2species", {}).items()}
health_idx_to_name  = {int(k): v for k, v in label_map.get("idx2health",  {}).items()}


# ── Image preprocessing ───────────────────────────────────────────────────────

def preprocess_image(file_path):
    """
    Read -> resize -> normalise.

    Two-stage normalisation for better confidence calibration:
      1. Scale pixel values to [0, 1].
      2. Apply ImageNet mean/std (matches pre-trained backbone distribution).
    """
    img = cv2.imread(str(file_path))
    if img is None:
        return None

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Lanczos resize preserves edge/texture detail better than bilinear
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_LANCZOS4)

    img = img.astype(np.float32) / 255.0

    # ImageNet normalisation — improves calibration when the backbone was
    # pre-trained on ImageNet (MobileNet, EfficientNet, ResNet families).
    img = (img - _IMAGENET_MEAN) / _IMAGENET_STD

    return np.expand_dims(img, axis=0)   # shape: (1, 256, 256, 3)


# ── Confidence calibration ────────────────────────────────────────────────────

def temperature_scale(logits, temperature=2.5):
    """
    Temperature scaling — divides raw logits by T before softmax.
    T > 1  => softer (more honest) probabilities.
    T = 1  => original softmax output unchanged.

    T=2.5 reduces over-confident predictions significantly.
    """
    scaled = logits / temperature
    e = np.exp(scaled - np.max(scaled, axis=1, keepdims=True))   # stable
    return e / e.sum(axis=1, keepdims=True)


# ── Startup pre-load ─────────────────────────────────────────────────────────

print("[STARTUP] Loading model at startup...", flush=True)
ensure_model()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return jsonify({
        "status":       "ok",
        "service":      "FloraScan Backend",
        "model_loaded": model is not None,
        "fast_predict": _predict_fn is not None,
        "message":      "Ready for predictions" if model is not None else "Starting model load"
    })


@app.route("/health")
def health():
    return jsonify({
        "status":          "ok",
        "model_loaded":    model is not None,
"tflite_loaded":  interpreter is not None,\n        "fast_predict":    _predict_fn is not None,
        "species_classes": list(species_idx_to_name.values()),
        "health_classes":  list(health_idx_to_name.values()),
        "message":         "Model failed to load on startup. It will retry on request." if model is None else "Ready for predictions"
    })


@app.route("/image/upload", methods=["POST"])
def image_upload():
    try:
        if not ensure_model():
            return jsonify({"error": "Model not loaded. Check server logs."}), 500

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded. Use key 'file'."}), 400

        file = request.files["file"]
        if not file.filename:
            return jsonify({"error": "Empty filename"}), 400

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".jfif"}:
            return jsonify({"error": f"Unsupported file type: {ext}. Use jpg/png/webp/jfif."}), 400

        filename   = sha512(uuid.uuid4().hex.encode()).hexdigest() + ext
        images_dir = BASE_DIR / "images"
        images_dir.mkdir(exist_ok=True)
        file_path  = images_dir / filename
        file.save(str(file_path))

        img = preprocess_image(file_path)
        if img is None:
            return jsonify({"error": "Could not decode image."}), 400

        # Use compiled tf.function when available, else direct model call
        predict = _predict_fn if _predict_fn is not None else (lambda x: model(x, training=False))\n        preds   = predict(img.astype(np.float16) if interpreter else img)

        if isinstance(preds, dict):
            species_logits = np.array(preds.get("species"))
            health_logits  = np.array(preds.get("health"))
        elif isinstance(preds, (list, tuple)) and len(preds) == 2:
            species_logits = np.array(preds[0])
            health_logits  = np.array(preds[1])
        else:
            return jsonify({"error": "Unexpected model output format"}), 500

        species_probs = temperature_scale(species_logits)
        health_probs  = temperature_scale(health_logits)

        species_idx = int(np.argmax(species_probs, axis=1)[0])
        health_idx  = int(np.argmax(health_probs,  axis=1)[0])

        all_species = {
            species_idx_to_name.get(i, f"class_{i}"): round(float(species_probs[0][i]) * 100, 1)
            for i in range(len(species_probs[0]))
        }
        all_health = {
            health_idx_to_name.get(i, f"class_{i}"): round(float(health_probs[0][i]) * 100, 1)
            for i in range(len(health_probs[0]))
        }

        species_name = species_idx_to_name.get(species_idx, "unknown")
        health_name = health_idx_to_name.get(health_idx, "unknown")

        message = ""
        if species_name == "rose":
            message = "Roses are beautiful flowers!"

        return jsonify({
            "species":            species_name,
            "species_confidence": round(float(np.max(species_probs)) * 100, 1),
            "species_all":        all_species,
            "health":             health_name,
            "health_confidence":  round(float(np.max(health_probs))  * 100, 1),
            "health_all":         all_health,
            "message":            message,
        })

    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ── Database setup ───────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect('comments.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS comments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  type TEXT NOT NULL,
                  name TEXT,
                  email TEXT,
                  content TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()


# ── Comments routes ──────────────────────────────────────────────────────────

@app.route("/comments", methods=["GET"])
def get_comments():
    try:
        comment_type = request.args.get("type")
        conn = sqlite3.connect('comments.db')
        c = conn.cursor()

        if comment_type:
            c.execute("SELECT id, type, name, email, content, created_at FROM comments WHERE type = ? ORDER BY created_at DESC", (comment_type,))
        else:
            c.execute("SELECT id, type, name, email, content, created_at FROM comments ORDER BY created_at DESC")

        comments = []
        for row in c.fetchall():
            comments.append({
                "id": row[0],
                "type": row[1],
                "name": row[2] or "",
                "email": row[3] or "",
                "content": row[4],
                "created_at": row[5]
            })

        conn.close()
        return jsonify(comments)
    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
        return jsonify({"error": str(e)}), 500


@app.route("/comments", methods=["POST"])
def add_comment():
    try:
        data = request.get_json()

        if not data or "content" not in data or "type" not in data:
            return jsonify({"error": "Missing required fields: content and type"}), 400

        if data["type"] not in ["comment", "improvement"]:
            return jsonify({"error": "Type must be 'comment' or 'improvement'"}), 400

        conn = sqlite3.connect('comments.db')
        c = conn.cursor()
        c.execute("INSERT INTO comments (type, name, email, content) VALUES (?, ?, ?, ?)",
                 (data["type"], data.get("name", ""), data.get("email", ""), data["content"]))
        conn.commit()
        comment_id = c.lastrowid
        conn.close()

        return jsonify({
            "id": comment_id,
            "message": "Comment added successfully",
            "type": data["type"]
        }), 201
    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
