# firewall_assistant/profiles.py

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .models import FullConfig, ProfileConfig, Action, AppRule
from .config import load_config, save_config
from .firewall_win import sync_profile_to_windows_firewall
from .activity_log import log_event


def get_active_profile(cfg: FullConfig) -> ProfileConfig:
    """
    Return the currently active ProfileConfig from FullConfig.
    If cfg.active_profile is invalid, try to repair it.
    """
    if cfg.active_profile in cfg.profiles:
        return cfg.profiles[cfg.active_profile]

    # Attempt to repair
    if "normal" in cfg.profiles:
        cfg.active_profile = "normal"
    elif cfg.profiles:
        cfg.active_profile = next(iter(cfg.profiles))
    else:
        raise RuntimeError("No profiles available in config")

    save_config(cfg)
    return cfg.profiles[cfg.active_profile]


def set_active_profile(cfg: FullConfig, profile_name: str) -> None:
    """
    Set cfg.active_profile to profile_name and persist config.
    Does NOT itself call Windows Firewall; caller can decide when to sync.
    """
    if profile_name not in cfg.profiles:
        raise ValueError(f"Profile '{profile_name}' not found")

    cfg.active_profile = profile_name
    save_config(cfg)
    log_event(
        "ACTIVE_PROFILE_CHANGED",
        f"Active profile changed to '{profile_name}'",
        {"profile": profile_name},
    )


def apply_profile(profile_name: str) -> None:
    """
    High-level: load config, set active_profile, save config,
    and call sync_profile_to_windows_firewall(profile_name).

    UI or CLI should call this when the user selects a profile.
    """
    cfg = load_config()

    if profile_name not in cfg.profiles:
        raise ValueError(f"Profile '{profile_name}' not found")

    cfg.active_profile = profile_name
    save_config(cfg)

    log_event(
        "PROFILE_APPLIED",
        f"Profile '{profile_name}' applied",
        {"profile": profile_name},
    )

    # Enforce the profile via Windows Firewall
    sync_profile_to_windows_firewall(profile_name)


def set_app_action_in_profile(
    cfg: FullConfig,
    profile_name: str,
    exe_path: str,
    action: Action,
) -> None:
    """
    In the given profile, set app_rules[exe_path].action = action.
    If rule does not exist, create it with default direction='out'.

    Caller should then save_config(cfg) and (optionally) apply_profile(cfg.active_profile)
    to sync changes to Windows Firewall.
    """
    if profile_name not in cfg.profiles:
        raise ValueError(f"Profile '{profile_name}' not found")

    exe_path_resolved = str(Path(exe_path).resolve())
    profile = cfg.profiles[profile_name]

    rule = profile.app_rules.get(exe_path_resolved)
    if rule is None:
        rule = AppRule(
            app_exe_path=exe_path_resolved,
            action=action,
            direction="out",
            temporary_until=None,
        )
        profile.app_rules[exe_path_resolved] = rule
        change_type = "created"
    else:
        rule.action = action
        rule.temporary_until = None  # clear temporary when user sets explicitly
        change_type = "updated"

    log_event(
        "PROFILE_APP_RULE_CHANGED",
        f"Rule {change_type}: {action.upper()} {exe_path_resolved} in profile '{profile_name}'",
        {
            "profile": profile_name,
            "exe_path": exe_path_resolved,
            "action": action,
            "change_type": change_type,
        },
    )


# ---------------------------------------------------------------------------
# "Why is this app not working?" backend helper
# ---------------------------------------------------------------------------

def explain_app_in_active_profile(exe_path: str) -> Dict[str, Any]:
    """
    Explain how the currently active profile treats the given exe_path.

    Returns a dict with keys:
      - exe_path
      - profile
      - profile_display_name
      - action           ("allow" or "block")
      - direction        ("in", "out", "both") – if explicit rule, else "out"
      - temporary_until  (str or None)
      - reason           (human-readable explanation)

    This is meant to be used by the UI when the user asks:
      "Why is this app not working?"
    """
    cfg = load_config()
    profile = get_active_profile(cfg)
    exe_path_resolved = str(Path(exe_path).resolve())

    explicit_rule = profile.app_rules.get(exe_path_resolved)

    if explicit_rule:
        explanation = {
            "exe_path": exe_path_resolved,
            "profile": profile.name,
            "profile_display_name": profile.display_name,
            "action": explicit_rule.action,
            "direction": explicit_rule.direction,
            "temporary_until": explicit_rule.temporary_until,
            "reason": (
                f"Explicit rule in profile '{profile.display_name}': "
                f"{explicit_rule.action.upper()} ({explicit_rule.direction})"
            ),
        }
    else:
        explanation = {
            "exe_path": exe_path_resolved,
            "profile": profile.name,
            "profile_display_name": profile.display_name,
            "action": profile.default_action,
            "direction": "out",
            "temporary_until": None,
            "reason": (
                f"No explicit rule in profile '{profile.display_name}'. "
                f"Using default_action='{profile.default_action}'."
            ),
        }

    # Log that someone asked for an explanation
    log_event(
        "APP_STATUS_EXPLAINED",
        f"Explained status for {exe_path_resolved} in profile '{profile.name}'",
        explanation,
    )

    return explanation


# ---------------------------------------------------------------------------
# Simple CLI for debug / manual testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Profile management / explanation test CLI (Member 1, Week 3)."
    )
    parser.add_argument(
        "profile",
        nargs="?",
        help="Profile name to apply (e.g. normal, public_wifi, focus). "
             "If omitted, no profile is changed.",
    )
    parser.add_argument(
        "--explain",
        metavar="EXE_PATH",
        help="Explain how the active profile treats this executable.",
    )
    args = parser.parse_args()

    cfg = load_config()
    print("Existing profiles:", ", ".join(cfg.profiles.keys()))
    print("Active profile before:", cfg.active_profile)

    if args.profile:
        apply_profile(args.profile)
        cfg2 = load_config()
        print("Active profile after:", cfg2.active_profile)

    if args.explain:
        info = explain_app_in_active_profile(args.explain)
        print("\nExplanation:")
        for k, v in info.items():
            print(f"  {k}: {v}")