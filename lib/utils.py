import os
import subprocess

def is_root():
    return os.getuid() == 0

def run_cmd(cmd):
    return subprocess.getoutput(cmd)