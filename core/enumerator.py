from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from time import time
import os
import subprocess
import concurrent.futures
from exploits.suid_exploit import exploit_suid
from exploits.suid_exploit import SUID_REPORT_FILE


console = Console()


def section(title):
    console.print(Panel(title, style="bold cyan", box=box.DOUBLE))


def timed(func):
    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        elapsed = time() - start
        console.print(f"[green]✓ Completed in {elapsed:.2f} seconds[/green]\n")
        return result
    return wrapper


def find_suid_in_path(path):
    try:
        cmd = f"find {path} -type f -perm -4000 2>/dev/null"
        return subprocess.getoutput(cmd).split('\n')
    except:
        return []


@timed
def check_suid():
    section("[🔍] Scanning for SUID Binaries")
    suid_binaries = []
    found_exploitable = False

    # Clear previous report
    if os.path.exists(SUID_REPORT_FILE):
        os.remove(SUID_REPORT_FILE)

    paths = ["/usr/bin", "/usr/sbin", "/bin", "/sbin", "/usr/local/bin"]
    with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:
        task = progress.add_task("Checking paths for SUID files...", total=None)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(find_suid_in_path, p) for p in paths]
            for future in concurrent.futures.as_completed(futures):
                suid_binaries.extend(future.result())

        progress.update(task, description="SUID check complete!")

    # Process results
    suid_binaries = [b for b in suid_binaries if b]
    for binary in suid_binaries:
        exploitable, findings = exploit_suid(binary)
        if exploitable:
            found_exploitable = True
        console.print(f"[yellow][SUID][/yellow] {binary}{findings}")

    # Final reporting
    if os.path.exists(SUID_REPORT_FILE):
        abs_path = os.path.abspath(SUID_REPORT_FILE)
        console.print(f"\n[bold green]✓ Saved exploit suggestions to: {abs_path}[/bold green]")
    elif not found_exploitable:
        console.print("\n[bold magenta]No exploitable SUID binaries found.[/bold magenta]")
    else:
        console.print("\n[red]Error: Found exploitable binaries but couldn't save report![/red]")


@timed
def check_cron():
    section("[🕒] Checking Cron Jobs")
    # User-level crontab
    user_cron = subprocess.getoutput("crontab -l 2>/dev/null")
    if user_cron:
        console.print("[cyan]User Crontab:[/cyan]")
        console.print(user_cron)
    else:
        console.print("[bold magenta]No user crontab found.[/bold magenta]")

    # System cron (only if root)
    if os.getuid() == 0:
        system_cron = subprocess.getoutput("ls -la /etc/cron* /var/spool/cron 2>/dev/null")
        if system_cron:
            console.print("[cyan]System Cron Jobs:[/cyan]")
            console.print(system_cron)
        else:
            console.print("[bold magenta]No system-level cron jobs found.[/bold magenta]")
    else:
        console.print("[red][!] You need root privileges to view system cron jobs.[/red]")


@timed
def check_docker():
    section("[🐳] Docker Container & Misconfig Detection")
    cgroup_data = subprocess.getoutput("cat /proc/self/cgroup")

    if "docker" in cgroup_data:
        console.print("[green]✔ Inside a Docker container[/green]")
        if os.path.exists("/var/run/docker.sock"):
            console.print("[red][!] Docker socket is exposed! Potential privilege escalation.[/red]")
        else:
            console.print("[yellow]Docker socket not found.[/yellow]")
    else:
        console.print("[cyan]Not running inside Docker.[/cyan]")


def is_wsl():
    try:
        with open("/proc/version", "r") as f:
            if "microsoft" in f.read().lower():
                return True
        return False
    except:
        return False


def is_vm():
    try:
        dmi_output = subprocess.getoutput("dmidecode -s system-product-name 2>/dev/null").lower()
        known_vms = ["virtualbox", "kvm", "vmware", "hyper-v", "xen", "qemu"]
        return any(vm in dmi_output for vm in known_vms)
    except:
        return False


def has_hypervisor_flag():
    return "hypervisor" in subprocess.getoutput("lscpu").lower()


def check_environment():
    console.print(Panel("[🌐] Host Environment Detection", style="bold cyan", box=box.SQUARE))

    if is_wsl():
        console.print("[yellow] [!] Running inside WSL (Windows Subsystem for Linux)[/yellow]")

    if is_vm():
        console.print("[cyan] [!] Virtual machine detected[/cyan]")

    if has_hypervisor_flag():
        console.print("[cyan] [!] CPU reports virtualization/hypervisor flag[/cyan]")
