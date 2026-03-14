# pyright: reportMissingImports=false
"""Compare API response changes using Tracelite's diff feature."""

from datetime import datetime, timezone

from fastapi import FastAPI

from tracelite import enable_tracing  # type: ignore[reportMissingImports]
from tracelite.core.diff import (  # type: ignore[reportMissingImports]
    diff_responses,
    diff_responses_text,
)

app = FastAPI(title="Tracelite Response Diff Example")

# One-line tracing setup; inspect captured traffic at /_tracelite.
enable_tracing(app)

# Mutable state to simulate an endpoint whose response changes over time.
STATE = {"version": 1, "feature_flag": False}


@app.get("/profile")
def profile():
    """Endpoint with changing response fields for diff demonstrations."""
    STATE["version"] += 1
    STATE["feature_flag"] = not STATE["feature_flag"]
    return {
        "user": {"id": 42, "name": "Alice"},
        "meta": {
            "version": STATE["version"],
            "feature_flag": STATE["feature_flag"],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def show_programmatic_diff() -> None:
    """Programmatic use case: compare two captured JSON response strings."""
    old_response = '{"user": {"id": 42, "name": "Alice"}, "meta": {"version": 1, "feature_flag": false}}'
    new_response = '{"user": {"id": 42, "name": "Alice"}, "meta": {"version": 2, "feature_flag": true}}'

    # Structured diff for custom tooling.
    structured_diff = diff_responses(old_response, new_response)
    print("Structured diff:")
    for entry in structured_diff:
        print(f"- {entry['path']}: {entry['old_value']} -> {entry['new_value']}")

    # Text diff for terminal output.
    print("\nText diff:")
    print(diff_responses_text(old_response, new_response))


if __name__ == "__main__":
    import uvicorn

    show_programmatic_diff()
    # Make repeated calls to /profile, then compare responses in /_tracelite.
    uvicorn.run(
        "examples.debugging.response_diff:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
