import subprocess
import os

class ServiceManager:
    def __init__(self, bin_path="bin"):
        self.bin_path = bin_path
        self.service_name = "AntiZapret"

    def is_running(self):
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq winws.exe"],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            return "winws.exe" in result.stdout
        except:
            return False

    def create_service(self, strategy="general"):
        try:
            script = os.path.join(self.bin_path, "service_create.cmd")
            if os.path.exists(script):
                subprocess.run([script, strategy], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return True
            return False
        except:
            return False

    def delete_service(self):
        try:
            script = os.path.join(self.bin_path, "service_del.cmd")
            if os.path.exists(script):
                subprocess.run([script], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return True
            return False
        except:
            return False

    def start_service(self):
        try:
            script = os.path.join(self.bin_path, "service_start.cmd")
            if os.path.exists(script):
                subprocess.run([script], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return True
            return False
        except:
            return False

    def stop_service(self):
        try:
            script = os.path.join(self.bin_path, "service_stop.cmd")
            if os.path.exists(script):
                subprocess.run([script], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return True
            return False
        except:
            return False

    def get_service_status(self):
        try:
            result = subprocess.run(
                ["sc", "query", self.service_name],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            if "RUNNING" in result.stdout:
                return "running"
            elif "STOPPED" in result.stdout:
                return "stopped"
            return "not_installed"
        except:
            return "not_installed"
