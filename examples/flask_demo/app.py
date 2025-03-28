from flask import Flask, jsonify

from tracelite.core.config import load_config
from tracelite.core.storage.sqlite import SQLiteStorage
from tracelite.middleware.flask import TraceliteMiddleware

app = Flask(__name__)

# Load configuration and storage
config = load_config()
storage = SQLiteStorage(db_path=config.db_path)

# Apply Tracelite middleware
app.wsgi_app = TraceliteMiddleware(app.wsgi_app, storage, config)


@app.route("/ping")
def ping():
    return jsonify(message="pong")


@app.route("/user", methods=["POST"])
def create_user():
    return jsonify(status="created"), 201


if __name__ == "__main__":
    app.run(port=5001, debug=True)
