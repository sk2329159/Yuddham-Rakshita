# firewall_assistant/config.py

from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Dict

from .models import FullConfig, AppInfo, ProfileConfig, AppRule, Action, Direction

# Repo root (same style as activity_log.py)
ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config.json"


def _default_raw_config() -> Dict[str, Any]:
    """
    Default config structure as plain dict (matches JSON).
    """
    return {
        "version": 1,
        "active_profile": "normal",
        "apps": {},
        "profiles": {
            "normal": {
                "display_name": "Normal",
                "description": "Default profile for home/office use.",
                "default_action": "allow",
                "app_rules": {},
            },
            "public_wifi": {
                "display_name": "Public Wi-Fi",
                "description": "Stricter rules for public networks.",
                "default_action": "allow",
                "app_rules": {},
            },
            "focus": {
                "display_name": "Focus",
                "description": "Block distracting apps while working.",
                "default_action": "allow",
                "app_rules": {},
            },
        },
    }


def load_raw_config() -> Dict[str, Any]:
    """
    Load config.json and return as plain dict.
    If file does not exist, return a default structure (but do not write it).
    """
    if not CONFIG_PATH.exists():
        return _default_raw_config()

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except JSONDecodeError as e:
        raise ValueError(f"Config file is not valid JSON: {e}") from e


def save_raw_config(cfg: Dict[str, Any]) -> None:
    """
    Save the given dict to config.json (pretty-printed JSON).
    """
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, sort_keys=False)


def parse_full_config(raw: Dict[str, Any]) -> FullConfig:
    """
    Convert a raw dict (as loaded from JSON) into FullConfig & dataclasses.
    """
    version = int(raw.get("version", 1))
    active_profile = raw.get("active_profile", "normal")

    # --- Apps ---
    apps: Dict[str, AppInfo] = {}
    apps_raw: Dict[str, Any] = raw.get("apps", {}) or {}
    for exe_path, app_data in apps_raw.items():
        name = app_data.get("name") or Path(exe_path).name
        tags = list(app_data.get("tags", []))
        last_seen = app_data.get("last_seen")
        pinned = bool(app_data.get("pinned", False))

        apps[exe_path] = AppInfo(
            exe_path=exe_path,
            name=name,
            tags=tags,
            last_seen=last_seen,
            pinned=pinned,
        )

    # --- Profiles ---
    profiles: Dict[str, ProfileConfig] = {}
    profiles_raw: Dict[str, Any] = raw.get("profiles", {}) or {}

    if not profiles_raw:
        profiles_raw = _default_raw_config()["profiles"]

    def _normalize_action(value: str) -> Action:
        return "block" if value == "block" else "allow"

    def _normalize_direction(value: str) -> Direction:
        value = (value or "out").lower()
        if value in ("in", "out", "both"):
            return value  # type: ignore[return-value]
        return "out"      # type: ignore[return-value]

    for p_name, p_data in profiles_raw.items():
        display_name = p_data.get("display_name") or p_name.title()
        description = p_data.get("description", "")
        default_action = _normalize_action(p_data.get("default_action", "allow"))

        app_rules_raw: Dict[str, Any] = p_data.get("app_rules", {}) or {}
        app_rules: Dict[str, AppRule] = {}

        for exe_path, rule_data in app_rules_raw.items():
            action = _normalize_action(rule_data.get("action", "allow"))
            direction = _normalize_direction(rule_data.get("direction", "out"))
            temporary_until = rule_data.get("temporary_until")

            app_rules[exe_path] = AppRule(
                app_exe_path=exe_path,
                action=action,
                direction=direction,
                temporary_until=temporary_until,
            )

        profiles[p_name] = ProfileConfig(
            name=p_name,
            display_name=display_name,
            description=description,
            default_action=default_action,
            app_rules=app_rules,
        )

    # Ensure our 3 base profiles always exist
    defaults = _default_raw_config()["profiles"]
    for p_name in ("normal", "public_wifi", "focus"):
        if p_name not in profiles:
            p_data = defaults[p_name]
            profiles[p_name] = ProfileConfig(
                name=p_name,
                display_name=p_data["display_name"],
                description=p_data["description"],
                default_action=_normalize_action(p_data["default_action"]),
                app_rules={},
            )

    # Fix active_profile if invalid
    if active_profile not in profiles:
        active_profile = "normal"

    return FullConfig(
        version=version,
        active_profile=active_profile,
        apps=apps,
        profiles=profiles,
    )


def full_config_to_raw(cfg: FullConfig) -> Dict[str, Any]:
    """
    Convert FullConfig/dataclasses back into a plain dict ready for JSON dump.
    """
    apps_raw: Dict[str, Any] = {}
    for exe_path, app in cfg.apps.items():
        apps_raw[exe_path] = {
            "name": app.name,
            "tags": app.tags,
            "last_seen": app.last_seen,
            "pinned": app.pinned,
        }

    profiles_raw: Dict[str, Any] = {}
    for p_name, profile in cfg.profiles.items():
        app_rules_raw: Dict[str, Any] = {}
        for exe_path, rule in profile.app_rules.items():
            app_rules_raw[exe_path] = {
                "action": rule.action,
                "direction": rule.direction,
                "temporary_until": rule.temporary_until,
            }

        profiles_raw[p_name] = {
            "display_name": profile.display_name,
            "description": profile.description,
            "default_action": profile.default_action,
            "app_rules": app_rules_raw,
        }

    return {
        "version": cfg.version,
        "active_profile": cfg.active_profile,
        "apps": apps_raw,
        "profiles": profiles_raw,
    }


def load_config() -> FullConfig:
    """
    Convenience: load_raw_config + parse_full_config.
    On error, reset to default config on disk.
    """
    try:
        raw = load_raw_config()
        return parse_full_config(raw)
    except Exception as exc:
        print(f"[config] Error loading config; resetting to default: {exc}")
        return ensure_default_config()


def save_config(cfg: FullConfig) -> None:
    """
    Convenience: full_config_to_raw + save_raw_config.
    """
    raw = full_config_to_raw(cfg)
    save_raw_config(raw)


def ensure_default_config() -> FullConfig:
    """
    Create a default config.json on disk and return it as FullConfig.
    Useful if the file was missing or corrupted.
    """
    raw = _default_raw_config()
    save_raw_config(raw)
    return parse_full_config(raw)


if __name__ == "__main__":
    # Simple self-test
    cfg = load_config()
    print("Active profile:", cfg.active_profile)
    print("Profiles:", list(cfg.profiles.keys()))
    save_config(cfg)