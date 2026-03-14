"""Debug authentication headers with Tracelite.

This example shows how to inspect Authorization headers
being sent to your API, while keeping sensitive values masked.
"""

from importlib import import_module

from fastapi import FastAPI, Header

enable_tracing = import_module("tracelite").enable_tracing

app = FastAPI()
enable_tracing(app)


@app.get("/protected")
def protected_endpoint(authorization: str = Header(None)):
    if not authorization:
        return {"error": "Missing Authorization header"}, 401
    return {"message": "Access granted", "auth_type": authorization.split()[0]}


@app.post("/api/login")
def login():
    return {"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}


# Run: uvicorn examples.debugging.auth_headers:app --reload
# Then: curl -H "Authorization: Bearer mytoken" http://localhost:8000/protected
# Check: http://localhost:8000/_tracelite - authorization header will be masked
