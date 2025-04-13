import os
import subprocess
from lib.logger import log

def check_suid():
    """Find exploitable SUID binaries"""
    log("Checking SUID binaries...", "info")
    suid_binaries = subprocess.getoutput("find / -perm -4000 2>/dev/null").split('\n')
    for binary in suid_binaries:
        if binary:  # Check if exploitable (simplified)
            log(f"Found SUID: {binary}", "warning")

def check_cron():
    """Find writable cron jobs"""
    log("Checking cron jobs...", "info")
    cron_paths = ["/etc/crontab", "/etc/cron.d/", "/var/spool/cron/"]
    for path in cron_paths:
        if os.path.exists(path):
            if os.access(path, os.W_OK):
                log(f"Writable cron: {path}", "critical")

def check_docker():
    """Detect Docker misconfigurations"""
    if "docker" in subprocess.getoutput("cat /proc/self/cgroup"):
        log("Inside Docker container!", "info")
        if os.path.exists("/var/run/docker.sock"):
            log("Docker socket exposed! (Privilege escalation possible)", "critical")