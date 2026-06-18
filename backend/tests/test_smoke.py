from leaseclear import __version__, health


def test_version_is_set() -> None:
    assert __version__ == "0.1.0"


def test_health() -> None:
    assert health() == {"status": "ok"}
