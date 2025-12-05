# 🔥 Firewall Assistant for Windows

A smart, friendly GUI for controlling which apps can access the internet powered by the built-in Windows Firewall. Instead of dealing with ports, protocols, and cryptic firewall rules, Firewall Assistant gives you:

🚦 Per-app Allow / Block controls

📡 Profiles for Normal / Public Wi-Fi / Focus modes

🤔 “Why is this app not working?” explanations

⏳ 1-hour Temporary Allow

🔐 All powered by the official Windows Firewall (netsh)

> ⚠️ Important: This tool modifies Windows Firewall rules and must be run as Administrator.

## ✨ Features
- Per-Application Control
- Shows apps (name + full path) with recent network activity.
- Mark any app as Allowed or Blocked for the current profile.
- All rules are enforced using Windows Firewall (netsh advfirewall firewall).

## 📂 Profiles

- Switch between three simple profiles — each with its own rules:
- Normal — everyday usage
- Public Wi-Fi — stricter for untrusted networks
- Focus — blocks distracting apps
- One-click switching instantly reapplies firewall rules.

## ❓ “Why is this app not working?”

For any selected app, get clear diagnostics:

- Which profile is active
- Whether the app is effectively Allowed or Blocked
- Whether the rule is explicit or inherited from profile defaults
- If a Temporary Allow is active and when it expires

## ⏱ Temporary Allow (1 Hour)

Give a blocked app 60 minutes of temporary internet access without altering permanent rules.

## 📝 Activity Log

- Logs all profile changes, rule updates, and errors into logs/activity.log.
- Recent entries are shown directly in the UI.

## 🧰 Tech Stack

- OS: Windows 10 / 11
- Language: Python 3
- UI Framework: Tkinter
- Firewall Integration: netsh advfirewall
- Process Discovery: psutil
- Config & Data: JSON + dataclasses

## 📁 Project Structure
```text
firewall_assistant/
│
├─ main.py                      # GUI entry point
│
├─ firewall_assistant/
│  ├─ __init__.py
│  ├─ models.py                 # Dataclasses (AppInfo, AppRule, ProfileConfig, FullConfig)
│  ├─ config.py                 # Load/save config.json
│  ├─ firewall_win.py           # Windows Firewall wrapper (netsh)
│  ├─ discovery.py              # Detect apps with network activity
│  ├─ profiles.py               # Profiles, temp allow logic, explanations
│  ├─ activity_log.py           # Append/read logs/activity.log
│  └─ ui/
│     ├─ __init__.py
│     └─ main_window.py         # Tkinter-based UI
│
├─ config.json                  # Auto-created configuration
└─ logs/
   └─ activity.log              # Auto-created log file

```

---
##  🛠️ Installation
### 📋 Requirements
* *Windows 10* or *Windows 11*
* *Python 3.9+* (*3.10+* recommended)
* psutil Python package

---

### 🚀 Steps
```bash
git clone <REPO_URL>
cd <REPO_FOLDER>
python -m venv .venv
.venv\Scripts\activate
pip install psutil
```

> "Important: run commands from a terminal started with “Run as administrator” (right‑click on Command Prompt / PowerShell)."

### 🧩 Usage
From the project root, run:
```bash
python main.py
```

In the GUI
- ***Refresh Apps:*** Detect apps with current network activity and add them to the list.
- ***Allow Selected / Block Selected:*** Select one or more apps and update their status for the active profile.
- ***Profiles (top):*** Switch between **Normal**, **Public Wi-Fi**, and **Focus**. Firewall rules are updated each time you change profile.
- ***Why not working?:*** Select exactly one app → shows an explanation of why it’s allowed or blocked.
- ***Temp Allow 1h:*** For a blocked app → temporarily allow it for 60 minutes in the active profile.
- ***Activity Log (right side):*** View recent profile changes, rule changes, and errors logged by the app.
---

## 📄 License
[MIT License](LICENSE)
