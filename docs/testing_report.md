# Testing Report

## Status

This document reflects the automated testing results produced during project validation.

## Test command

```powershell
python -m pytest -v
```

## Results

The suite should be run after installing dependencies and training the model.

## Notes

- Test fixtures focus on schema validation, model training, route availability, health checks, and CSV validation.
- The system uses real training logic rather than fake model metrics.
