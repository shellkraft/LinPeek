import os
import re
from lib.logger import log

def loot_proc():
    """Extract credentials from /proc"""
    for root, _, files in os.walk("/proc"):
        if "environ" in files:
            path = os.path.join(root, "environ")
            try:
                with open(path, "rb") as f:
                    data = f.read().decode(errors="ignore")
                    if "PASS" in data or "SECRET" in data:
                        log(f"Found secrets in {path}", "critical")
            except: pass

def scan_history_files():
    """Check shell history for passwords"""
    history_files = [
        "~/.bash_history",
        "~/.zsh_history",
        "~/.mysql_history"
    ]
    for file in history_files:
        file = os.path.expanduser(file)
        if os.path.exists(file):
            log(f"Checking {file}...", "info")