import os
from lib.logger import log
from rich.console import Console
from rich.panel import Panel
from rich import box
from time import time

console = Console()

def check_docker_breakouts():
    """Check for common Docker escape vectors"""
    start = time()
    console.print(Panel("[🐳] Docker Breakout Checks", style="bold cyan", box=box.SQUARE))

    if not is_container():
        console.print("[magenta]✘ Not detected inside a container[/magenta]\n")
        return

    console.print("[yellow][!] Inside a container. Checking for escape paths...[/yellow]\n")
    check_privileged_mode()
    check_dangerous_mounts()
    check_docker_socket()
    check_dangerous_capabilities()
    check_unconfined_seccomp()

    console.print(f"[green]✓ Docker checks completed in {time() - start:.2f}s[/green]\n")


def is_container():
    """Check if we're running in a container"""
    try:
        if os.path.exists("/.dockerenv"):
            return True
        with open("/proc/1/cgroup", "r") as f:
            content = f.read()
            if any(x in content for x in ["docker", "containerd", "kubepods"]):
                return True
        return False
    except Exception as e:
        console.print(f"[red]Error during Docker detection: {e}[/red]")
        return False


def check_privileged_mode():
    """Check if container is running in privileged mode"""
    if os.path.exists("/dev/mem"):
        console.print("[red][!] Privileged mode detected (access to /dev/mem)[/red]")


def check_dangerous_mounts():
    """Check for dangerous host mounts"""
    dangerous_mounts = ["/", "/etc", "/var/run/docker.sock", "/sys", "/proc"]

    try:
        with open("/proc/mounts", "r") as f:
            mounts = f.read()
            for dm in dangerous_mounts:
                if dm in mounts:
                    console.print(f"[red][!] Dangerous mount found: {dm}[/red]")
    except Exception as e:
        console.print(f"[red]Error reading /proc/mounts: {e}[/red]")


def check_docker_socket():
    """Check for Docker socket access"""
    docker_sock_paths = ["/var/run/docker.sock", "/run/docker.sock"]

    for sock_path in docker_sock_paths:
        if os.path.exists(sock_path):
            if os.access(sock_path, os.R_OK):
                console.print(f"[red][!] Docker socket accessible: {sock_path}[/red]")
                console.print("[yellow]    Exploit: docker run -v /:/host -it ubuntu chroot /host[/yellow]")


def check_dangerous_capabilities():
    """Check for dangerous capabilities"""
    dangerous_caps = [
        "CAP_SYS_ADMIN", "CAP_SYS_MODULE", "CAP_SYS_PTRACE",
        "CAP_NET_ADMIN", "CAP_DAC_READ_SEARCH"
    ]

    try:
        with open("/proc/self/status", "r") as f:
            status = f.read()
            for cap in dangerous_caps:
                if cap in status:
                    console.print(f"[red][!] Dangerous capability enabled: {cap}[/red]")
    except Exception as e:
        console.print(f"[red]Error checking capabilities: {e}[/red]")


def check_unconfined_seccomp():
    """Check if seccomp is disabled"""
    try:
        with open("/proc/self/status", "r") as f:
            if "Seccomp: 0" in f.read():
                console.print("[red][!] Seccomp is disabled (--security-opt=unconfined)[/red]")
    except Exception as e:
        console.print(f"[red]Error checking seccomp status: {e}[/red]")
