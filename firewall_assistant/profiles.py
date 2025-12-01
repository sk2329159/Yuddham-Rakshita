from __future__ import annotations

from .models import FullConfig, ProfileConfig, Action, AppRule
from .config import load_config, save_config
from .firewall_win import sync_profile_to_windows_firewall


def get_active_profile(cfg: FullConfig) -> ProfileConfig:
    """
    Return the currently active ProfileConfig from FullConfig.
    If cfg.active_profile is invalid, try to repair it.
    """
    if cfg.active_profile in cfg.profiles:
        return cfg.profiles[cfg.active_profile]

    # Try to repair
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

    UI should call this when user selects a profile.
    """
    cfg = load_config()

    if profile_name not in cfg.profiles:
        raise ValueError(f"Profile '{profile_name}' not found")

    cfg.active_profile = profile_name
    save_config(cfg)

    # Now actually enforce the profile in Windows Firewall
    sync_profile_to_windows_firewall(profile_name)


def set_app_action_in_profile(
    cfg: FullConfig,
    profile_name: str,
    exe_path: str,
    action: Action,
) -> None:
    """
    In the given profile, set app_rules[exe_path].action = action.
    If rule does not exist, create it. Caller should then save_config() and
    (optionally) apply_profile(cfg.active_profile) to sync to Windows Firewall.
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
        # When user explicitly changes action, clear any temporary timer
        rule.temporary_until = None


if __name__ == "__main__":
    # Quick manual test (non-firewall part)
    cfg = load_config()
    print("Before:", cfg.active_profile)
    set_app_action_in_profile(cfg, "focus", r"C:\Test\game.exe", "block")
    save_config(cfg)
    apply_profile("focus")  # will actually call netsh; run as admin if you try this
    print("After:", load_config().active_profile)