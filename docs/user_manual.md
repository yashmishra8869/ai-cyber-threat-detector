# User Manual

## Overview

This application lets you analyze network traffic records and identify whether they appear to be normal or malicious.

## Features

- Analyze a single traffic record by filling the form
- Upload CSV files containing multiple traffic records
- View prediction history on the dashboard
- Review model evaluation metrics and charts

## How to Use

### Single record prediction

1. Open the Analyze page.
2. Fill all 41 input fields with valid values.
3. Submit the form.
4. View the predicted label and probability.

### Batch CSV prediction

1. Open the Analyze page.
2. Upload a CSV file with the required columns.
3. Submit the file.
4. Review the prediction summary and download the result CSV.

## Notes

- Only valid CSV files are accepted.
- Files larger than 2 MB are rejected.
- Uploads are limited to 100 rows.
- Inputs are validated to prevent malformed traffic records.
