from datetime import datetime

def log(msg, level="info"):
    colors = {
        "info": "\033[94m",
        "warning": "\033[93m",
        "critical": "\033[91m",
        "reset": "\033[0m"
    }
    print(f"{colors[level]}[{datetime.now()}] {msg}{colors['reset']}")