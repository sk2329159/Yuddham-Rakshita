# firewall_assistant/discovery.py

from __future__ import annotations
from typing import List
from .models import AppInfo


def discover_active_apps() -> List[AppInfo]:
    """
    Return a list of AppInfo for apps that currently have network activity
    (or had very recent activity).

    Implementation options:
      - Use psutil to get connections per process.
      - OR call an external C++ helper that prints JSON and parse it.
    """
    ...


def merge_discovered_apps_into_config(cfg) -> None:
    """
    Take FullConfig, run discover_active_apps(), and:
      - Add any new exe_path to cfg.apps with basic info.
      - Update last_seen for known apps.
    Does NOT save to disk; caller must call save_config().
    """
    ...