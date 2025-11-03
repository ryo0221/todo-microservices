import json
import logging
import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from gateway.app.middleware.logging_middleware import LoggingMiddleware

@pytest.fixture()
def fake_app():
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)

    @app.get("/todos")
    async def todos():
        return JSONResponse({"todos": []})

    return app


def test_logging_middleware_outputs_structured_log(caplog, fake_app):
    """
    LoggingMiddleware should emit structured JSON logs for each request.
    """
    caplog.set_level(logging.INFO)

    client = TestClient(fake_app)
    response = client.get("/todos")

    assert response.status_code == 200

    # Find valid JSON log lines
    valid_json_lines = [
        rec.message for rec in caplog.records
        if rec.message.strip().startswith("{") and rec.message.strip().endswith("}")
    ]

    assert valid_json_lines, "No structured JSON logs found"
    log_entry = json.loads(valid_json_lines[0])

    # Validate structure
    assert set(["method", "path", "status_code", "duration_ms"]).issubset(log_entry.keys())
    assert log_entry["method"] == "GET"
    assert log_entry["path"] == "/todos"
    assert isinstance(log_entry["duration_ms"], (int, float))