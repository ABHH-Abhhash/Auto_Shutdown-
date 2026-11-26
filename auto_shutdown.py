"""
Auto Shutdown v2.0 - AI-Powered Idle Computer Shutdown
------------------------------------------------------
Monitors user inactivity and automatically shuts down the computer
after 5 minutes of no mouse/keyboard activity.

Run directly:              python auto_shutdown.py
Run with custom timeout:   python auto_shutdown.py --timeout 600
Show help:                 python auto_shutdown.py --help
Compile to EXE:            pyinstaller --onefile --noconsole auto_shutdown.py

Deployment for 40 PCs: See deploy_to_40_pcs.md
"""

import ctypes
import os
import sys
import time
import argparse
import logging
from datetime import datetime, timedelta

# ─── Windows API Structure for GetLastInputInfo ───
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("dwTime", ctypes.c_uint),
    ]


# ─── Logging Setup ───
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auto_shutdown.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("AutoShutdown")


# ─── Idle Detection ───
def get_idle_seconds():
    """
    Returns how many seconds the computer has been completely idle
    (no mouse movement or keyboard input).
    Uses Windows GetLastInputInfo API.
    """
    try:
        last_input_info = LASTINPUTINFO()
        last_input_info.cbSize = ctypes.sizeof(LASTINPUTINFO)

        result = ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input_info))
        if result == 0:
            logger.error("GetLastInputInfo API call failed.")
            return 0

        millis = ctypes.windll.kernel32.GetTickCount() - last_input_info.dwTime
        idle_seconds = millis / 1000.0
        return idle_seconds
    except Exception as e:
        logger.error(f"Error getting idle time: {e}")
        return 0


# ─── Shutdown Function ───
def shutdown_computer(timeout_seconds=30, message="Computer idle too long. Shutting down..."):
    """
    Initiates Windows shutdown with a countdown.
    Uses Windows' built-in shutdown.exe for reliability.
    """
    logger.warning(f"IDLE LIMIT REACHED! Initiating shutdown in {timeout_seconds} seconds...")
    logger.warning(f"Shutdown message: {message}")

    # /s = shutdown, /f = force close apps, /t = timeout, /c = comment
    shutdown_cmd = (
        f'shutdown /s /f /t {timeout_seconds} /c "{message}"'
    )
    logger.info(f"Executing: {shutdown_cmd}")
    os.system(shutdown_cmd)

    # Also log to a visible file so the user can check why it shut down
    try:
        with open("SHUTDOWN_REASON.txt", "w") as f:
            f.write(f"Auto Shutdown triggered at: {datetime.now()}\n")
            f.write(f"Reason: {message}\n")
            f.write("To prevent this: move mouse or press a key.\n")
    except:
        pass

    logger.info("Shutdown command issued. Goodbye!")
    sys.exit(0)


# ─── Abort Listener (optional) ───
def listen_for_abort(stop_event, abort_key='q'):
    """
    Background thread: if user presses 'q' + Enter, aborts the shutdown.
    Since shutdown.exe has its own /t countdown, this gives a chance to cancel.
    """
    import threading
    def _listen():
        try:
            inp = input().strip().lower()
            if inp == abort_key:
                logger.info("🛑 ABORT requested by user! Cancelling shutdown...")
                os.system("shutdown /a")
                logger.info("Shutdown aborted. Program will exit.")
                os._exit(0)
        except:
            pass
    t = threading.Thread(target=_listen, daemon=True)
    t.start()


# ─── Main ───
def main():
    # ── Parse Arguments ──
    parser = argparse.ArgumentParser(
        description="Auto Shutdown - Shuts down PC after idle timeout",
        epilog="Supports: Python script, compiled EXE, Windows Task Scheduler"
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=300,
        help="Idle timeout in seconds (default: 300 = 5 minutes)"
    )
    parser.add_argument(
        "--check-interval", "-c",
        type=int,
        default=5,
        help="How often to check idle status in seconds (default: 5)"
    )
    parser.add_argument(
        "--shutdown-delay", "-d",
        type=int,
        default=30,
        help="Countdown shown to user before shutdown (default: 30)"
    )
    parser.add_argument(
        "--message", "-m",
        type=str,
        default="Computer idle for 5 minutes. Auto-shutdown initiated.",
        help="Custom message shown during shutdown countdown"
    )
    parser.add_argument(
        "--no-abort", "-na",
        action="store_true",
        help="Disable the abort option (type 'q' to cancel shutdown)"
    )
    args = parser.parse_args()

    # ── Banner ──
    print("=" * 60)
    print("  🔒 AUTO SHUTDOWN v2.0")
    print("  Monitors idle time and shuts down when inactive")
    print("=" * 60)
    print(f"  Idle Limit:     {args.timeout} seconds ({args.timeout//60} min)")
    print(f"  Check Interval: {args.check_interval} seconds")
    print(f"  Shutdown Delay: {args.shutdown_delay} seconds")
    print(f"  Abort Allowed:  {'No' if args.no_abort else 'Yes (type \"q\" + Enter)'}")
    print(f"  Log File:       {LOG_FILE}")
    print("=" * 60)
    print("  🔄 Monitoring started... Move your mouse or press a key to reset.")
    print()

    # ── Check for Admin (for /f force shutdown) ──
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            logger.warning("⚠️  Not running as Administrator. Force shutdown may fail.")
            logger.warning("   Recommended: Right-click → Run as Administrator")
    except:
        pass

    # ── Start Abort Listener ──
    if not args.no_abort:
        logger.info("Abort listener active. Type 'q' + Enter to cancel shutdown.")
        listen_for_abort(None)

    # ── Countdown display variables ──
    next_warning_time = args.timeout - 60  # Warn at 1 minute before shutdown
    warned = False

    # ── Main Loop ──
    try:
        while True:
            idle_time = get_idle_seconds()

            # ── Show current status periodically ──
            remaining = max(0, args.timeout - idle_time)
            status = f"Idle: {idle_time:.0f}s / {args.timeout}s | Remaining: {remaining:.0f}s"
            print(f"\r  {status}", end="", flush=True)

            # ── Warning at 1 minute left ──
            if idle_time >= next_warning_time and not warned:
                print()  # new line
                logger.warning(f"⚠️  Warning: Shutdown in {args.shutdown_delay + 60} seconds unless activity detected!")
                warned = True

            # ── Reset warning if activity detected ──
            if idle_time < next_warning_time:
                warned = False

            # ── SHUTDOWN Condition ──
            if idle_time >= args.timeout:
                print()  # new line
                shutdown_computer(
                    timeout_seconds=args.shutdown_delay,
                    message=args.message
                )
                break

            time.sleep(args.check_interval)

    except KeyboardInterrupt:
        print("\n")
        logger.info("👋 User interrupted. Exiting gracefully.")
        logger.info("To run at startup: place this EXE in Windows Startup folder.")
        sys.exit(0)


if __name__ == "__main__":
    main()

