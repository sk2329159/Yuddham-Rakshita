# firewall_assistant/firewall_win.py

from __future__ import annotations
from typing import Optional
from .models import Action, Direction


def add_app_rule_in_windows_firewall(
    exe_path: str,
    action: Action,
    direction: Direction = "out",
    rule_name: Optional[str] = None,
) -> None:
    """
    Ensure there is a Windows Firewall rule for this exe_path and action.
    If rule_name is None, construct a consistent name, e.g. "FWAssist_BLOCK_<exe_name>".
    Uses 'netsh advfirewall' or PowerShell under the hood.
    """
    ...


def remove_app_rule_from_windows_firewall(
    exe_path: str,
    action: Optional[Action] = None,
    direction: Optional[Direction] = None,
    rule_name: Optional[str] = None,
) -> None:
    """
    Remove firewall rule(s) created by this assistant for the given exe_path.
    If action/direction/rule_name are None, remove all related rules.
    """
    ...


def sync_profile_to_windows_firewall(
    profile_name: str,
    cfg_path: Optional[str] = None,
) -> None:
    """
    High-level function:
    - Load config (or use cfg_path if provided).
    - For the given profile:
        * Apply app_rules to Windows Firewall.
        * Remove any stale rules previously set by other profiles.
    UI should call this after switching profiles.
    """
    ...