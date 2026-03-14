import shlex

from tracelite.core.replay import generate_curl


def _one_line(command: str) -> str:
    return command.replace(" \\\n  ", " ")


def test_generate_curl_simple_get_request():
    command = generate_curl("GET", "/ping")
    assert _one_line(command) == "curl -X GET http://localhost:8000/ping"


def test_generate_curl_post_with_body_includes_data_flag():
    command = generate_curl("POST", "/items", body='{"name":"test"}')
    one_line = _one_line(command)

    assert " -d " in one_line
    assert shlex.quote('{"name":"test"}') in one_line


def test_generate_curl_includes_header_flags():
    command = generate_curl(
        "GET",
        "/headers",
        headers={"Authorization": "Bearer token", "X-Custom": "1"},
    )
    one_line = _one_line(command)

    assert "-H" in one_line
    assert shlex.quote("Authorization: Bearer token") in one_line
    assert shlex.quote("X-Custom: 1") in one_line


def test_generate_curl_skips_host_content_length_transfer_encoding_headers():
    command = generate_curl(
        "GET",
        "/skip",
        headers={
            "Host": "example.com",
            "Content-Length": "123",
            "Transfer-Encoding": "chunked",
            "X-Trace": "yes",
        },
    )
    one_line = _one_line(command)

    assert "Host:" not in one_line
    assert "Content-Length:" not in one_line
    assert "Transfer-Encoding:" not in one_line
    assert shlex.quote("X-Trace: yes") in one_line


def test_generate_curl_includes_query_string_in_url():
    command = generate_curl("GET", "/search", query="q=tracelite&page=2")
    one_line = _one_line(command)

    assert "'http://localhost:8000/search?q=tracelite&page=2'" in one_line


def test_generate_curl_uses_custom_base_url():
    command = generate_curl("GET", "/ping", base_url="https://api.example.com")
    one_line = _one_line(command)

    assert "https://api.example.com/ping" in one_line


def test_generate_curl_quotes_special_characters_in_url():
    command = generate_curl("GET", "/items/hello world", query="q=weird value&x=1")
    one_line = _one_line(command)
    expected_url = "http://localhost:8000/items/hello world?q=weird value&x=1"

    assert shlex.quote(expected_url) in one_line
