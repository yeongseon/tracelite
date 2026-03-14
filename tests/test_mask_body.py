import json

from tracelite.core.filters import _mask_dict_recursive, mask_body


def test_mask_body_masks_sensitive_keys_in_json():
    body = json.dumps({"username": "alice", "password": "secret", "token": "abc"})

    masked = mask_body(body, ["password", "token"])

    assert masked is not None
    parsed = json.loads(masked)
    assert parsed["username"] == "alice"
    assert parsed["password"] == "***"
    assert parsed["token"] == "***"


def test_mask_body_masks_nested_json_recursively():
    body = json.dumps(
        {
            "profile": {
                "email": "user@example.com",
                "credentials": {"password": "p@ss", "secret": "s3cr3t"},
            }
        }
    )

    masked = mask_body(body, ["password", "secret"])

    assert masked is not None
    parsed = json.loads(masked)
    assert parsed["profile"]["credentials"]["password"] == "***"
    assert parsed["profile"]["credentials"]["secret"] == "***"


def test_mask_body_masks_dict_objects_inside_arrays():
    body = json.dumps(
        {
            "items": [
                {"name": "item1", "token": "a"},
                {"name": "item2", "password": "b"},
                "plain-string",
            ]
        }
    )

    masked = mask_body(body, ["password", "token"])

    assert masked is not None
    parsed = json.loads(masked)
    assert parsed["items"][0]["token"] == "***"
    assert parsed["items"][1]["password"] == "***"
    assert parsed["items"][2] == "plain-string"


def test_mask_body_returns_original_for_non_json():
    body = "not-json-body"
    assert mask_body(body, ["password"]) == body


def test_mask_body_returns_none_for_none_body():
    assert mask_body(None, ["password"]) is None


def test_mask_body_returns_empty_string_for_empty_body():
    assert mask_body("", ["password"]) == ""


def test_mask_body_matches_keys_case_insensitively():
    body = json.dumps({"Password": "SecretValue", "other": "ok"})

    masked = mask_body(body, ["password"])

    assert masked is not None
    parsed = json.loads(masked)
    assert parsed["Password"] == "***"
    assert parsed["other"] == "ok"


def test_mask_body_uses_custom_mask_string():
    body = json.dumps({"password": "secret"})

    masked = mask_body(body, ["password"], mask="[REDACTED]")

    assert masked is not None
    parsed = json.loads(masked)
    assert parsed["password"] == "[REDACTED]"


def test_mask_dict_recursive_masks_nested_dict_and_list_values():
    data = {
        "token": "root-token",
        "nested": {
            "Password": "hidden",
            "arr": [{"secret": "top"}, {"safe": "value"}],
        },
    }

    masked = _mask_dict_recursive(data, ["token", "password", "secret"], "***")

    assert masked["token"] == "***"
    assert masked["nested"]["Password"] == "***"
    assert masked["nested"]["arr"][0]["secret"] == "***"
    assert masked["nested"]["arr"][1]["safe"] == "value"
