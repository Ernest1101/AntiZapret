import subprocess
import os

class StrategyManager:
    def __init__(self, bin_path="bin"):
        self.bin_path = bin_path
        self.current_process = None
        self.strategies = {
            "general": {
                "name": "General",
                "description": "Базовая стратегия обхода DPI",
                "args": [
                    "--wf-tcp=80,443", "--wf-udp=443",
                    "--filter-udp=443", "--hostlist=lists\\list-general.txt",
                    "--dpi-desync=fake", "--dpi-desync-repeats=6",
                    "--dpi-desync-fake-quic=bin\\files\\quic_initial_www_google_com.bin",
                    "--new", "--filter-udp=53", "--dpi-desync=fake",
                    "--dpi-desync-any-protocol", "--dpi-desync-cutoff=d3",
                    "--dpi-desync-repeats=6",
                    "--dpi-desync-fake-quic=bin\\files\\quic_initial_www_google_com.bin",
                    "--new", "--filter-tcp=80", "--hostlist=lists\\list-general.txt",
                    "--dpi-desync=fake,split2", "--dpi-desync-autottl=2",
                    "--dpi-desync-fooling=md5sig"
                ]
            },
            "general_alt": {
                "name": "General (ALT)",
                "description": "Альтернативная стратегия с другими параметрами",
                "args": [
                    "--wf-tcp=80,443", "--wf-udp=443",
                    "--filter-udp=443", "--hostlist=lists\\list-general.txt",
                    "--dpi-desync=fake", "--dpi-desync-repeats=8",
                    "--dpi-desync-fake-quic=bin\\files\\quic_initial_www_google_com.bin",
                    "--new", "--filter-udp=53", "--dpi-desync=fake",
                    "--dpi-desync-any-protocol", "--dpi-desync-cutoff=d3",
                    "--dpi-desync-repeats=8",
                    "--dpi-desync-fake-quic=bin\\files\\quic_initial_www_google_com.bin",
                    "--new", "--filter-tcp=80", "--hostlist=lists\\list-general.txt",
                    "--dpi-desync=split,pos,1", "--dpi-desync-autottl=2",
                    "--dpi-desync-fooling=md5sig"
                ]
            },
            "general_fake": {
                "name": "General (FAKE TLS)",
                "description": "Стратегия с подменой TLS пакетов",
                "args": [
                    "--wf-tcp=80,443", "--wf-udp=443",
                    "--filter-udp=443", "--hostlist=lists\\list-general.txt",
                    "--dpi-desync=fake", "--dpi-desync-repeats=6",
                    "--dpi-desync-fake-quic=bin\\files\\quic_initial_www_google_com.bin",
                    "--new", "--filter-udp=53", "--dpi-desync=fake",
                    "--dpi-desync-any-protocol", "--dpi-desync-cutoff=d3",
                    "--dpi-desync-repeats=6",
                    "--dpi-desync-fake-quic=bin\\files\\quic_initial_www_google_com.bin",
                    "--new", "--filter-tcp=80", "--hostlist=lists\\list-general.txt",
                    "--dpi-desync=fake,split2", "--dpi-desync-autottl=2",
                    "--dpi-desync-fooling=md5sig"
                ]
            }
        }

    def get_available_strategies(self):
        available = {}
        for key, strategy in self.strategies.items():
            available[key] = strategy["name"]
        return available

    def run_strategy(self, strategy_name):
        if strategy_name not in self.strategies:
            return False, "Strategy not found"

        if self.current_process and self.current_process.poll() is None:
            self.stop_all()

        winws_path = os.path.join(self.bin_path, "winws.exe")
        if not os.path.exists(winws_path):
            return False, f"File {winws_path} not found"

        strategy = self.strategies[strategy_name]
        cmd = [winws_path] + strategy["args"]

        try:
            self.current_process = subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True, "Strategy started"
        except Exception as e:
            return False, str(e)

    def stop_all(self):
        try:
            if self.current_process and self.current_process.poll() is None:
                self.current_process.terminate()
                self.current_process.wait(timeout=3)
                self.current_process = None

            subprocess.run(
                ["taskkill", "/F", "/IM", "winws.exe"],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, "All processes stopped"
        except:
            return False, "Error stopping processes"

    def is_running(self):
        if self.current_process and self.current_process.poll() is None:
            return True
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq winws.exe"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return "winws.exe" in result.stdout
        except:
            return False
