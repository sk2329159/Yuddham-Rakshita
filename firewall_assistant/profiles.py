# firewall_assistant/profiles.py

from __future__ import annotations

from .models import FullConfig, ProfileConfig, Action, AppRule
from .config import load_config, save_config
from .firewall_win import block_app, allow_app, sync_profile_to_windows_firewall


def get_active_profile(cfg: FullConfig) -> ProfileConfig:
    """
    Return the currently active ProfileConfig from FullConfig.
    If cfg.active_profile is invalid, try to repair it to 'normal' or
    the first available profile.
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

    # Enforce the profile via Windows Firewall (implemented in firewall_win)
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

    profile = cfg.profiles[profile_name]

    rule = profile.app_rules.get(exe_path)
    if rule is None:
        rule = AppRule(
            app_exe_path=exe_path,
            action=action,
            direction="out",
            temporary_until=None,
        )
        profile.app_rules[exe_path] = rule
    else:
        rule.action = action
        rule.temporary_until = None  # clear temporary flag when user sets explicitly


if __name__ == "__main__":
    # Simple CLI to test profile application
    import argparse
    parser = argparse.ArgumentParser(
        description="Profile management test CLI (Member 1, Week 2)."
    )
    parser.add_argument(
        "profile",
        nargs="?",
        help="Profile name to apply (e.g. normal, public_wifi, focus)",
    )
    args = parser.parse_args()

    cfg = load_config()
    print("Existing profiles:", ", ".join(cfg.profiles.keys()))
    print("Active profile before:", cfg.active_profile)

    if args.profile:
        apply_profile(args.profile)
        cfg2 = load_config()
        print("Active profile after:", cfg2.active_profile)
    else:
        print("No profile name given; not changing anything.")