"""Sensitive data masking example.

Tracelite automatically masks sensitive fields in headers AND request/response bodies.
"""

from importlib import import_module

from fastapi import FastAPI

enable_tracing = import_module("tracelite").enable_tracing
TraceliteConfig = import_module("tracelite.core.config").TraceliteConfig

app = FastAPI()

# Custom config with additional mask keys
config = TraceliteConfig(
    mask_keys=["password", "token", "authorization", "secret", "credit_card", "ssn"]
)
enable_tracing(app, config=config)


@app.post("/api/register")
async def register():
    # Response body will have 'token' masked in the dashboard
    return {"user_id": 1, "token": "secret-jwt-token", "status": "created"}


@app.post("/api/payment")
async def payment():
    # 'credit_card' will be masked in captured request body
    return {"status": "processed", "transaction_id": "txn_123"}


# Run: uvicorn examples.security.masking_example:app --reload
# Then: curl -X POST http://localhost:8000/api/register
# Check /_tracelite - 'token' in the response body will show as '***'
