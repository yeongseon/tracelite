from tracelite.core.filters import mask_sensitive, should_exclude


def test_should_exclude():
    assert should_exclude("/static/img.png", ["/static"])
    assert should_exclude("/favicon.ico", ["/static", "/favicon.ico"])
    assert not should_exclude("/api/data", ["/static"])


def test_mask_sensitive():
    data = {"token": "abc123", "user": "admin", "Password": "secret"}
    masked = mask_sensitive(data, ["token", "password"])
    assert masked["token"] == "***"
    assert masked["Password"] == "***"
    assert masked["user"] == "admin"
