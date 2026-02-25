# src/tabby/web/routes/__init__.py

"""
API route handlers.
"""

from . import health
from . import server_setting
from . import events
from . import models
from . import completion

__all__ = ["health", "server_setting", "events", "models", "completion"]