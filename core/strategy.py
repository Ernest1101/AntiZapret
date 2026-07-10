import subprocess
import os

class StrategyManager:
    def __init__(self, bin_path="bin"):
        self.bin_path = bin_path
        self.strategies = {
            "general": "general.bat",
            "general_alt": "general (ALT).bat",
            "general_fake": "general (FAKE TLS).bat"
        }

    def get_available_strategies(self):
        available = {}
        for key, filename in self.strategies.items():
            path = os.path.join(filename)
            if os.path.exists(path):
                available[key] = filename
        return available

    def run_strategy(self, strategy_name):
        if strategy_name not in self.strategies:
            return False, "Strategy not found"

        bat_file = self.strategies[strategy_name]
        if not os.path.exists(bat_file):
            return False, f"File {bat_file} not found"

        try:
            subprocess.Popen(
                [bat_file],
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, "Strategy started"
        except Exception as e:
            return False, str(e)

    def stop_all(self):
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", "winws.exe"],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, "All processes stopped"
        except:
            return False, "Error stopping processes"
