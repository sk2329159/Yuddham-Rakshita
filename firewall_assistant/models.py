from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional


Action = Literal["allow", "block"]
Direction = Literal["in", "out", "both"]


@dataclass
class AppInfo:
    exe_path: str
    name: str
    tags: List[str] = field(default_factory=list)
    last_seen: Optional[str] = None  # ISO timestamp or None
    pinned: bool = False


@dataclass
class AppRule:
    app_exe_path: str
    action: Action
    direction: Direction = "out"
    temporary_until: Optional[str] = None  # ISO timestamp or None


@dataclass
class ProfileConfig:
    name: str                     # internal id, e.g. "normal"
    display_name: str             # user-facing, e.g. "Normal"
    description: str
    default_action: Action        # how to treat unknown apps (conceptual for now)
    app_rules: Dict[str, AppRule] = field(default_factory=dict)  # key: exe_path


@dataclass
class FullConfig:
    version: int = 1
    active_profile: str = "normal"
    apps: Dict[str, AppInfo] = field(default_factory=dict)           # key: exe_path
    profiles: Dict[str, ProfileConfig] = field(default_factory=dict) # key: profile name