# pyright: reportMissingImports=false
"""Comprehensive Flask CRUD example with Tracelite tracing."""

from datetime import datetime, timezone

from flask import Flask, jsonify, request

from tracelite import enable_tracing  # type: ignore[reportMissingImports]

app = Flask(__name__)

# One-line setup: captures Flask routes and serves /_tracelite dashboard.
enable_tracing(app)

# In-memory data store so you can test all CRUD routes quickly.
ITEMS = {
    1: {
        "id": 1,
        "name": "Notebook",
        "price": 12.5,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    2: {
        "id": 2,
        "name": "Pen",
        "price": 2.5,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
}
next_id = 3


@app.get("/")
def index():
    return jsonify(
        {
            "message": "Flask CRUD demo with Tracelite",
            "dashboard": "http://localhost:5000/_tracelite",
        }
    )


@app.get("/items")
def list_items():
    return jsonify(list(ITEMS.values()))


@app.get("/items/<int:item_id>")
def get_item(item_id: int):
    item = ITEMS.get(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item)


@app.post("/items")
def create_item():
    global next_id
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    price = payload.get("price")

    if not name or not isinstance(price, (int, float)):
        return jsonify({"error": "name (str) and price (number) are required"}), 400

    item = {
        "id": next_id,
        "name": str(name),
        "price": float(price),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    ITEMS[next_id] = item
    next_id += 1
    return jsonify(item), 201


@app.put("/items/<int:item_id>")
def update_item(item_id: int):
    payload = request.get_json(silent=True) or {}
    item = ITEMS.get(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    name = payload.get("name")
    price = payload.get("price")
    if not name or not isinstance(price, (int, float)):
        return jsonify({"error": "name (str) and price (number) are required"}), 400

    item["name"] = str(name)
    item["price"] = float(price)
    item["updated_at"] = datetime.now(timezone.utc).isoformat()
    return jsonify(item)


@app.delete("/items/<int:item_id>")
def delete_item(item_id: int):
    item = ITEMS.pop(item_id, None)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify({"deleted": True, "item": item})


if __name__ == "__main__":
    # Run this file directly: python examples/basic/flask_app.py
    # Tracelite dashboard: http://localhost:5000/_tracelite
    app.run(host="127.0.0.1", port=5000, debug=True)
