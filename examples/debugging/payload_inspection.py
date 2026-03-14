"""Inspect request payloads with Tracelite.

Useful when debugging why an API endpoint receives unexpected data.
"""

from importlib import import_module

from fastapi import FastAPI, Request

enable_tracing = import_module("tracelite").enable_tracing

app = FastAPI()
enable_tracing(app)


@app.post("/api/users")
async def create_user(request: Request):
    body = await request.json()
    # Simulate validation
    if "email" not in body:
        return {"error": "email is required"}, 422
    return {"id": 1, "email": body["email"]}


@app.put("/api/users/{user_id}")
async def update_user(user_id: int, request: Request):
    body = await request.json()
    return {"id": user_id, **body}


# Run: uvicorn examples.debugging.payload_inspection:app --reload
# Then: curl -X POST http://localhost:8000/api/users -H "Content-Type: application/json" -d '{"name": "Alice"}'
# Check: http://localhost:8000/_tracelite - see the request body that was sent
