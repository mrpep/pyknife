import subprocess
import shlex

def run_command(cmd,silent=False,timeout=15):
    """
    Runs a command in a terminal
    cmd:     command to run
    silent:  if True, logs are not shown
    timeout: integer telling the number of seconds to wait before aborting the command
    """
    if isinstance(cmd,str):
        cmd = shlex.split(cmd)

    if silent:
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout)
    else:
        subprocess.check_call(cmd,timeout=timeout)
