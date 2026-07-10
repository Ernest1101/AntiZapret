import subprocess
import os
import json
from pathlib import Path

class StrategyManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.bin_dir = self.base_dir / "bin"
        self.lists_dir = self.base_dir / "lists"
        self.config_file = self.base_dir / "config.json"
        self.current_process = None
        self.current_strategy = None
        self.strategies = self._load_strategies()
        
    def _load_strategies(self):
        return {
            "general": {
                "name": "General",
                "description": "Базовая стратегия для Discord и YouTube",
                "params": [
                    "--wf-tcp=80,443,2053,2083,2087,2096,8443",
                    "--wf-udp=443,19294-19344,50000-50100",
                    "--filter-l7=discord,youtube,stun,quic",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=fake,fakedsplit",
                    "--dpi-desync-fooling=ts",
                    "--dpi-desync-autottl=2",
                    "--dpi-desync-fake-discord=bin\\files\\quic_initial_www_google_com.bin",
                    "--dpi-desync-fake-tls=bin\\files\\tls_clienthello_www_google_com.bin",
                    "--dpi-desync-fake-quic=bin\\files\\quic_initial_www_google_com.bin"
                ]
            },
            "general_alt": {
                "name": "General (ALT)",
                "description": "Альтернативная стратегия - часто работает лучше",
                "params": [
                    "--wf-tcp=80,443,2053,2083,2087,2096,8443",
                    "--wf-udp=443,19294-19344,50000-50100",
                    "--filter-l7=discord,youtube,stun,quic",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=fake,fakedsplit",
                    "--dpi-desync-fooling=ts",
                    "--dpi-desync-fake-discord=bin\\files\\quic_initial_dbankcloud_ru.bin",
                    "--dpi-desync-fake-tls=bin\\files\\tls_clienthello_4pda_to.bin",
                    "--dpi-desync-fake-quic=bin\\files\\quic_initial_dbankcloud_ru.bin"
                ]
            },
            "general_alt2": {
                "name": "General (ALT2)",
                "description": "Вариант ALT с другими fake пакетами",
                "params": [
                    "--wf-tcp=80,443,2053,2083,2087,2096,8443",
                    "--wf-udp=443,19294-19344,50000-50100",
                    "--filter-l7=discord,youtube,stun,quic",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=fake,multisplit",
                    "--dpi-desync-fooling=badseq",
                    "--dpi-desync-fake-discord=bin\\files\\quic_initial_www_google_com.bin",
                    "--dpi-desync-fake-tls=bin\\files\\tls_clienthello_max_ru.bin"
                ]
            },
            "general_alt3": {
                "name": "General (ALT3)",
                "description": "Комбинированная стратегия",
                "params": [
                    "--wf-tcp=80,443",
                    "--wf-udp=443",
                    "--filter-l7=discord,youtube",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=fake,split2",
                    "--dpi-desync-fooling=md5sig",
                    "--dpi-desync-fake-tls=bin\\files\\tls_clienthello_www_google_com.bin"
                ]
            },
            "general_alt4": {
                "name": "General (ALT4)",
                "description": "UDP фокус стратегия",
                "params": [
                    "--wf-tcp=80,443",
                    "--wf-udp=443,19294-19344",
                    "--filter-l7=discord,youtube,stun",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=fake,fakedsplit",
                    "--dpi-desync-fooling=ts,badseq",
                    "--dpi-desync-fake-quic=bin\\files\\quic_initial_dbankcloud_ru.bin"
                ]
            },
            "general_alt5": {
                "name": "General (ALT5)",
                "description": "Multisplit с auto TTL",
                "params": [
                    "--wf-tcp=80,443",
                    "--wf-udp=443",
                    "--filter-l7=discord,youtube",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=multisplit",
                    "--dpi-desync-autottl=2",
                    "--dpi-desync-fake-tls=bin\\files\\tls_clienthello_4pda_to.bin"
                ]
            },
            "general_alt6": {
                "name": "General (ALT6)",
                "description": "Split с timestamp fooling",
                "params": [
                    "--wf-tcp=80,443",
                    "--wf-udp=443",
                    "--filter-l7=discord,youtube",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=split",
                    "--dpi-desync-fooling=ts",
                    "--dpi-desync-fake-tls=bin\\files\\tls_clienthello_www_google_com.bin"
                ]
            },
            "general_alt7": {
                "name": "General (ALT7)",
                "description": "Fake с MD5 signature",
                "params": [
                    "--wf-tcp=80,443",
                    "--wf-udp=443",
                    "--filter-l7=discord,youtube",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=fake",
                    "--dpi-desync-fooling=md5sig",
                    "--dpi-desync-fake-tls=bin\\files\\tls_clienthello_max_ru.bin"
                ]
            },
            "general_alt8": {
                "name": "General (ALT8)",
                "description": "Fakedsplit с badseq",
                "params": [
                    "--wf-tcp=80,443",
                    "--wf-udp=443",
                    "--filter-l7=discord,youtube",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=fakedsplit",
                    "--dpi-desync-fooling=badseq",
                    "--dpi-desync-fake-tls=bin\\files\\tls_clienthello_4pda_to.bin"
                ]
            },
            "general_alt9": {
                "name": "General (ALT9)",
                "description": "Комбинированный fake + split",
                "params": [
                    "--wf-tcp=80,443",
                    "--wf-udp=443",
                    "--filter-l7=discord,youtube",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=fake,split",
                    "--dpi-desync-fooling=ts,md5sig",
                    "--dpi-desync-fake-tls=bin\\files\\tls_clienthello_www_google_com.bin"
                ]
            },
            "general_alt10": {
                "name": "General (ALT10)",
                "description": "Disorder стратегия",
                "params": [
                    "--wf-tcp=80,443",
                    "--wf-udp=443",
                    "--filter-l7=discord,youtube",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=disorder",
                    "--dpi-desync-fooling=ts",
                    "--dpi-desync-fake-tls=bin\\files\\tls_clienthello_max_ru.bin"
                ]
            },
            "general_alt11": {
                "name": "General (ALT11)",
                "description": "IP ID zero стратегия",
                "params": [
                    "--wf-tcp=80,443",
                    "--wf-udp=443",
                    "--filter-l7=discord,youtube",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=fake",
                    "--ip-id=zero",
                    "--dpi-desync-fake-tls=bin\\files\\tls_clienthello_4pda_to.bin"
                ]
            },
            "general_alt12": {
                "name": "General (ALT12)",
                "description": "TTL fooling стратегия",
                "params": [
                    "--wf-tcp=80,443",
                    "--wf-udp=443",
                    "--filter-l7=discord,youtube",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=fake",
                    "--dpi-desync-ttl=5",
                    "--dpi-desync-fake-tls=bin\\files\\tls_clienthello_www_google_com.bin"
                ]
            },
            "general_fake_tls_auto": {
                "name": "General (FAKE TLS AUTO)",
                "description": "Автоматический fake TLS обход",
                "params": [
                    "--wf-tcp=80,443",
                    "--wf-udp=443",
                    "--filter-l7=discord,youtube",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=fake,split2",
                    "--dpi-desync-fooling=md5sig,badseq",
                    "--dpi-desync-fake-tls=bin\\files\\tls_clienthello_www_google_com.bin",
                    "--dpi-desync-fake-quic=bin\\files\\quic_initial_www_google_com.bin"
                ]
            },
            "general_fake_tls_auto_alt": {
                "name": "General (FAKE TLS AUTO ALT)",
                "description": "Вариант FAKE TLS AUTO",
                "params": [
                    "--wf-tcp=80,443",
                    "--wf-udp=443",
                    "--filter-l7=discord,youtube",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=fake,split",
                    "--dpi-desync-fooling=ts,md5sig",
                    "--dpi-desync-fake-tls=bin\\files\\tls_clienthello_4pda_to.bin"
                ]
            },
            "general_fake_tls_auto_alt2": {
                "name": "General (FAKE TLS AUTO ALT2)",
                "description": "Вариант FAKE TLS с multisplit",
                "params": [
                    "--wf-tcp=80,443",
                    "--wf-udp=443",
                    "--filter-l7=discord,youtube",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=fake,multisplit",
                    "--dpi-desync-fooling=badseq",
                    "--dpi-desync-fake-tls=bin\\files\\tls_clienthello_max_ru.bin"
                ]
            },
            "general_fake_tls_auto_alt3": {
                "name": "General (FAKE TLS AUTO ALT3)",
                "description": "Вариант FAKE TLS с disorder",
                "params": [
                    "--wf-tcp=80,443",
                    "--wf-udp=443",
                    "--filter-l7=discord,youtube",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=fake,disorder",
                    "--dpi-desync-fooling=ts",
                    "--dpi-desync-fake-tls=bin\\files\\tls_clienthello_www_google_com.bin"
                ]
            },
            "general_simple_fake": {
                "name": "General (SIMPLE FAKE)",
                "description": "Простой fake без split",
                "params": [
                    "--wf-tcp=80,443",
                    "--wf-udp=443",
                    "--filter-l7=discord,youtube",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=fake",
                    "--dpi-desync-fake-tls=bin\\files\\tls_clienthello_www_google_com.bin"
                ]
            },
            "general_simple_fake_alt": {
                "name": "General (SIMPLE FAKE ALT)",
                "description": "Простой fake с auto TTL",
                "params": [
                    "--wf-tcp=80,443",
                    "--wf-udp=443",
                    "--filter-l7=discord,youtube",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=fake",
                    "--dpi-desync-autottl=2",
                    "--dpi-desync-fake-tls=bin\\files\\tls_clienthello_4pda_to.bin"
                ]
            },
            "general_simple_fake_alt2": {
                "name": "General (SIMPLE FAKE ALT2)",
                "description": "Простой fake с IP ID zero",
                "params": [
                    "--wf-tcp=80,443",
                    "--wf-udp=443",
                    "--filter-l7=discord,youtube",
                    "--hostlist-auto=lists\\list-general.txt",
                    "--dpi-desync=fake",
                    "--ip-id=zero",
                    "--dpi-desync-fake-tls=bin\\files\\tls_clienthello_max_ru.bin"
                ]
            }
        }
    
    def start_strategy(self, strategy_id):
        if strategy_id not in self.strategies:
            return False, f"Стратегия {strategy_id} не найдена"
        
        self.stop_all()
        
        strategy = self.strategies[strategy_id]
        winws_path = self.bin_dir / "winws.exe"
        
        if not winws_path.exists():
            return False, "winws.exe не найден в папке bin/"
        
        cmd = [str(winws_path)] + strategy["params"]
        
        try:
            self.current_process = subprocess.Popen(
                cmd,
                cwd=str(self.base_dir),
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.current_strategy = strategy_id
            self._save_config()
            return True, f"Strategy started: {strategy['name']}"
        except Exception as e:
            return False, f"Ошибка запуска: {str(e)}"
    
    def stop_all(self):
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=3)
            except:
                try:
                    subprocess.run(["taskkill", "/F", "/IM", "winws.exe"], 
                                 capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                except:
                    pass
            self.current_process = None
            self.current_strategy = None
        else:
            try:
                subprocess.run(["taskkill", "/F", "/IM", "winws.exe"], 
                             capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            except:
                pass
    
    def is_running(self):
        if self.current_process and self.current_process.poll() is None:
            return True
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq winws.exe"],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            return "winws.exe" in result.stdout
        except:
            return False
    
    def get_current_strategy(self):
        return self.current_strategy
    
    def _save_config(self):
        config = {}
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except:
                pass
        
        config['last_strategy'] = self.current_strategy
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def test_strategy(self, strategy_id, test_url="https://discord.com"):
        import urllib.request
        import time
        
        success, msg = self.start_strategy(strategy_id)
        if not success:
            return {"success": False, "error": msg}
        
        time.sleep(3)
        
        try:
            start_time = time.time()
            req = urllib.request.Request(test_url, method='HEAD')
            req.add_header('User-Agent', 'Mozilla/5.0')
            response = urllib.request.urlopen(req, timeout=10)
            latency = (time.time() - start_time) * 1000
            
            self.stop_all()
            
            return {
                "success": True,
                "status_code": response.getcode(),
                "latency": round(latency, 2),
                "strategy": strategy_id
            }
        except Exception as e:
            self.stop_all()
            return {
                "success": False,
                "error": str(e),
                "strategy": strategy_id
            }
    
    def test_all_strategies(self, test_url="https://discord.com"):
        results = []
        for strategy_id in self.strategies.keys():
            result = self.test_strategy(strategy_id, test_url)
            results.append(result)
        return results
