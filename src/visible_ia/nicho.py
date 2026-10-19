"""Temporary alias: the niche vocabulary moved to `visible_ia.config.nichos` (reorganization
step 3). Removed in step 8."""

from visible_ia.config.nichos import NICHE_TOML, Niche, load_niche

__all__ = ["NICHE_TOML", "Niche", "load_niche"]
