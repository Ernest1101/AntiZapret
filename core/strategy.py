import subprocess
import os

class StrategyManager:
    def __init__(self, bin_path="bin", lists_path="lists"):
        self.bin_path = bin_path
        self.lists_path = lists_path
        self.current_process = None
        self.strategies = {
            "general": {
                "name": "General",
                "description": "Базовая стратегия обхода DPI",
                "args": self._get_general_args()
            },
            "general_alt": {
                "name": "General (ALT)",
                "description": "Альтернативная стратегия с fake пакетами для Discord",
                "args": self._get_general_alt_args()
            },
            "general_fake": {
                "name": "General (FAKE TLS)",
                "description": "Стратегия с подменой TLS пакетов",
                "args": self._get_general_fake_args()
            }
        }

    def _get_general_args(self):
        return [
            "--wf-tcp=80,443,2053,2083,2087,2096,8443",
            "--wf-udp=443,19294-19344,50000-50100",
            "--filter-udp=443",
            f"--hostlist={self.lists_path}\\list-general.txt",
            f"--hostlist={self.lists_path}\\list-general-user.txt",
            "--dpi-desync=fake",
            "--dpi-desync-repeats=6",
            f"--dpi-desync-fake-quic={self.bin_path}\\files\\quic_initial_www_google_com.bin",
            "--new",
            "--filter-udp=19294-19344,50000-50100",
            "--filter-l7=discord,stun",
            "--dpi-desync=fake",
            f"--dpi-desync-fake-discord={self.bin_path}\\quic_initial_dbankcloud_ru.bin",
            f"--dpi-desync-fake-stun={self.bin_path}\\quic_initial_dbankcloud_ru.bin",
            "--dpi-desync-repeats=6",
            "--new",
            "--filter-tcp=2053,2083,2087,2096,8443",
            "--hostlist-domains=discord.media",
            "--dpi-desync=fake,fakedsplit",
            "--dpi-desync-repeats=6",
            "--dpi-desync-fooling=ts",
            f"--dpi-desync-fake-tls={self.bin_path}\\tls_clienthello_www_google_com.bin",
            "--new",
            "--filter-tcp=80,443",
            f"--hostlist={self.lists_path}\\list-general.txt",
            f"--hostlist={self.lists_path}\\list-general-user.txt",
            "--dpi-desync=fake,fakedsplit",
            "--dpi-desync-repeats=6",
            "--dpi-desync-fooling=ts",
            f"--dpi-desync-fake-tls={self.bin_path}\\tls_clienthello_www_google_com.bin"
        ]

    def _get_general_alt_args(self):
        return [
            "--wf-tcp=80,443,2053,2083,2087,2096,8443",
            "--wf-udp=443,19294-19344,50000-50100",
            "--filter-udp=443",
            f"--hostlist={self.lists_path}\\list-general.txt",
            f"--hostlist={self.lists_path}\\list-general-user.txt",
            "--dpi-desync=fake",
            "--dpi-desync-repeats=6",
            f"--dpi-desync-fake-quic={self.bin_path}\\files\\quic_initial_www_google_com.bin",
            "--new",
            "--filter-udp=19294-19344,50000-50100",
            "--filter-l7=discord,stun",
            "--dpi-desync=fake",
            f"--dpi-desync-fake-discord={self.bin_path}\\quic_initial_dbankcloud_ru.bin",
            f"--dpi-desync-fake-stun={self.bin_path}\\quic_initial_dbankcloud_ru.bin",
            "--dpi-desync-repeats=6",
            "--new",
            "--filter-tcp=2053,2083,2087,2096,8443",
            "--hostlist-domains=discord.media",
            "--dpi-desync=fake,fakedsplit",
            "--dpi-desync-repeats=6",
            "--dpi-desync-fooling=ts",
            f"--dpi-desync-fake-tls={self.bin_path}\\tls_clienthello_www_google_com.bin",
            "--new",
            "--filter-tcp=80,443",
            f"--hostlist={self.lists_path}\\list-general.txt",
            f"--hostlist={self.lists_path}\\list-general-user.txt",
            "--dpi-desync=fake,fakedsplit",
            "--dpi-desync-repeats=6",
            "--dpi-desync-fooling=ts",
            f"--dpi-desync-fake-tls={self.bin_path}\\tls_clienthello_www_google_com.bin"
        ]

    def _get_general_fake_args(self):
        return [
            "--wf-tcp=80,443,2053,2083,2087,2096,8443",
            "--wf-udp=443,19294-19344,50000-50100",
            "--filter-udp=443",
            f"--hostlist={self.lists_path}\\list-general.txt",
            f"--hostlist={self.lists_path}\\list-general-user.txt",
            "--dpi-desync=fake",
            "--dpi-desync-repeats=6",
            f"--dpi-desync-fake-quic={self.bin_path}\\files\\quic_initial_www_google_com.bin",
            "--new",
            "--filter-udp=19294-19344,50000-50100",
            "--filter-l7=discord,stun",
            "--dpi-desync=fake",
            f"--dpi-desync-fake-discord={self.bin_path}\\quic_initial_dbankcloud_ru.bin",
            f"--dpi-desync-fake-stun={self.bin_path}\\quic_initial_dbankcloud_ru.bin",
            "--dpi-desync-repeats=6",
            "--new",
            "--filter-tcp=2053,2083,2087,2096,8443",
            "--hostlist-domains=discord.media",
            "--dpi-desync=fake,split2",
            "--dpi-desync-repeats=6",
            "--dpi-desync-fooling=md5sig,badseq",
            f"--dpi-desync-fake-tls={self.bin_path}\\tls_clienthello_www_google_com.bin",
            "--new",
            "--filter-tcp=80,443",
            f"--hostlist={self.lists_path}\\list-general.txt",
            f"--hostlist={self.lists_path}\\list-general-user.txt",
            "--dpi-desync=fake,split2",
            "--dpi-desync-repeats=6",
            "--dpi-desync-fooling=md5sig,badseq",
            f"--dpi-desync-fake-tls={self.bin_path}\\tls_clienthello_www_google_com.bin"
        ]

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