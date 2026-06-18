"""LeaseClear backend — residential lease Q&A with citations."""

__version__ = "0.1.0"


def health() -> dict[str, str]:
    """Return a typed health payload for smoke tests and future /health endpoint."""
    return {"status": "ok"}
