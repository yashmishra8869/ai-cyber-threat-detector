import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "model"
UPLOAD_DIR = PROJECT_ROOT / "uploads"
STATIC_DIR = PROJECT_ROOT / "static"
TEMPLATE_DIR = PROJECT_ROOT / "templates"

DATASET_PATH = DATA_DIR / "KDDTrain+.txt"
MODEL_PATH = MODEL_DIR / "threat_pipeline.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"
CONFUSION_MATRIX_PATH = MODEL_DIR / "confusion_matrix.png"
DATABASE_PATH = DATA_DIR / "predictions.db"

MAX_UPLOAD_SIZE = 2 * 1024 * 1024
ALLOWED_UPLOAD_EXTENSIONS = {".csv"}

SECRET_KEY = os.environ.get("SECRET_KEY", "cyber-threat-detector-secret-key")
DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
PORT = int(os.environ.get("PORT", "5000"))

APP_NAME = "AI Threat Detector"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
