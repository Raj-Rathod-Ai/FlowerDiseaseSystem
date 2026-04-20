import shutil
import tensorflow as tf
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"
INPUT_MODEL = MODEL_DIR / "multitask_finetuned.keras"
OUTPUT_MODEL = MODEL_DIR / "multitask_finetuned.tflite"
SAVED_MODEL_DIR = MODEL_DIR / "tmp_saved_model"

if not INPUT_MODEL.exists():
    raise FileNotFoundError(f"Keras model not found at {INPUT_MODEL}")

print(f"Loading Keras model from: {INPUT_MODEL}")
model = tf.keras.models.load_model(str(INPUT_MODEL))

if SAVED_MODEL_DIR.exists():
    shutil.rmtree(SAVED_MODEL_DIR)

print(f"Saving temporary SavedModel to: {SAVED_MODEL_DIR}")
tf.saved_model.save(model, str(SAVED_MODEL_DIR))

print("Converting SavedModel to TFLite...")
converter = tf.lite.TFLiteConverter.from_saved_model(str(SAVED_MODEL_DIR))
# Enable optimizations for size and speed
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.float16]  # Use float16 for compression
# Optional: further compression
# converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]

try:
    tflite_model = converter.convert()
except Exception as exc:
    raise RuntimeError(f"TFLite conversion failed: {exc}")

print(f"Writing TFLite model to: {OUTPUT_MODEL}")
OUTPUT_MODEL.write_bytes(tflite_model)
print("Conversion complete.")
