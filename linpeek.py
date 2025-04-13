#!/usr/bin/env python3
import argparse
from core.enumerator import check_suid, check_cron, check_docker
from core.privesc import check_kernel_exploits
from core.creds import loot_proc
from lib.logger import log


def main():
    parser = argparse.ArgumentParser(description="LinPeek - Linux Pentest Toolkit")
    parser.add_argument("--enum", help="Basic enumeration", action="store_true")
    parser.add_argument("--privesc", help="Privilege escalation checks", action="store_true")
    parser.add_argument("--creds", help="Credential harvesting", action="store_true")

    args = parser.parse_args()

    if args.enum:
        check_suid()
        check_cron()
        check_docker()

    if args.privesc:
        check_kernel_exploits()

    if args.creds:
        loot_proc()


if __name__ == "__main__":
    main()