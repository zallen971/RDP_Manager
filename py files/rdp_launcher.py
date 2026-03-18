import subprocess
import shutil
import sys


def find_rdp_client():
    if sys.platform == "win32":
        return "mstsc.exe"
    candidates = ["wfreerdp", "sdl-freerdp", "xfreerdp3", "xfreerdp"]
    for name in candidates:
        path = shutil.which(name)
        if path:
            return path
    return None


def launch_rdp(connection, password=None):
    if sys.platform == "win32":
        host = f"{connection['host']}:{connection['port']}"

        if connection.get("username") and password:
            subprocess.run([
                "cmdkey",
                f"/generic:TERMSRV/{connection['host']}",
                f"/user:{connection['username']}",
                f"/pass:{password}"
            ], capture_output=True)

        args = [
            "mstsc.exe",
            f"/v:{host}",
            "/f",
        ]
        try:
            subprocess.Popen(args)
            return True, "Launched"
        except Exception as e:
            return False, str(e)

    binary = find_rdp_client()
    if not binary:
        return False, (
            "FreeRDP not found.\n\n"
            "Install it with:\n"
            "  • macOS:   brew install freerdp\n"
            "  • Linux:   sudo apt install freerdp2-x11"
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
        subprocess.Popen(args)
        return True, "Launched"
    except Exception as e:
        return False, str(e)