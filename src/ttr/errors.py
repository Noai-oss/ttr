class TTRError(Exception):
    """Base exception for expected ttr failures."""


class BackendError(TTRError):
    """Raised when a translation backend cannot complete a request."""


class CacheError(TTRError):
    """Raised when the local cache cannot be read or written."""


class ClipboardError(TTRError):
    """Raised when clipboard integration is unavailable or fails."""
