# common.py

import requests
import socket
import platform
import datetime
from config import (
    N8N_WEBHOOK_URL,
    EVENT_NAME,
    DEVICE_TYPE,
    REQUEST_TIMEOUT
)

def send_unlock_event():
    payload = {
        "event_type": EVENT_NAME,
        "device": DEVICE_TYPE,
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }

    try:
        requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )
    except Exception:
        # MVP: silent failure (no crash, no retries)
        pass
