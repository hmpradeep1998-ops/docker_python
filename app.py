from flask import Flask, jsonify
import os, socket
from datetime import datetime

app = Flask(__name__)
PORT = int(os.environ.get("PORT", "8080"))

@app.get("/")
def home():
    return jsonify(
        service="python-flask-hello",
        message="Hello from Python (Flask) in a container!",
        hostname=socket.gethostname(),
        time=datetime.utcnow().isoformat() + "Z",
    )

@app.get("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
