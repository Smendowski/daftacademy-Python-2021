## Activate Virtual Environment
```PowerShell
.\daft\Scripts\activate
```

## Start Localhost Server with Unicorn
```PowerShell
python -m uvicorn main:app --port 5555
# Uvicorn running on http://127.0.0.1:5555
```

## Run Pytest's test cases
```PowerShell
pytest tests.py
```