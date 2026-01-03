# PC Unlock Agent (Python)

Minimal background agent that detects PC unlock events and sends them to n8n.

## Supported OS
- Windows (reliable)
- macOS (requires Accessibility permission)
- Linux (systemd only)

## Run
python main.py

## Event sent
event: pc_unlocked
