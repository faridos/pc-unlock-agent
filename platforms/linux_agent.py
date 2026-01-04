import logging
import threading
import time
import subprocess
from datetime import datetime

from common import send_unlock_event
from config import SEND_EVENT_START_HOUR, SEND_EVENT_END_HOUR

try:
    from pydbus import SessionBus
    from gi.repository import GLib
except ImportError:
    raise ImportError(
        "Required packages missing. Install via:\n"
        "sudo apt install python3-gi gir1.2-gtk-3.0\n"
        "pip install pydbus"
    )

window_event_sent = False


def is_within_time_window(): # by time
    now_time = datetime.now().time()  # <--- datetime.time object

    if SEND_EVENT_START_HOUR < SEND_EVENT_END_HOUR:
        # same-day window
        return SEND_EVENT_START_HOUR <= now_time < SEND_EVENT_END_HOUR
    else:
        # overnight window, e.g., 23:00 → 07:00
        return now_time >= SEND_EVENT_START_HOUR or now_time < SEND_EVENT_END_HOUR


def issss_session_active():
    """
    Wayland-safe check using loginctl
    """
    try:
        out = subprocess.check_output(
            ["loginctl", "show-session", "--property=Active", "--value"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return out == "yes"
    except Exception as e:
        logging.error(f"Session check failed: {e}")
        return False

def is_session_active():
    """
    Returns True if the current user session is active
    """
    try:
        import os
        session_id = os.environ.get("XDG_SESSION_ID")
        if not session_id:
            # fallback: pick first session for this user
            import getpass
            user = getpass.getuser()
            session_id = subprocess.check_output(
                ["loginctl", "list-sessions", "--no-legend"],
                text=True
            ).split()[0]  # first session
        out = subprocess.check_output(
            ["loginctl", "show-session", session_id, "--property=Active", "--value"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return out == "yes"
    except Exception as e:
        logging.error(f"Session check failed: {e}")
        return False



def window_monitor_loop():
    global window_event_sent

    logging.info("Time window monitor started")

    while True:
        in_window = is_within_time_window()

        if in_window and not window_event_sent and is_session_active():
            logging.info(
                "Time window entered while session already active. Sending unlock event."
            )
            send_unlock_event()
            window_event_sent = True

        if not in_window:
            window_event_sent = False

        time.sleep(60)


def run():
    """
    Linux agent for GNOME Wayland.
    Detects:
      - lock → unlock
      - entering time window while already unlocked
    """
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s'
    )

    logging.info("Linux unlock agent started (GNOME Wayland).")

    # Start window monitor thread
    threading.Thread(
        target=window_monitor_loop,
        daemon=True
    ).start()

    bus = SessionBus()

    try:
        screensaver = bus.get("org.gnome.ScreenSaver")
    except Exception as e:
        logging.error(f"Failed to connect to org.gnome.ScreenSaver DBus: {e}")
        return

    def handle_unlock(active):
        global window_event_sent
        print("active......", active)
        if not active:  # screen unlocked
            if is_within_time_window():
                logging.info("Unlock detected in time window. Sending event...")
                send_unlock_event()
                window_event_sent = True
            else:
                logging.info("Unlock detected outside  time window. Ignored.")
        else:
            logging.info("Screen locked.")

    try:
        screensaver.ActiveChanged.connect(handle_unlock)
    except AttributeError:
        try:
            screensaver.OnActiveChanged.connect(handle_unlock)
        except AttributeError as e:
            logging.error(f"Cannot connect to ActiveChanged signal: {e}")
            return

    logging.info("Listening for unlock events and time window entry...")
    GLib.MainLoop().run()
