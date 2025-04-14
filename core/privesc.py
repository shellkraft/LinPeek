import os
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich import box
from time import time

console = Console()

def section(title):
    console.print(Panel(title, style="bold cyan", box=box.SQUARE))

def timed(func):
    def wrapper(*args, **kwargs):
        section(f"[🚀] {func.__name__.replace('_', ' ').title()}")
        start = time()
        result = func(*args, **kwargs)
        console.print(f"[green]✓ Completed in {time() - start:.2f}s[/green]\n")
        return result
    return wrapper


@timed
def check_kernel_exploits():
    """Offline kernel exploit suggester with real CVE checks"""
    kernel = subprocess.getoutput("uname -r")
    cve_db = {
            "3.13.0": ["CVE-2015-1328", "OverlayFS PrivEsc", "https://www.exploit-db.com/exploits/37292"],
            "4.4.0": ["CVE-2016-5195", "DirtyCow", "https://dirtycow.ninja/"],
            "4.9.0": ["CVE-2017-6074", "DCCP Double-Free", "https://www.exploit-db.com/exploits/41458"],
            "5.8.0": ["CVE-2021-3493", "OverlayFS (Ubuntu)", "https://github.com/briskets/CVE-2021-3493"],
            "5.13.0": ["CVE-2022-0847", "DirtyPipe", "https://dirtypipe.cm4all.com/"],
            "5.15.0": ["CVE-2022-2588", "NFT Privilege Escalation", "https://github.com/veritas501/CVE-2022-2588"]
        }

    matched = False
    for version, details in cve_db.items():
        if version in kernel:
            console.print(f"[red][!] Vulnerable Kernel ({kernel}): {details[0]} - {details[1]}[/red]")
            console.print(f"    Exploit: [cyan]{details[2]}[/cyan]")
            matched = True

    if not matched:
        console.print("[magenta]No known kernel vulnerabilities detected in local version.[/magenta]")


@timed
def check_sudo_perms():
    """Check sudo permissions for current user"""
    console.print("[cyan]Checking sudo permissions for current user...[/cyan]")
    sudo_perms = subprocess.getoutput("sudo -l 2>/dev/null")
    if "not allowed" not in sudo_perms and "may not run" not in sudo_perms:
        console.print(f"[yellow][!] Current user can run sudo commands:[/yellow]\n{sudo_perms}")
    else:
        console.print("[magenta]No sudo permissions found.[/magenta]")


@timed
def check_writable_system_files():
    """Find writable system files critical for privesc"""
    targets = [
        "/etc/passwd",
        "/etc/shadow",
        "/etc/sudoers",
        "/etc/cron.d/",
        "/etc/crontab",
        "/etc/cron.hourly/",
        "/etc/cron.daily/",
        "/etc/cron.weekly/",
        "/etc/cron.monthly/",
        "/etc/init.d/",
        "/etc/systemd/system/",
        "/var/spool/cron/",
        "/var/spool/cron/crontabs/"
    ]

    found = False
    for target in targets:
        try:
            if os.path.exists(target):
                if os.access(target, os.W_OK):
                    console.print(f"[!] Writable: {target}")
                    found = True
                # Check if parent directory is writable
                elif os.access(os.path.dirname(target), os.W_OK):
                    console.print(f"[!] Parent directory writable: {os.path.dirname(target)}")
                    found = True
        except Exception as e:
            console.print(f"[!] Error checking {target}: {e}")
    
    if not found:
        console.print("[-] No critical writable system files found")
