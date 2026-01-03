# platforms/windows_agent.py

import win32con
import win32gui
import win32ts
from common import send_unlock_event

class SessionMonitor:
    def __init__(self):
        message_map = {
            win32con.WM_WTSSESSION_CHANGE: self.on_session_change,
        }

        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = message_map
        wc.lpszClassName = "PCUnlockAgent"

        self.class_atom = win32gui.RegisterClass(wc)
        self.hwnd = win32gui.CreateWindow(
            self.class_atom,
            "PC Unlock Agent",
            0,
            0, 0, 0, 0,
            0, 0, 0, None
        )

        win32ts.WTSRegisterSessionNotification(
            self.hwnd,
            win32ts.NOTIFY_FOR_THIS_SESSION
        )

    def on_session_change(self, hwnd, msg, wparam, lparam):
        if wparam == win32ts.WTS_SESSION_UNLOCK:
            send_unlock_event()

def run():
    SessionMonitor()
    win32gui.PumpMessages()
