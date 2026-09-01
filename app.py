import os
from flask import Flask

app = Flask(__name__)

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/version")
def version():
    app_version = os.environ.get("APP_VERSION", "1.0.0")
    return {"version": app_version}

@app.route("/ping")
def ping():
    return {"message": "pong"}

@app.route("/status")
def status():
    return {"service": "running"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)