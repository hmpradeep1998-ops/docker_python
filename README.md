# Python (Flask) - Hello Service

## What it does
- `GET /` -> JSON response
- `GET /health` -> OK
- Uses `PORT` env var (default 8080)

## Local Run (without Docker)
```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
python app.py
curl http://localhost:8080/
curl http://localhost:8080/health
```

## Your Task
Create `Dockerfile` and `.dockerignore`, then containerize it.
