from flask import Flask

app = Flask(__name__)

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/version")
def version():
    return {"version": "1.0.0"}

if __name__ == "__main__":
    app.run(port=5000, debug=True)