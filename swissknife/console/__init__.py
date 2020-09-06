import subprocess
import shlex

def run_command(cmd,silent=True,timeout=15):
    if isinstance(cmd,str):
        cmd = shlex.split(cmd)

    if silent:
        subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout)
    else:
        subprocess.call(cmd,timeout=15)