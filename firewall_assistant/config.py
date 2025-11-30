# firewall_assistant/config.py

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
from .models import FullConfig, AppInfo, ProfileConfig, AppRule

CONFIG_PATH = Path("config.json")


def load_raw_config() -> Dict[str, Any]:
    """
    Load config.json and return as plain dict.
    If file does not exist, return a default structure.
    """
    ...


def save_raw_config(cfg: Dict[str, Any]) -> None:
    """
    Save the given dict to config.json (pretty-printed JSON).
    """
    ...


def parse_full_config(raw: Dict[str, Any]) -> FullConfig:
    """
    Convert a raw dict (as loaded from JSON) into FullConfig & dataclasses.
    """
    ...


def full_config_to_raw(cfg: FullConfig) -> Dict[str, Any]:
    """
    Convert FullConfig/dataclasses back into a plain dict ready for JSON dump.
    """
    ...


def load_config() -> FullConfig:
    """
    Convenience: load_raw_config + parse_full_config.
    """
    ...


def save_config(cfg: FullConfig) -> None:
    """
    Convenience: full_config_to_raw + save_raw_config.
    """
    ```
    ...


def ensure_default_config() -> FullConfig:
    """
    If config.json missing or invalid, create a default config with
    'normal', 'public_wifi', and 'focus' profiles and no app-specific rules.
    """
    ...