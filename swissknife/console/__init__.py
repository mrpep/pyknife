import subprocess
import shlex

def run_command(cmd,silent=False,timeout=15):
    if isinstance(cmd,str):
        cmd = shlex.split(cmd)

    if silent:
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout)
    else:
        subprocess.check_call(cmd,timeout=15)