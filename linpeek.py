#!/usr/bin/env python3
import argparse
from rich.console import Console
from rich.panel import Panel
from rich import box

# Import updated modules (make sure these are refactored with Rich too)
from core.enumerator import check_suid, check_cron, check_docker, check_environment
from core.privesc import check_kernel_exploits, check_sudo_perms, check_writable_system_files
from core.creds import loot_proc, scan_history, find_ssh_keys
from core.persistence import install_backdoor, clean_logs
from exploits.suid_exploit import check_and_update_data


console = Console()


def banner():
    console.print(Panel.fit("""
     [bold cyan]LinPeek[/bold cyan] - [white]Linux Post-Exploitation Toolkit[/white]

    """, title="LinPeek", subtitle="By shellkraft", box=box.HEAVY))


def main():
    banner()

    parser = argparse.ArgumentParser(description="LinPeek - Linux Post-Exploitation Toolkit")
    parser.add_argument("--enum", help="Basic enumeration", action="store_true")
    parser.add_argument("--privesc", help="Privilege escalation checks", action="store_true")
    parser.add_argument("--creds", help="Credential harvesting", action="store_true")
    parser.add_argument("--persist", help="Install persistence mechanisms", action="store_true")

    args = parser.parse_args()

    if args.enum:
        check_and_update_data()
        check_suid()
        check_cron()
        check_docker()
        check_environment()

    if args.privesc:
        console.print(Panel("[bold green]Starting Privilege Escalation Checks[/bold green]", box=box.SQUARE))
        check_kernel_exploits()
        check_sudo_perms()
        check_writable_system_files()

    if args.creds:
        console.print(Panel("[bold green]Starting Credential Harvesting[/bold green]", box=box.SQUARE))
        loot_proc()
        scan_history()
        find_ssh_keys()

    if args.persist:
        console.print(Panel("[bold green]Starting Persistence Module[/bold green]", box=box.SQUARE))
        install_backdoor()
        clean_logs()


if __name__ == "__main__":
    main()
