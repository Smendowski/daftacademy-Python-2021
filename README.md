## Create and Activate Virtual Environment
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


### CURL Testing Commands
```PowerShell
HTTP 401:

curl -i "http://127.0.0.1:5555/auth?password=haslo&password_hash=f34ad4b3ae1e2cf33092e2abb60dc0444781c15d0e2e9ecdb37e4b14176a0164027b05900e09fa0f61a1882e0b89fbfa5dcfcc9765dd2ca4377e2c794837e091"

HTTP 204:

curl -i "http://127.0.0.1:5555/auth?password=haslo&password_hash=013c6889f799cd986a735118e1888727d1435f7f623d05d58c61bf2cd8b49ac90105e5786ceaabd62bbc27336153d0d316b2d13b36804080c44aa6198c533215"

Register Patient:
curl -i -X POST -H "Content-Type: application/json" -d "{\"name\":\"Krzysztof\", \"surname\":\"Jakubiak\"}" http://127.0.0.1:5555/register

Get Patient:
curl -i -X GET http://127.0.0.1:5555/patient/1
```