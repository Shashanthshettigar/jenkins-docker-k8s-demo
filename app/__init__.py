from flask import Flask, jsonify


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def home():
        return jsonify({"message": "Hello from flask-cicd-eks!", "status": "ok"})

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy"}), 200

    return app
