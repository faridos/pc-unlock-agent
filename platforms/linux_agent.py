# platforms/linux_agent.py

import logging
from common import send_unlock_event
from config import SEND_EVENT_START_HOUR, SEND_EVENT_END_HOUR
from datetime import datetime

def is_within_time_window():
    if SEND_EVENT_START_HOUR is None or SEND_EVENT_END_HOUR is None:
        return True  # no restriction

    now_hour = datetime.now().hour

    if SEND_EVENT_START_HOUR < SEND_EVENT_END_HOUR:
        # e.g., 09:00 → 17:00
        return SEND_EVENT_START_HOUR <= now_hour < SEND_EVENT_END_HOUR
    else:
        # e.g., 23:00 → 07:00 (overnight)
        return now_hour >= SEND_EVENT_START_HOUR or now_hour < SEND_EVENT_END_HOUR

try:
    from pydbus import SessionBus
    from gi.repository import GLib
except ImportError:
    raise ImportError(
        "Required packages missing. Install via:\n"
        "sudo apt install python3-gi gir1.2-gtk-3.0\n"
        "pip install pydbus"
    )

def run():
    """
    Linux agent for GNOME Wayland.
    Listens to ScreenSaver DBus signals and triggers unlock events.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s'
    )

    logging.info("Linux unlock agent started (GNOME Wayland).")

    bus = SessionBus()

    try:
        screensaver = bus.get("org.gnome.ScreenSaver")
    except Exception as e:
        logging.error(f"Failed to connect to org.gnome.ScreenSaver DBus: {e}")
        return

    def handle_unlock(active):
        if not active:  # screen unlocked
            if is_within_time_window():
                logging.info("Unlock detected in allowed time window. Sending event...")
                send_unlock_event()
            else:
                logging.info("Unlock detected outside allowed time window. Ignored.")
        else:
            logging.info("Screen locked.")



    # Connect signal (GNOME exposes 'ActiveChanged' or 'OnActiveChanged')
    try:
        screensaver.ActiveChanged.connect(handle_unlock)
    except AttributeError:
        try:
            screensaver.OnActiveChanged.connect(handle_unlock)
        except AttributeError as e:
            logging.error(f"Cannot connect to ActiveChanged signal: {e}")
            return

    logging.info("Listening for unlock events...")
    loop = GLib.MainLoop()
    loop.run()
