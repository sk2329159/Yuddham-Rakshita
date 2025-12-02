# firewall_assistant/models.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional

Action = Literal["allow", "block"]
Direction = Literal["in", "out", "both"]


@dataclass
class AppInfo:
    """
    Basic information about an application executable, stored in config.
    Keyed by exe_path in FullConfig.apps.
    """
    exe_path: str
    name: str
    tags: List[str] = field(default_factory=list)
    last_seen: Optional[str] = None  # ISO timestamp or None
    pinned: bool = False


@dataclass
class AppRule:
    """
    Per-profile rule for a specific app (by exe_path).
    """
    app_exe_path: str
    action: Action          # "allow" or "block"
    direction: Direction = "out"
    temporary_until: Optional[str] = None  # ISO timestamp or None (for future use)


@dataclass
class ProfileConfig:
    """
    A logical profile (Normal, Public Wi-Fi, Focus, etc.).
    """
    name: str                        # internal id, e.g. "normal"
    display_name: str                # user-facing e.g. "Normal"
    description: str
    default_action: Action           # conceptual default for unknown apps
    app_rules: Dict[str, AppRule] = field(default_factory=dict)  # key: exe_path


@dataclass
class FullConfig:
    """
    Top-level configuration object representing config.json.
    """
    version: int = 1
    active_profile: str = "normal"
    apps: Dict[str, AppInfo] = field(default_factory=dict)           # key: exe_path
    profiles: Dict[str, ProfileConfig] = field(default_factory=dict) # key: profile name