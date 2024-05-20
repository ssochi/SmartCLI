import os
import subprocess

def execute_command(command):
    """Execute a shell command and return its output."""
    try:
        if command.startswith("cd "):
            path = command[3:].strip()
            os.chdir(path)
            return ""
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return str(e)