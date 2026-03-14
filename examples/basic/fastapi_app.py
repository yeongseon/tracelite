# pyright: reportMissingImports=false
"""Comprehensive FastAPI CRUD example with Tracelite tracing."""

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from tracelite import enable_tracing  # type: ignore[reportMissingImports]

app = FastAPI(title="Tracelite FastAPI CRUD Example")

# One-line setup: traces all HTTP methods and exposes /_tracelite dashboard.
enable_tracing(app)


class ItemCreate(BaseModel):
    name: str
    price: float


class ItemUpdate(BaseModel):
    name: str
    price: float


# Simple in-memory data store for example purposes.
ITEMS = {
    1: {
        "id": 1,
        "name": "Keyboard",
        "price": 79.99,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    2: {
        "id": 2,
        "name": "Mouse",
        "price": 39.99,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
}
next_id = 3


@app.get("/")
def read_root():
    return {
        "message": "FastAPI CRUD demo with Tracelite",
        "dashboard": "http://localhost:8000/_tracelite",
    }


@app.get("/items")
def list_items():
    """GET list endpoint: useful for list-page traffic inspection."""
    return list(ITEMS.values())


@app.get("/items/{item_id}")
def get_item(item_id: int):
    """GET-by-id endpoint: inspect path params and response bodies."""
    item = ITEMS.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/items", status_code=201)
def create_item(payload: ItemCreate):
    """POST create endpoint: inspect incoming JSON payloads."""
    global next_id
    item = {
        "id": next_id,
        "name": payload.name,
        "price": payload.price,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    ITEMS[next_id] = item
    next_id += 1
    return item


@app.put("/items/{item_id}")
def update_item(item_id: int, payload: ItemUpdate):
    """PUT update endpoint: compare before/after values in dashboard."""
    item = ITEMS.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    item["name"] = payload.name
    item["price"] = payload.price
    item["updated_at"] = datetime.now(timezone.utc).isoformat()
    return item


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    """DELETE endpoint: verify status codes and empty responses."""
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail="Item not found")
    deleted = ITEMS.pop(item_id)
    return {"deleted": True, "item": deleted}


if __name__ == "__main__":
    import uvicorn

    # Run this file directly: python examples/basic/fastapi_app.py
    # Tracelite dashboard: http://localhost:8000/_tracelite
    uvicorn.run(
        "examples.basic.fastapi_app:app", host="127.0.0.1", port=8000, reload=True
    )
