"""Layer 1 · Configuration. `from visible_ia.config import get_settings` keeps working: the
settings moved to `ajustes.py` in step 3 of the reorganization (19/10/2026)."""

from visible_ia.config.ajustes import LATER, REQUIRED_PER_ENV, Env, Settings, get_settings

__all__ = ["LATER", "REQUIRED_PER_ENV", "Env", "Settings", "get_settings"]
