class TLError(Exception):
    """Base exception for expected ttr failures."""


class BackendError(TLError):
    """Raised when a translation backend cannot complete a request."""


class ClipboardError(TLError):
    """Raised when clipboard integration is unavailable or fails."""

