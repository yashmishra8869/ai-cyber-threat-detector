from __future__ import annotations

import io
import json
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from flask import Flask, Response, current_app, flash, jsonify, render_template, request
from werkzeug.utils import secure_filename

from config import (
    ALLOWED_UPLOAD_EXTENSIONS,
    APP_NAME,
    CONFUSION_MATRIX_PATH,
    DATABASE_PATH,
    DEBUG,
    MAX_UPLOAD_SIZE,
    METRICS_PATH,
    MODEL_PATH,
    PORT,
    PROJECT_ROOT,
    SECRET_KEY,
    TEMPLATE_DIR,
    UPLOAD_DIR,
)
from schema import (
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    NUMERIC_FEATURES,
    VALID_FLAGS,
    VALID_PROTOCOL_TYPES,
    VALID_SERVICES,
    validate_categorical_values,
    validate_numeric_values,
)


def initialize_database(db_path: str | Path = DATABASE_PATH) -> Path:
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(db_file))
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            label TEXT NOT NULL,
            probability REAL,
            analysis_type TEXT NOT NULL
        )
        """
    )
    connection.commit()
    connection.close()
    return db_file


def get_db_connection(db_path: str | Path = DATABASE_PATH):
    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    return connection


def save_prediction_history(label: str, probability: float | None = None, analysis_type: str = "individual", db_path: str | Path = DATABASE_PATH) -> None:
    connection = get_db_connection(db_path)
    connection.execute(
        "INSERT INTO analysis_history (created_at, label, probability, analysis_type) VALUES (?, ?, ?, ?)",
        (datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), label, probability, analysis_type),
    )
    connection.commit()
    connection.close()


def get_prediction_history(db_path: str | Path = DATABASE_PATH, limit: int = 20):
    connection = get_db_connection(db_path)
    rows = connection.execute(
        "SELECT created_at, label, probability, analysis_type FROM analysis_history ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    connection.close()
    return rows


def get_summary_cards(db_path: str | Path = DATABASE_PATH):
    rows = get_prediction_history(db_path, limit=1000)
    total = len(rows)
    normal_count = sum(1 for row in rows if str(row["label"]).lower() == "normal traffic")
    attack_count = sum(1 for row in rows if str(row["label"]).lower() == "attack traffic")
    return {
        "total": total,
        "normal": normal_count,
        "attack": attack_count,
        "sessions": total,
    }


def get_model_metrics(metrics_path: str | Path = METRICS_PATH):
    path = Path(metrics_path)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def is_model_ready(model_path: str | Path = MODEL_PATH):
    return Path(model_path).exists()


def load_model(model_path: str | Path = MODEL_PATH):
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Model not found at {path}. Train the model using 'python train_model.py' before starting the app.")
    return joblib.load(path)


def normalize_label(value: int | str | None) -> str:
    if value is None:
        return "Normal Traffic"
    if isinstance(value, str):
        if value.lower() == "normal":
            return "Normal Traffic"
        if value.lower() in {"attack", "anomaly", "malicious"}:
            return "Attack Traffic"
        return value
    return "Normal Traffic" if int(value) == 0 else "Attack Traffic"


def parse_feature_value(raw_value: object, column_name: str):
    if column_name in CATEGORICAL_FEATURES:
        value = str(raw_value).strip()
        if value == "":
            raise ValueError(f"Field '{column_name}' is required.")
        return value

    if raw_value is None or str(raw_value).strip() == "":
        raise ValueError(f"Field '{column_name}' is required.")
    try:
        numeric_value = float(raw_value)
    except (TypeError, ValueError):
        raise ValueError(f"Field '{column_name}' must be a numeric value.")
    if not np.isfinite(numeric_value):
        raise ValueError(f"Field '{column_name}' contains an invalid numeric value.")
    return numeric_value


def build_feature_dataframe(raw_record: dict) -> pd.DataFrame:
    prepared = {}
    for column in FEATURE_COLUMNS:
        if column not in raw_record:
            raise ValueError(f"Missing required feature '{column}'.")
        prepared[column] = parse_feature_value(raw_record[column], column)
    frame = pd.DataFrame([prepared], columns=FEATURE_COLUMNS)
    for column in CATEGORICAL_FEATURES:
        frame[column] = frame[column].astype(str).str.strip()
    for column in NUMERIC_FEATURES:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    validate_categorical_values(frame)
    validate_numeric_values(frame)
    return frame


def predict_single_record(record: dict, model=None):
    model = model or load_model(current_app.config["MODEL_PATH"])
    df = build_feature_dataframe(record)
    prediction = model.predict(df)[0]
    probability = None
    if hasattr(model, "predict_proba"):
        predictions = model.predict_proba(df)[0]
        class_index = int(np.where(model.classes_ == prediction)[0][0]) if prediction in model.classes_ else 0
        probability = float(predictions[class_index])
    label = normalize_label(prediction)
    return {
        "label": label,
        "prediction": int(prediction),
        "status": "Normal Traffic" if int(prediction) == 0 else "Attack Traffic",
        "probability": probability,
        "confidence_message": "Estimated probability from the model (not a guarantee)." if probability is not None else "Probability not available.",
    }


def create_app(test_config=None):
    app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(Path(__file__).resolve().parent / "static"))
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE
    app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)
    app.config["MODEL_PATH"] = str(MODEL_PATH)
    app.config["METRICS_PATH"] = str(METRICS_PATH)
    app.config["DATABASE_PATH"] = str(DATABASE_PATH)
    app.config["DEBUG"] = DEBUG
    app.config["TESTING"] = False
    if test_config:
        app.config.update(test_config)

    initialize_database(app.config["DATABASE_PATH"])

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(_error):
        return render_template("500.html"), 500

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/analyze", methods=["GET", "POST"])
    def analyze():
        feature_fields = [{"name": name, "label": name.replace("_", " ").title()} for name in FEATURE_COLUMNS]
        categorical_features = list(CATEGORICAL_FEATURES)
        choices = {
            "protocol_type": sorted(VALID_PROTOCOL_TYPES),
            "service": sorted(VALID_SERVICES),
            "flag": sorted(VALID_FLAGS),
        }

        if request.method == "GET":
            return render_template("analyze.html", feature_fields=feature_fields, categorical_features=categorical_features, choices=choices)

        if "csv_file" in request.files and request.files["csv_file"].filename:
            file = request.files["csv_file"]
            filename = secure_filename(file.filename)
            if not filename:
                flash("Please select a CSV file to upload.", "danger")
                return render_template("analyze.html", feature_fields=feature_fields, categorical_features=categorical_features, choices=choices)
            if Path(filename).suffix.lower() != ".csv":
                flash("Only CSV files are supported.", "danger")
                return render_template("analyze.html", feature_fields=feature_fields, categorical_features=categorical_features, choices=choices)
            file.stream.seek(0, os.SEEK_END)
            file_size = file.stream.tell()
            file.stream.seek(0)
            if file_size > MAX_UPLOAD_SIZE:
                flash("File is too large. Maximum supported size is 2 MB.", "danger")
                return render_template("analyze.html", feature_fields=feature_fields, categorical_features=categorical_features, choices=choices)
            upload_path = Path(app.config["UPLOAD_FOLDER"]) / f"{uuid.uuid4().hex}_{filename}"
            upload_path.parent.mkdir(parents=True, exist_ok=True)
            file.save(upload_path)
            try:
                df = pd.read_csv(upload_path)
            except Exception as exc:
                flash(f"Malformed CSV file: {exc}", "danger")
                return render_template("analyze.html", feature_fields=feature_fields, categorical_features=categorical_features, choices=choices)
            if df.empty:
                flash("Uploaded CSV file is empty.", "danger")
                return render_template("analyze.html", feature_fields=feature_fields, categorical_features=categorical_features, choices=choices)
            if len(df) > 100:
                flash("CSV upload limit is 100 rows per file.", "danger")
                return render_template("analyze.html", feature_fields=feature_fields, categorical_features=categorical_features, choices=choices)

            missing_columns = [column for column in FEATURE_COLUMNS if column not in df.columns]
            if missing_columns:
                flash(f"Missing required columns: {missing_columns}", "danger")
                return render_template("analyze.html", feature_fields=feature_fields, categorical_features=categorical_features, choices=choices)

            try:
                for column in NUMERIC_FEATURES:
                    df[column] = pd.to_numeric(df[column], errors="raise")
                df[FEATURE_COLUMNS] = df[FEATURE_COLUMNS].replace({np.nan: None})
                validate_categorical_values(df)
                validate_numeric_values(df)
            except Exception as exc:
                flash(f"CSV validation error: {exc}", "danger")
                return render_template("analyze.html", feature_fields=feature_fields, categorical_features=categorical_features, choices=choices)

            try:
                model = load_model(app.config["MODEL_PATH"])
            except FileNotFoundError as exc:
                flash(str(exc), "danger")
                return render_template("analyze.html", feature_fields=feature_fields, categorical_features=categorical_features, choices=choices)

            results = []
            for index, row in df.iterrows():
                record = row.to_dict()
                outcome = predict_single_record(record, model=model)
                label = outcome["label"]
                save_prediction_history(label, outcome["probability"], "csv", app.config["DATABASE_PATH"])
                results.append(
                    {
                        "record_number": index + 1,
                        "prediction": label,
                        "probability": round(float(outcome["probability"]), 6) if outcome["probability"] is not None else None,
                        "status": outcome["status"],
                    }
                )

            results_df = pd.DataFrame(results)
            csv_buffer = io.StringIO()
            results_df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            return render_template(
                "result.html",
                single_prediction=None,
                csv_results=results,
                total_records=len(results),
                normal_count=sum(1 for item in results if item["prediction"] == "Normal Traffic"),
                attack_count=sum(1 for item in results if item["prediction"] == "Attack Traffic"),
                csv_download=csv_buffer.getvalue(),
            )

        raw_record = {}
        for column in FEATURE_COLUMNS:
            value = request.form.get(column)
            if value is None:
                flash(f"Missing feature value: {column}", "danger")
                return render_template("analyze.html", feature_fields=feature_fields, categorical_features=categorical_features, choices=choices)
            raw_record[column] = value

        try:
            prediction = predict_single_record(raw_record)
            save_prediction_history(prediction["label"], prediction["probability"], "individual", app.config["DATABASE_PATH"])
            return render_template(
                "result.html",
                single_prediction=prediction,
                csv_results=[],
                total_records=1,
                normal_count=1 if prediction["label"] == "Normal Traffic" else 0,
                attack_count=1 if prediction["label"] == "Attack Traffic" else 0,
                analysis_time=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            )
        except FileNotFoundError as exc:
            flash(str(exc), "danger")
            return render_template("analyze.html", feature_fields=feature_fields, categorical_features=categorical_features, choices=choices)
        except Exception as exc:
            flash(f"Validation error: {exc}", "danger")
            return render_template("analyze.html", feature_fields=feature_fields, categorical_features=categorical_features, choices=choices)

    @app.route("/dashboard")
    def dashboard():
        history = get_prediction_history(app.config["DATABASE_PATH"], limit=100)
        summary = get_summary_cards(app.config["DATABASE_PATH"])
        metrics = get_model_metrics(app.config["METRICS_PATH"])
        recent_history = [
            {
                "timestamp": row["created_at"],
                "label": row["label"],
                "analysis_type": row["analysis_type"],
                "probability": row["probability"],
            }
            for row in history
        ]
        chart_payload = {
            "labels": ["Normal Traffic", "Attack Traffic"],
            "values": [summary["normal"], summary["attack"]],
            "history": recent_history,
            "metrics": metrics,
        }
        current_date = datetime.utcnow().strftime("%Y-%m-%d")
        model_status = "Ready" if is_model_ready(app.config["MODEL_PATH"]) else "Model not available"
        return render_template(
            "dashboard.html",
            summary=summary,
            history=recent_history,
            metrics=metrics,
            chart_payload=chart_payload,
            current_date=current_date,
            model_status=model_status,
        )

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "model_ready": is_model_ready(app.config["MODEL_PATH"])})

    @app.route("/download-results")
    def download_results():
        data = request.args.get("data")
        if not data:
            return jsonify({"error": "No result data available"}), 400
        decoded = json.loads(data)
        df = pd.DataFrame(decoded)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        return Response(
            csv_buffer.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=result_summary.csv"},
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
