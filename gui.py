import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import time
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from core.strategy import StrategyManager
from core.service import ServiceManager
from core.config import ConfigManager

ctk.set_default_color_theme("blue")

class AntiZapretGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("AntiZapret - Обход блокировок")
        self.geometry("1100x700")
        self.minsize(900, 600)
        
        self.strategy_manager = StrategyManager()
        self.service_manager = ServiceManager()
        self.config_manager = ConfigManager()
        
        self.stats = self._load_stats()
        
        self._setup_window()
        self._create_ui()
        self._start_status_monitor()
        
        self.log("AntiZapret запущен", "OK")
        self.log(f"Права администратора: {'да' if self._is_admin() else 'нет'}", "INFO")
        
        config = self.strategy_manager.load_config()
        if config.get('last_strategy'):
            self.strategy_var.set(config['last_strategy'])
    
    def _setup_window(self):
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _create_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)
        
        logo_label = ctk.CTkLabel(self.sidebar, text="🛡️ AntiZapret", 
                                   font=ctk.CTkFont(size=20, weight="bold"))
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.nav_buttons = {}
        nav_items = [
            ("home", "🏠 Главная"),
            ("strategies", "⚡ Стратегии"),
            ("services", "⚙️ Службы"),
            ("lists", "📋 Списки"),
            ("logs", "📝 Логи"),
            ("settings", "🔧 Настройки"),
            ("about", "ℹ️ О программе")
        ]
        
        for i, (key, text) in enumerate(nav_items):
            btn = ctk.CTkButton(self.sidebar, text=text, anchor="w", height=40,
                               corner_radius=8, command=lambda k=key: self._show_page(k))
            btn.grid(row=i+1, column=0, padx=10, pady=5, sticky="ew")
            self.nav_buttons[key] = btn
        
        self.status_frame = ctk.CTkFrame(self.sidebar)
        self.status_frame.grid(row=8, column=0, padx=10, pady=10, sticky="ew")
        
        self.status_indicator = ctk.CTkLabel(self.status_frame, text="●", 
                                              text_color="gray", font=ctk.CTkFont(size=20))
        self.status_indicator.pack(side="left", padx=5)
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="Остановлено", 
                                          font=ctk.CTkFont(size=12))
        self.status_label.pack(side="left", padx=5)
        
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        self.pages = {}
        self._create_home_page()
        self._create_strategies_page()
        self._create_services_page()
        self._create_lists_page()
        self._create_logs_page()
        self._create_settings_page()
        self._create_about_page()
        
        self._show_page("home")
    
    def _create_home_page(self):
        page = ctk.CTkFrame(self.main_frame)
        self.pages["home"] = page
        
        title = ctk.CTkLabel(page, text="Главная", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="w")
        
        cards_frame = ctk.CTkFrame(page)
        cards_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.card_strategy = self._create_card(cards_frame, "Текущая стратегия", "Не выбрана", 0)
        self.card_status = self._create_card(cards_frame, "Статус", "Остановлено", 1)
        self.card_uptime = self._create_card(cards_frame, "Время работы", "0:00:00", 2)
        
        self.stats_frame = ctk.CTkFrame(page)
        self.stats_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
        
        stats_title = ctk.CTkLabel(self.stats_frame, text="📊 Статистика", 
                                    font=ctk.CTkFont(size=16, weight="bold"))
        stats_title.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")
        
        self.stats_labels = {}
        stats_items = [
            ("total_launches", "Всего запусков"),
            ("successful_tests", "Успешных тестов"),
            ("favorite_strategy", "Любимая стратегия")
        ]
        
        for i, (key, text) in enumerate(stats_items):
            label = ctk.CTkLabel(self.stats_frame, text=f"{text}: {self.stats.get(key, 0)}")
            label.grid(row=i+1, column=0, columnspan=3, padx=10, pady=2, sticky="w")
            self.stats_labels[key] = label
        
        buttons_frame = ctk.CTkFrame(page)
        buttons_frame.grid(row=3, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
        
        self.btn_start = ctk.CTkButton(buttons_frame, text="▶️ Запустить", 
                                        command=self._start_current, height=40,
                                        fg_color="green", hover_color="darkgreen")
        self.btn_start.grid(row=0, column=0, padx=10, pady=10)
        
        self.btn_stop = ctk.CTkButton(buttons_frame, text="⏹️ Остановить", 
                                       command=self._stop_current, height=40,
                                       fg_color="red", hover_color="darkred")
        self.btn_stop.grid(row=0, column=1, padx=10, pady=10)
        
        self.btn_test_all = ctk.CTkButton(buttons_frame, text="🔍 Проверить все стратегии", 
                                           command=self._test_all_strategies, height=40)
        self.btn_test_all.grid(row=0, column=2, padx=10, pady=10)
    
    def _create_card(self, parent, title, value, col):
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.grid(row=0, column=col, padx=10, pady=10, sticky="ew")
        
        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12))
        title_label.pack(padx=20, pady=(15, 5))
        
        value_label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=18, weight="bold"))
        value_label.pack(padx=20, pady=(0, 15))
        
        return value_label
    
    def _create_strategies_page(self):
        page = ctk.CTkScrollableFrame(self.main_frame)
        self.pages["strategies"] = page
        
        title = ctk.CTkLabel(page, text="⚡ Стратегии", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(padx=20, pady=(20, 10), anchor="w")
        
        self.strategy_var = tk.StringVar(value="general")
        
        strategies = self.strategy_manager.strategies
        
        categories = {
            "Базовые": ["general", "general_alt"],
            "ALT варианты": [f"general_alt{i}" for i in range(2, 13)],
            "FAKE TLS": ["general_fake_tls_auto", "general_fake_tls_auto_alt", 
                        "general_fake_tls_auto_alt2", "general_fake_tls_auto_alt3"],
            "Simple Fake": ["general_simple_fake", "general_simple_fake_alt", 
                           "general_simple_fake_alt2"]
        }
        
        for category, strategy_ids in categories.items():
            cat_label = ctk.CTkLabel(page, text=f"📁 {category}", 
                                     font=ctk.CTkFont(size=16, weight="bold"))
            cat_label.pack(padx=20, pady=(15, 5), anchor="w")
            
            for strategy_id in strategy_ids:
                if strategy_id in strategies:
                    self._create_strategy_card(page, strategy_id, strategies[strategy_id])
    
    def _create_strategy_card(self, parent, strategy_id, strategy):
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.pack(padx=20, pady=5, fill="x")
        
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=5)
        
        radio = ctk.CTkRadioButton(header, text=strategy["name"], 
                                    variable=self.strategy_var, value=strategy_id,
                                    font=ctk.CTkFont(size=14, weight="bold"))
        radio.pack(side="left")
        
        desc = ctk.CTkLabel(card, text=strategy["description"], 
                           font=ctk.CTkFont(size=12), text_color="gray")
        desc.pack(padx=10, pady=(0, 5), anchor="w")
        
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        test_btn = ctk.CTkButton(btn_frame, text="🔍 Тест", width=80, height=30,
                                 command=lambda sid=strategy_id: self._test_strategy(sid))
        test_btn.pack(side="right", padx=5)
        
        start_btn = ctk.CTkButton(btn_frame, text="▶️ Запустить", width=100, height=30,
                                  command=lambda sid=strategy_id: self._start_strategy(sid))
        start_btn.pack(side="right", padx=5)
    
    def _create_services_page(self):
        page = ctk.CTkFrame(self.main_frame)
        self.pages["services"] = page
        
        title = ctk.CTkLabel(page, text="⚙️ Службы", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")
        
        service_frame = ctk.CTkFrame(page)
        service_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        service_title = ctk.CTkLabel(service_frame, text="Управление службой", 
                                     font=ctk.CTkFont(size=16, weight="bold"))
        service_title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        self.service_status_label = ctk.CTkLabel(service_frame, text="Статус: Не установлена")
        self.service_status_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        btn_frame = ctk.CTkFrame(service_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        
        ctk.CTkButton(btn_frame, text="Создать службу", command=self._create_service).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Удалить службу", command=self._remove_service).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Запустить", command=self._start_service).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Остановить", command=self._stop_service).pack(side="left", padx=5)
        
        tools_frame = ctk.CTkFrame(page)
        tools_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        tools_title = ctk.CTkLabel(tools_frame, text="Инструменты", 
                                   font=ctk.CTkFont(size=16, weight="bold"))
        tools_title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        ctk.CTkButton(tools_frame, text="🔄 Обновить IPSet", 
                     command=self._update_ipset).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkButton(tools_frame, text="📝 Обновить hosts", 
                     command=self._update_hosts).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkButton(tools_frame, text="🔍 Диагностика", 
                     command=self._run_diagnostics).grid(row=3, column=0, padx=10, pady=5, sticky="w")
    
    def _create_lists_page(self):
        page = ctk.CTkFrame(self.main_frame)
        self.pages["lists"] = page
        
        title = ctk.CTkLabel(page, text="📋 Списки доменов", 
                            font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.list_tabs = ctk.CTkTabview(page)
        self.list_tabs.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)
        
        lists = {
            "Основные": "list-general.txt",
            "Пользовательские": "list-general-user.txt",
            "Google": "list-google.txt",
            "IPSet": "ipset-all.txt"
        }
        
        self.list_editors = {}
        for tab_name, filename in lists.items():
            tab = self.list_tabs.add(tab_name)
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(0, weight=1)
            
            editor = ctk.CTkTextbox(tab, font=ctk.CTkFont(size=12))
            editor.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            
            btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
            btn_frame.grid(row=1, column=0, padx=10, pady=5)
            
            ctk.CTkButton(btn_frame, text="💾 Сохранить", width=100,
                         command=lambda fn=filename, ed=editor: self._save_list(fn, ed)).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text="🔄 Обновить", width=100,
                         command=lambda fn=filename, ed=editor: self._load_list(fn, ed)).pack(side="left", padx=5)
            
            self.list_editors[filename] = editor
            self._load_list(filename, editor)
    
    def _create_logs_page(self):
        page = ctk.CTkFrame(self.main_frame)
        self.pages["logs"] = page
        
        title = ctk.CTkLabel(page, text="📝 Логи", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.log_text = ctk.CTkTextbox(page, font=ctk.CTkFont(size=12), state="disabled")
        self.log_text.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)
        
        btn_frame = ctk.CTkFrame(page, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=20, pady=10)
        
        ctk.CTkButton(btn_frame, text="🗑️ Очистить", command=self._clear_logs).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="💾 Экспорт", command=self._export_logs).pack(side="left", padx=5)
    
    def _create_settings_page(self):
        page = ctk.CTkScrollableFrame(self.main_frame)
        self.pages["settings"] = page
        
        title = ctk.CTkLabel(page, text="🔧 Настройки", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(padx=20, pady=(20, 10), anchor="w")
        
        appearance_frame = ctk.CTkFrame(page)
        appearance_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(appearance_frame, text="🎨 Внешний вид", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(padx=10, pady=10, anchor="w")
        
        theme_frame = ctk.CTkFrame(appearance_frame, fg_color="transparent")
        theme_frame.pack(padx=10, pady=5, fill="x")
        
        ctk.CTkLabel(theme_frame, text="Тема:").pack(side="left", padx=5)
        self.theme_var = tk.StringVar(value=ctk.get_appearance_mode())
        ctk.CTkOptionMenu(theme_frame, values=["Светлая", "Тёмная", "Системная"],
                         variable=self.theme_var, command=self._change_theme).pack(side="left", padx=5)
        
        behavior_frame = ctk.CTkFrame(page)
        behavior_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(behavior_frame, text="⚡ Поведение", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(padx=10, pady=10, anchor="w")
        
        self.auto_start_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(behavior_frame, text="Автозапуск при старте Windows",
                       variable=self.auto_start_var).pack(padx=10, pady=5, anchor="w")
        
        self.minimize_to_tray_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(behavior_frame, text="Сворачивать в трей при закрытии",
                       variable=self.minimize_to_tray_var).pack(padx=10, pady=5, anchor="w")
        
        self.notifications_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(behavior_frame, text="Показывать уведомления",
                       variable=self.notifications_var).pack(padx=10, pady=5, anchor="w")
        
        test_frame = ctk.CTkFrame(page)
        test_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(test_frame, text="🔍 Тестирование", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(padx=10, pady=10, anchor="w")
        
        ctk.CTkLabel(test_frame, text="URL для теста:").pack(padx=10, pady=5, anchor="w")
        self.test_url_var = tk.StringVar(value="https://discord.com")
        ctk.CTkEntry(test_frame, textvariable=self.test_url_var, width=400).pack(padx=10, pady=5)
        
        ctk.CTkButton(test_frame, text="🔍 Проверить все стратегии", 
                     command=self._test_all_strategies).pack(padx=10, pady=10)
        
        data_frame = ctk.CTkFrame(page)
        data_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(data_frame, text="💾 Данные", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(padx=10, pady=10, anchor="w")
        
        btn_frame = ctk.CTkFrame(data_frame, fg_color="transparent")
        btn_frame.pack(padx=10, pady=10)
        
        ctk.CTkButton(btn_frame, text="📤 Экспорт конфигурации", 
                     command=self._export_config).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="📥 Импорт конфигурации", 
                     command=self._import_config).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🗑️ Сброс статистики", 
                     command=self._reset_stats).pack(side="left", padx=5)
    
    def _create_about_page(self):
        page = ctk.CTkFrame(self.main_frame)
        self.pages["about"] = page
        
        title = ctk.CTkLabel(page, text="ℹ️ О программе", 
                            font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(padx=20, pady=(20, 10))
        
        info_frame = ctk.CTkFrame(page)
        info_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(info_frame, text="AntiZapret", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        ctk.CTkLabel(info_frame, text="Версия: 1.0.0", 
                    font=ctk.CTkFont(size=14)).pack(pady=5)
        ctk.CTkLabel(info_frame, text="GUI для обхода DPI блокировок", 
                    font=ctk.CTkFont(size=12), text_color="gray").pack(pady=5)
        
        links_frame = ctk.CTkFrame(page)
        links_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(links_frame, text="🔗 Ссылки", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        ctk.CTkButton(links_frame, text="GitHub репозиторий", 
                     command=lambda: self._open_url("https://github.com/Ernest1101/AntiZapret")).pack(pady=5)
        ctk.CTkButton(links_frame, text="Оригинальный zapret", 
                     command=lambda: self._open_url("https://github.com/bol-van/zapret")).pack(pady=5)
        ctk.CTkButton(links_frame, text="zapret-discord-youtube", 
                     command=lambda: self._open_url("https://github.com/Flowseal/zapret-discord-youtube")).pack(pady=5)
        
        credits_frame = ctk.CTkFrame(page)
        credits_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(credits_frame, text="🙏 Благодарности", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        ctk.CTkLabel(credits_frame, text="bol-van - разработчик zapret", 
                    font=ctk.CTkFont(size=12)).pack(pady=2)
        ctk.CTkLabel(credits_frame, text="Flowseal - zapret-discord-youtube", 
                    font=ctk.CTkFont(size=12)).pack(pady=2)
    
    def _show_page(self, page_name):
        for page in self.pages.values():
            page.grid_remove()
        
        self.pages[page_name].grid(row=0, column=0, sticky="nsew")
        
        for key, btn in self.nav_buttons.items():
            if key == page_name:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")
    
    def _start_current(self):
        strategy_id = self.strategy_var.get()
        self._start_strategy(strategy_id)
    
    def _start_strategy(self, strategy_id):
        success, msg = self.strategy_manager.start_strategy(strategy_id)
        self.log(msg, "OK" if success else "ERROR")
        
        if success:
            self._update_stats("total_launches")
            self._update_stats("favorite_strategy", strategy_id)
            self._update_status(True)
            self._update_card("strategy", self.strategy_manager.strategies[strategy_id]["name"])
    
    def _stop_current(self):
        self.strategy_manager.stop_all()
        self.log("Остановка всех процессов...", "INFO")
        self.log("All processes stopped", "OK")
        self._update_status(False)
        self._update_card("strategy", "Не выбрана")
    
    def _test_strategy(self, strategy_id):
        self.log(f"Тестирование стратегии: {strategy_id}", "INFO")
        
        def test():
            result = self.strategy_manager.test_strategy(strategy_id, self.test_url_var.get())
            if result["success"]:
                self.log(f"✅ {strategy_id}: OK ({result['latency']}ms)", "OK")
                self._update_stats("successful_tests")
            else:
                self.log(f"❌ {strategy_id}: {result.get('error', 'Failed')}", "ERROR")
        
        threading.Thread(target=test, daemon=True).start()
    
    def _test_all_strategies(self):
        self.log("🔍 Запуск теста всех стратегий...", "INFO")
        
        def test_all():
            results = self.strategy_manager.test_all_strategies(self.test_url_var.get())
            
            working = [r for r in results if r["success"]]
            
            self.log(f"\n{'='*50}", "INFO")
            self.log(f"📊 Результаты тестирования:", "INFO")
            self.log(f"Всего стратегий: {len(results)}", "INFO")
            self.log(f"Рабочих: {len(working)}", "OK")
            self.log(f"Нерабочих: {len(results) - len(working)}", "ERROR")
            
            if working:
                self.log(f"\n✅ Рабочие стратегии:", "OK")
                for r in working:
                    self.log(f"  - {r['strategy']}: {r['latency']}ms", "OK")
            
            self.log(f"{'='*50}\n", "INFO")
        
        threading.Thread(target=test_all, daemon=True).start()
    
    def _update_status(self, running):
        if running:
            self.status_indicator.configure(text_color="green")
            self.status_label.configure(text="Работает")
            self._update_card("status", "✅ Работает")
        else:
            self.status_indicator.configure(text_color="red")
            self.status_label.configure(text="Остановлено")
            self._update_card("status", "❌ Остановлено")
            self._update_card("uptime", "0:00:00")
    
    def _update_card(self, card_name, value):
        if card_name == "strategy":
            self.card_strategy.configure(text=value)
        elif card_name == "status":
            self.card_status.configure(text=value)
        elif card_name == "uptime":
            self.card_uptime.configure(text=value)
    
    def _start_status_monitor(self):
        def monitor():
            start_time = None
            while True:
                if self.strategy_manager.is_running():
                    if start_time is None:
                        start_time = time.time()
                    elapsed = int(time.time() - start_time)
                    hours, remainder = divmod(elapsed, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    self._update_card("uptime", f"{hours}:{minutes:02d}:{seconds:02d}")
                else:
                    start_time = None
                    if self.status_label.cget("text") == "Работает":
                        self._update_status(False)
                time.sleep(2)
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        log_entry = f"{timestamp} [{level}] {message}\n"
        
        self.log_text.configure(state="normal")
        self.log_text.insert("end", log_entry)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
    
    def _clear_logs(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
    
    def _export_logs(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                               filetypes=[("Text files", "*.txt")])
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_text.get("1.0", "end"))
            self.log(f"Логи экспортированы в {filename}", "OK")
    
    def _load_list(self, filename, editor):
        filepath = Path(__file__).parent.parent / "lists" / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            editor.delete("1.0", "end")
            editor.insert("1.0", content)
    
    def _save_list(self, filename, editor):
        filepath = Path(__file__).parent.parent / "lists" / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(editor.get("1.0", "end"))
        self.log(f"Список {filename} сохранён", "OK")
    
    def _create_service(self):
        strategy_id = self.strategy_var.get()
        success, msg = self.service_manager.create_service(strategy_id)
        self.log(msg, "OK" if success else "ERROR")
    
    def _remove_service(self):
        success, msg = self.service_manager.remove_service()
        self.log(msg, "OK" if success else "ERROR")
    
    def _start_service(self):
        success, msg = self.service_manager.start_service()
        self.log(msg, "OK" if success else "ERROR")
    
    def _stop_service(self):
        success, msg = self.service_manager.stop_service()
        self.log(msg, "OK" if success else "ERROR")
    
    def _update_ipset(self):
        self.log("Обновление IPSet...", "INFO")
    
    def _update_hosts(self):
        self.log("Обновление hosts файла...", "INFO")
    
    def _run_diagnostics(self):
        self.log("Запуск диагностики...", "INFO")
    
    def _change_theme(self, choice):
        if choice == "Светлая":
            ctk.set_appearance_mode("light")
        elif choice == "Тёмная":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("system")
    
    def _export_config(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json",
                                               filetypes=[("JSON files", "*.json")])
        if filename:
            config = {
                "last_strategy": self.strategy_var.get(),
                "stats": self.stats,
                "settings": {
                    "auto_start": self.auto_start_var.get(),
                    "minimize_to_tray": self.minimize_to_tray_var.get(),
                    "notifications": self.notifications_var.get(),
                    "test_url": self.test_url_var.get()
                }
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.log(f"Конфигурация экспортирована в {filename}", "OK")
    
    def _import_config(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if "last_strategy" in config:
                    self.strategy_var.set(config["last_strategy"])
                
                if "stats" in config:
                    self.stats = config["stats"]
                    self._update_stats_display()
                
                if "settings" in config:
                    settings = config["settings"]
                    self.auto_start_var.set(settings.get("auto_start", False))
                    self.minimize_to_tray_var.set(settings.get("minimize_to_tray", True))
                    self.notifications_var.set(settings.get("notifications", True))
                    self.test_url_var.set(settings.get("test_url", "https://discord.com"))
                
                self.log(f"Конфигурация импортирована из {filename}", "OK")
            except Exception as e:
                self.log(f"Ошибка импорта: {str(e)}", "ERROR")
    
    def _reset_stats(self):
        if messagebox.askyesno("Подтверждение", "Сбросить всю статистику?"):
            self.stats = {
                "total_launches": 0,
                "successful_tests": 0,
                "favorite_strategy": "Не определена"
            }
            self._save_stats()
            self._update_stats_display()
            self.log("Статистика сброшена", "OK")
    
    def _load_stats(self):
        stats_file = Path(__file__).parent.parent / "stats.json"
        if stats_file.exists():
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "total_launches": 0,
            "successful_tests": 0,
            "favorite_strategy": "Не определена"
        }
    
    def _save_stats(self):
        stats_file = Path(__file__).parent.parent / "stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
    
    def _update_stats(self, key, value=None):
        if value:
            self.stats[key] = value
        else:
            self.stats[key] = self.stats.get(key, 0) + 1
        self._save_stats()
        self._update_stats_display()
    
    def _update_stats_display(self):
        for key, label in self.stats_labels.items():
            label.configure(text=f"{label.cget('text').split(':')[0]}: {self.stats.get(key, 0)}")
    
    def _is_admin(self):
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def _open_url(self, url):
        import webbrowser
        webbrowser.open(url)
    
    def _on_closing(self):
        if self.minimize_to_tray_var.get():
            self.withdraw()
            self.log("Свёрнуто в трей", "INFO")
        else:
            self.strategy_manager.stop_all()
            self.destroy()

def main():
    try:
        if sys.platform == "win32":
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                script = os.path.abspath(sys.argv[0])
                params = ' '.join([f'"{script}"'] + [f'"{arg}"' for arg in sys.argv[1:]])
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
                sys.exit(0)
        
        app = AntiZapretGUI()
        app.mainloop()
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()