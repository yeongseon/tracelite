import json

from tracelite.core.diff import diff_responses, diff_responses_text


def test_diff_responses_both_none_returns_empty_list():
    assert diff_responses(None, None) == []


def test_diff_responses_same_json_returns_empty_list():
    body = json.dumps({"a": 1, "b": [1, 2], "c": {"x": True}})
    assert diff_responses(body, body) == []


def test_diff_responses_different_simple_values_returns_one_entry():
    diffs = diff_responses(json.dumps(1), json.dumps(2))
    assert diffs == [{"path": "$", "old_value": 1, "new_value": 2}]


def test_diff_responses_added_key_has_none_old_value():
    diffs = diff_responses(json.dumps({"a": 1}), json.dumps({"a": 1, "b": 2}))
    assert diffs == [{"path": "$.b", "old_value": None, "new_value": 2}]


def test_diff_responses_removed_key_has_none_new_value():
    diffs = diff_responses(json.dumps({"a": 1, "b": 2}), json.dumps({"a": 1}))
    assert diffs == [{"path": "$.b", "old_value": 2, "new_value": None}]


def test_diff_responses_nested_dict_path_includes_nested_key():
    diffs = diff_responses(
        json.dumps({"outer": {"inner": {"flag": False}}}),
        json.dumps({"outer": {"inner": {"flag": True}}}),
    )
    assert diffs == [
        {"path": "$.outer.inner.flag", "old_value": False, "new_value": True}
    ]


def test_diff_responses_list_changes_detects_changed_and_added_items():
    diffs = diff_responses(json.dumps(["a", "b"]), json.dumps(["a", "c", "d"]))
    assert diffs == [
        {"path": "$[1]", "old_value": "b", "new_value": "c"},
        {"path": "$[2]", "old_value": None, "new_value": "d"},
    ]


def test_diff_responses_non_json_strings_that_differ_returns_root_diff():
    diffs = diff_responses("plain text old", "plain text new")
    assert diffs == [
        {"path": "$", "old_value": "plain text old", "new_value": "plain text new"}
    ]


def test_diff_responses_non_json_strings_that_are_same_returns_empty_list():
    assert diff_responses("same text", "same text") == []


def test_diff_responses_text_returns_no_differences_message_when_equal():
    assert (
        diff_responses_text(json.dumps({"a": 1}), json.dumps({"a": 1}))
        == "No differences found."
    )


def test_diff_responses_text_returns_formatted_output_when_different():
    text = diff_responses_text(json.dumps({"a": 1}), json.dumps({"a": 2}))

    assert "$.a:" in text
    assert "- 1" in text
    assert "+ 2" in text


def test_diff_responses_type_mismatch_dict_vs_list_returns_diff_entry():
    diffs = diff_responses(json.dumps({"a": 1}), json.dumps([{"a": 1}]))
    assert diffs == [{"path": "$", "old_value": {"a": 1}, "new_value": [{"a": 1}]}]
