# platforms/macos_agent.py

from AppKit import NSWorkspace
from Foundation import NSObject
from PyObjCTools import AppHelper
from common import send_unlock_event

class WorkspaceObserver(NSObject):
    def sessionDidBecomeActive_(self, notification):
        send_unlock_event()

def run():
    workspace = NSWorkspace.sharedWorkspace()
    observer = WorkspaceObserver.alloc().init()

    nc = workspace.notificationCenter()
    nc.addObserver_selector_name_object_(
        observer,
        "sessionDidBecomeActive:",
        "NSWorkspaceSessionDidBecomeActiveNotification",
        None
    )

    AppHelper.runConsoleEventLoop()
