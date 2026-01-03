# main.py

import platform
import sys

def main():
    system = platform.system().lower()

    if system == "windows":
        from platforms.windows_agent import run
    elif system == "darwin":
        from platforms.macos_agent import run
    elif system == "linux":
        print("i am here in linux")
        from platforms.linux_agent import run
    else:
        sys.exit("Unsupported OS")

    run()

if __name__ == "__main__":
    main()
