# PyRDM — Personal Remote Desktop Manager

A lightweight cross-platform SSH + RDP connection manager built with Python and PyQt6.

## Features
- Organised connection list with groups
- SSH sessions embedded as tabs inside the app
- RDP sessions launched via FreeRDP (separate window)
- Passwords stored in OS native keychain (macOS Keychain / Windows Credential Manager / Linux libsecret)
- Search / filter connections
- Right-click context menu to edit or delete

## Requirements

### Python packages
```bash
pip install -r requirements.txt
```

### FreeRDP (for RDP connections only)
| Platform | Install command |
|----------|----------------|
| Linux (Debian/Ubuntu) | `sudo apt install freerdp2-x11` |
| macOS | `brew install freerdp` |
| Windows | Download from https://github.com/FreeRDP/FreeRDP/releases |

FreeRDP is **not** needed if you only use SSH connections.

## Running

```bash
python main.py
```

## Project structure

```
rdm-tool/
├── main.py                  # Entry point
├── requirements.txt
└── src/
    ├── database.py          # SQLite connection storage
    ├── credentials.py       # OS keychain wrapper
    ├── main_window.py       # Main application window
    ├── sidebar.py           # Connection tree sidebar
    ├── ssh_tab.py           # Embedded SSH terminal tab
    ├── rdp_launcher.py      # FreeRDP subprocess launcher
    └── connection_dialog.py # Add / edit connection dialog
```

## Data storage
- **Connections database**: `~/.pyrdm/connections.db` (SQLite)
- **Passwords**: OS native keychain — never stored in plain text

## Tips
- Double-click a connection to open it
- Right-click for edit / delete options
- Use the search box to quickly filter connections
- The `+` button adds a new connection; `⊞` adds a group
