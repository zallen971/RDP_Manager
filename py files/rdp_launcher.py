import subprocess
import shutil
import sys

def find_freerdp():
    candidates = ["sdl-freerdp", "xfreerdp", "wfreerdp"]
    for name in candidates:
        path = shutil.which(name)
        if path:
            return path
    return None


def launch_rdp(connection, password=None):
    binary = find_freerdp()

    if not binary:
        return False, (
            "FreeRDP not found. \n"
            "Install it with: brew install freerdp"
        )
    

    args = [binary]
    args += [f"/v:{connection['host']}:{connection['port']}"]


    if connection.get("username"):
        args += [f"/u:{connection['username']}"]
    if password:
        args += [f"/p:{password}"]

    
    args += [
        "/f",
        "/dynamic-resolution",
        "/cert:ignore",
        "+clipboard",
    ]

    try:
        process = subprocess.Popen(args)
        return True, "Launched"
    except Exception as e:
        return False, str(e)