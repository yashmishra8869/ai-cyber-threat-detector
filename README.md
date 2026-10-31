# AI-Powered Cybersecurity Threat Detection

This project builds an AI-powered cybersecurity threat detection web application using Flask, scikit-learn, pandas, and a Random Forest classifier. It analyzes network traffic records and classifies them as either normal traffic or suspicious/attack traffic using a trained NSL-KDD-based model.

## Project Goal

The application is designed as an educational final-year B.Tech project and demonstrates how a machine learning model can classify network traffic records into two classes:

- Normal Traffic
- Attack Traffic

This project is not a live packet sniffer, firewall, or intrusion prevention system. It analyzes pre-existing traffic records and predicts whether a record is normal or malicious based on a trained ML model.

## Features

- Modern cybersecurity dashboard with summary cards and charts
- Individual traffic analysis form for all 41 NSL-KDD features
- CSV upload analysis for batch records
- Real Random Forest pipeline training and evaluation
- Model artifact persistence using joblib
- Prediction history stored in SQLite
- Downloadable CSV prediction results
- Health endpoint for deployment verification
- Flask app configured for Render deployment

## Tech Stack

- Python
- Flask
- scikit-learn
- pandas
- NumPy
- joblib
- matplotlib
- Bootstrap 5
- SQLite
- Pytest

## Folder Structure

cyber_threat_detector/
    app.py
    train_model.py
    schema.py
    config.py
    requirements.txt
    render.yaml
    .gitignore
    README.md
    data/
        README.md
    model/
        README.md
    uploads/
    static/
        css/style.css
        js/main.js
        images/
    templates/
        base.html
        index.html
        analyze.html
        result.html
        dashboard.html
        about.html
        404.html
        500.html
    tests/
        test_schema.py
        test_model.py
        test_routes.py
        test_csv_upload.py
        test_dashboard.py
        test_health.py
    docs/
        deployment.md
        user_manual.md
        testing_report.md

## Dataset Setup

This model requires the genuine NSL-KDD training file.

1. Download the NSL-KDD dataset from the official project page or a trusted source.
2. Place the file named `KDDTrain+.txt` in the `data/` folder.
3. The file should contain the 41 traffic features and the labels `attack_name` and `difficulty`.

If the file is missing, the training script will raise a clear error explaining where to place it.

## Local Setup

### 1. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Train the model

```powershell
python train_model.py
```

### 4. Run the app

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

### 5. Run tests

```powershell
python -m pytest -v
```

## Deployment

This project is configured for Render deployment with a Gunicorn production server.

### Render configuration

- `requirements.txt` installs all Python dependencies.
- `render.yaml` defines the web service.
- `gunicorn app:app --bind 0.0.0.0:$PORT` is the start command.

### Deployment steps

1. Push the repository to GitHub.
2. Log in to Render.
3. Create a new Web Service.
4. Connect the GitHub repository.
5. Use the default build command.
6. Set the start command to:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

7. Deploy.

## Important Notes

- The application is designed for educational demonstration.
- It does not perform live packet monitoring or live blocking.
- The training process uses the NSL-KDD dataset and a Random Forest model.
- The model is loaded from a saved joblib artifact and is not retrained on every startup.

## Limitations

- This is a static feature-based classification system.
- It is not a real-time IDS or firewall.
- Model performance depends on the quality and availability of the actual NSL-KDD dataset.

## License

This project is intended for academic use and demonstration purposes.
