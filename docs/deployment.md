# Deployment Guide

## Render Deployment

1. Create a GitHub repository for this project.
2. Push the code using Git.
3. Log in to Render and create a new Web Service.
4. Connect your GitHub repository.
5. Select the repository and the root folder.
6. Set the start command:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

7. Add environment variables if needed:
   - `FLASK_DEBUG=false`
   - `SECRET_KEY=<secure-value>`
8. Save and deploy.
9. Copy the public URL from Render after the build completes.

## Important notes

- The app must load a trained model artifact from `model/threat_pipeline.joblib`.
- Train the model locally before deployment using `python train_model.py`.
- Ensure the model is included in the repository or retrieved using a trusted deployment process.
- Do not rely on local-only path structures in production.
