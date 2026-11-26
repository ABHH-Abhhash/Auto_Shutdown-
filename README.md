⚡ PowerGuard — Smart Auto Shutdown

🐍 PowerGuard is a Python-based Windows utility that automatically shuts down your PC after a specified period of inactivity to help save power and improve efficiency. It monitors mouse and keyboard activity, provides real-time idle status, supports customizable shutdown timers, and includes a shutdown countdown with a cancellation option.

✨ Features

- 🖥️ Mouse and keyboard inactivity detection
- ⏱️ Custom idle timeout and check interval
- ⏳ Configurable shutdown countdown
- 🛑 Cancel shutdown by typing "q"
- 📝 Activity and shutdown logging
- 💬 Custom shutdown message
- 🔧 Command-line options
- 📦 Support for standalone EXE compilation

🛠️ Built With

🐍 Python • 🪟 Windows API • ⚙️ Windows Shutdown Utility

🚀 Usage

python auto_shutdown.py

Custom idle timeout:

python auto_shutdown.py --timeout 600

View help:

python auto_shutdown.py --help

📂 Project Structure

PowerGuard/
├── auto_shutdown.py
├── README.md
├── auto_shutdown.log
└── SHUTDOWN_REASON.txt

⚠️ Requirements

🪟 Windows OS • 🐍 Python 3 • Administrator privileges recommended.

Note: The program can force-close applications during shutdown. Save your work before running.

PowerGuard — Save Power. Stay Smart.
