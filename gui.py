import sys
import os
import ctypes
import subprocess
import tkinter as tk
from datetime import datetime
from tkinter import scrolledtext, messagebox

import customtkinter as ctk

from core.config import Config
from core.service import ServiceManager
from core.strategy import StrategyManager


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    script = os.path.abspath(sys.argv[0])
    params = " ".join(sys.argv[1:])
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script}" {params}', None, 1
        )
    except:
        pass
    sys.exit()


if not is_admin():
    run_as_admin()


class LogPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.log_text = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, font=("Consolas", 11),
            bg="#1a1a2e", fg="#e0e0e0", insertbackground="#e0e0e0"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {"INFO": "#4fc3f7", "OK": "#66bb6a", "ERROR": "#ef5350", "WARN": "#ffa726"}
        color = colors.get(level, "#e0e0e0")
        self.log_text.insert(tk.END, f"[{timestamp}] ", "time")
        self.log_text.insert(tk.END, f"[{level}] ", "level")
        self.log_text.insert(tk.END, f"{message}\n", "msg")
        self.log_text.tag_config("time", foreground="#9e9e9e")
        self.log_text.tag_config("level", foreground=color)
        self.log_text.tag_config("msg", foreground="#e0e0e0")
        self.log_text.see(tk.END)


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        title = ctk.CTkLabel(self, text="AntiZapret", font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=(20, 5))
        subtitle = ctk.CTkLabel(self, text="Обход блокировок", font=ctk.CTkFont(size=14), text_color="gray")
        subtitle.pack(pady=(0, 20))

        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill=tk.X, padx=20, pady=10)
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")

        self.card_zapret = self._create_card(cards_frame, 0, 0, "Zapret", "Проверка...")
        self.card_service = self._create_card(cards_frame, 0, 1, "Служба", "Проверка...")
        self.card_strategy = self._create_card(cards_frame, 0, 2, "Стратегия", "Не выбрана")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill=tk.X, padx=20, pady=20)

        self.btn_start = ctk.CTkButton(
            btn_frame, text="▶  Запустить", font=ctk.CTkFont(size=14, weight="bold"),
            height=45, fg_color="#66bb6a", hover_color="#4caf50",
            command=self.app.start_zapret
        )
        self.btn_start.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        self.btn_stop = ctk.CTkButton(
            btn_frame, text="■  Остановить", font=ctk.CTkFont(size=14, weight="bold"),
            height=45, fg_color="#ef5350", hover_color="#e53935",
            command=self.app.stop_zapret
        )
        self.btn_stop.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

    def _create_card(self, parent, row, col, title, value):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(15, 5))
        value_label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=16, weight="bold"))
        value_label.pack(pady=(0, 15))
        return value_label

    def update_status(self, zapret_running, service_status, strategy_name):
        if zapret_running:
            self.card_zapret.configure(text="● Работает", text_color="#66bb6a")
        else:
            self.card_zapret.configure(text="● Остановлен", text_color="#ef5350")

        status_map = {"running": ("● Активна", "#66bb6a"), "stopped": ("● Остановлена", "#ef5350"), "not_installed": ("● Не установлена", "#ffa726")}
        text, color = status_map.get(service_status, ("● Неизвестно", "gray"))
        self.card_service.configure(text=text, text_color=color)

        self.card_strategy.configure(text=strategy_name if strategy_name else "Не выбрана")


class StrategyPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        ctk.CTkLabel(self, text="⚡ Стратегии", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(self, text="Выберите стратегию для обхода блокировок", text_color="gray").pack(pady=(0, 20))

        self.strategies_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.strategies_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        self.strategy_var = ctk.StringVar(value="general")

        self.strategy_info = {
            "general": {"name": "General", "desc": "Базовая стратегия обхода. Подходит для большинства случаев."},
            "general_alt": {"name": "General (ALT)", "desc": "Альтернативная стратегия. Используйте если базовая не работает."},
            "general_fake": {"name": "General (FAKE TLS)", "desc": "Стратегия с подменой TLS handshake. Для сложных блокировок."}
        }

        self._build_strategies()

        self.desc_frame = ctk.CTkFrame(self, corner_radius=12)
        self.desc_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        self.desc_label = ctk.CTkLabel(
            self.desc_frame, text=self.strategy_info["general"]["desc"],
            wraplength=500, justify="left", font=ctk.CTkFont(size=12)
        )
        self.desc_label.pack(padx=15, pady=15)

    def _build_strategies(self):
        for widget in self.strategies_frame.winfo_children():
            widget.destroy()

        for key, info in self.strategy_info.items():
            card = ctk.CTkFrame(self.strategies_frame, corner_radius=10)
            card.pack(fill=tk.X, pady=5)

            rb = ctk.CTkRadioButton(
                card, text=info["name"], variable=self.strategy_var, value=key,
                font=ctk.CTkFont(size=14, weight="bold"),
                command=self._on_strategy_change
            )
            rb.pack(padx=15, pady=12, anchor="w")

    def _on_strategy_change(self):
        key = self.strategy_var.get()
        if key in self.strategy_info:
            self.desc_label.configure(text=self.strategy_info[key]["desc"])
        self.app.config.set("last_strategy", key)

    def get_selected(self):
        return self.strategy_var.get()


class ServicePage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        ctk.CTkLabel(self, text="⚙️ Службы", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(self, text="Управление службой Windows для автозапуска", text_color="gray").pack(pady=(0, 20))

        status_frame = ctk.CTkFrame(self, corner_radius=12)
        status_frame.pack(fill=tk.X, padx=20, pady=10)

        ctk.CTkLabel(status_frame, text="Статус службы:", font=ctk.CTkFont(size=14)).pack(padx=15, pady=(15, 5), anchor="w")
        self.status_label = ctk.CTkLabel(status_frame, text="Проверка...", font=ctk.CTkFont(size=18, weight="bold"))
        self.status_label.pack(padx=15, pady=(0, 15), anchor="w")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        self.btn_create = ctk.CTkButton(btn_frame, text="Создать службу", height=40, command=self._create_service)
        self.btn_create.pack(fill=tk.X, pady=5)

        self.btn_delete = ctk.CTkButton(btn_frame, text="Удалить службу", height=40, fg_color="#ef5350", hover_color="#e53935", command=self._delete_service)
        self.btn_delete.pack(fill=tk.X, pady=5)

        self.btn_start = ctk.CTkButton(btn_frame, text="Запустить службу", height=40, fg_color="#66bb6a", hover_color="#4caf50", command=self._start_service)
        self.btn_start.pack(fill=tk.X, pady=5)

        self.btn_stop = ctk.CTkButton(btn_frame, text="Остановить службу", height=40, fg_color="#ffa726", hover_color="#fb8c00", command=self._stop_service)
        self.btn_stop.pack(fill=tk.X, pady=5)

    def _create_service(self):
        strategy = self.app.strategy_page.get_selected()
        ok = self.app.service.create_service(strategy)
        self.app.log_panel.log("Служба создана" if ok else "Ошибка создания службы", "OK" if ok else "ERROR")
        self.update_status()

    def _delete_service(self):
        ok = self.app.service.delete_service()
        self.app.log_panel.log("Служба удалена" if ok else "Ошибка удаления", "OK" if ok else "ERROR")
        self.update_status()

    def _start_service(self):
        ok = self.app.service.start_service()
        self.app.log_panel.log("Служба запущена" if ok else "Ошибка запуска", "OK" if ok else "ERROR")
        self.update_status()

    def _stop_service(self):
        ok = self.app.service.stop_service()
        self.app.log_panel.log("Служба остановлена" if ok else "Ошибка остановки", "OK" if ok else "ERROR")
        self.update_status()

    def update_status(self):
        status = self.app.service.get_service_status()
        status_map = {"running": ("● Запущена", "#66bb6a"), "stopped": ("● Остановлена", "#ef5350"), "not_installed": ("● Не установлена", "#ffa726")}
        text, color = status_map.get(status, ("● Неизвестно", "gray"))
        self.status_label.configure(text=text, text_color=color)


class ListsPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        ctk.CTkLabel(self, text="📋 Списки доменов", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(self, text="Редактирование списков доменов и IP", text_color="gray").pack(pady=(0, 15))

        tabs = ctk.CTkTabview(self, corner_radius=10)
        tabs.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.editors = {}
        files = {
            "Основные домены": "lists/list-general.txt",
            "Пользовательские": "lists/list-general-user.txt",
            "IP адреса": "lists/ipset-all.txt"
        }

        for name, path in files.items():
            tab = tabs.add(name)
            text = scrolledtext.ScrolledText(
                tab, wrap=tk.WORD, font=("Consolas", 11),
                bg="#1a1a2e", fg="#e0e0e0", insertbackground="#e0e0e0"
            )
            text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.editors[path] = text

            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    text.insert("1.0", f.read())

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

        ctk.CTkButton(btn_frame, text="💾 Сохранить все", height=38, command=self._save_all).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        ctk.CTkButton(btn_frame, text="🔄 Обновить", height=38, fg_color="gray", command=self._reload_all).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

    def _save_all(self):
        for path, text in self.editors.items():
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text.get("1.0", tk.END).strip() + "\n")
        self.app.log_panel.log("Списки сохранены", "OK")

    def _reload_all(self):
        for path, text in self.editors.items():
            text.delete("1.0", tk.END)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    text.insert("1.0", f.read())
        self.app.log_panel.log("Списки обновлены", "INFO")


class AboutPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        ctk.CTkLabel(self, text="ℹ️ О программе", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 5))

        card = ctk.CTkFrame(self, corner_radius=15)
        card.pack(fill=tk.X, padx=30, pady=20)

        ctk.CTkLabel(card, text="AntiZapret", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(25, 5))
        ctk.CTkLabel(card, text="GUI Edition", font=ctk.CTkFont(size=14), text_color="gray").pack(pady=(0, 15))

        info = [
            ("Версия", "1.0.0"),
            ("Движок", "zapret (winws)"),
            ("Автор", "Ernest"),
            ("Лицензия", "MIT")
        ]

        for label, value in info:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill=tk.X, padx=20, pady=3)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=13), text_color="gray").pack(side=tk.LEFT)
            ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=13, weight="bold")).pack(side=tk.RIGHT)

        ctk.CTkLabel(card, text=" ", height=10).pack()

        links_frame = ctk.CTkFrame(card, fg_color="transparent")
        links_frame.pack(pady=(0, 20))

        ctk.CTkButton(links_frame, text="GitHub репозиторий", fg_color="gray", hover_color="#555",
                      command=lambda: os.system("start https://github.com/Ernest1101/AntiZapret")).pack(pady=3, fill=tk.X)
        ctk.CTkButton(links_frame, text="Оригинальный zapret", fg_color="gray", hover_color="#555",
                      command=lambda: os.system("start https://github.com/bol-van/zapret-win-bundle")).pack(pady=3, fill=tk.X)


class AntiZapretApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AntiZapret — GUI")
        self.geometry("900x650")
        self.minsize(800, 600)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.config = Config()
        self.service = ServiceManager()
        self.strategy_manager = StrategyManager()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_header()
        self._build_content()

        self.log_panel = LogPanel(self.content_area)
        self.pages = {
            "home": HomePage(self.content_area, self),
            "strategy": StrategyPage(self.content_area, self),
            "service": ServicePage(self.content_area, self),
            "lists": ListsPage(self.content_area, self),
            "logs": self.log_panel,
            "about": AboutPage(self.content_area, self),
        }

        last = self.config.get("last_strategy", "general")
        if hasattr(self.pages["strategy"], "strategy_var"):
            self.pages["strategy"].strategy_var.set(last)

        self._show_page("home")
        self.log_panel.log("AntiZapret запущен", "OK")
        self.log_panel.log(f"Права администратора: {'да' if is_admin() else 'нет'}", "INFO")

        self._update_status()

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(pady=(20, 25))
        ctk.CTkLabel(logo_frame, text="🛡️", font=ctk.CTkFont(size=32)).pack()
        ctk.CTkLabel(logo_frame, text="AntiZapret", font=ctk.CTkFont(size=16, weight="bold")).pack()

        nav_items = [
            ("home", "🏠  Главная"),
            ("strategy", "⚡  Стратегии"),
            ("service", "⚙️  Службы"),
            ("lists", "📋  Списки"),
            ("logs", "📝  Логи"),
            ("about", "ℹ️  О программе"),
        ]

        self.nav_buttons = {}
        for key, text in nav_items:
            btn = ctk.CTkButton(
                sidebar, text=text, anchor="w", height=40,
                fg_color="transparent", text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                command=lambda k=key: self._show_page(k)
            )
            btn.pack(fill=tk.X, padx=10, pady=2)
            self.nav_buttons[key] = btn

        spacer = ctk.CTkFrame(sidebar, fg_color="transparent")
        spacer.pack(fill=tk.BOTH, expand=True)

        ctk.CTkButton(
            sidebar, text="✕  Выход", anchor="w", height=40,
            fg_color="transparent", text_color="#ef5350",
            hover_color=("gray70", "gray30"),
            command=self._quit
        ).pack(fill=tk.X, padx=10, pady=(0, 15))

    def _build_header(self):
        header = ctk.CTkFrame(self, height=50, corner_radius=0)
        header.grid(row=0, column=1, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        self.page_title = ctk.CTkLabel(header, text="Главная", font=ctk.CTkFont(size=16, weight="bold"))
        self.page_title.grid(row=0, column=0, padx=20, pady=10)

        self.status_indicator = ctk.CTkLabel(header, text="● Остановлен", font=ctk.CTkFont(size=12), text_color="#ef5350")
        self.status_indicator.grid(row=0, column=2, padx=20, pady=10)

    def _build_content(self):
        self.content_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_area.grid(row=1, column=1, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

    def _show_page(self, page_key):
        titles = {"home": "Главная", "strategy": "Стратегии", "service": "Службы", "lists": "Списки доменов", "logs": "Логи", "about": "О программе"}
        self.page_title.configure(text=titles.get(page_key, ""))

        for btn in self.nav_buttons.values():
            btn.configure(fg_color="transparent")
        if page_key in self.nav_buttons:
            self.nav_buttons[page_key].configure(fg_color=("gray75", "gray25"))

        for page in self.pages.values():
            page.pack_forget()

        if page_key in self.pages:
            self.pages[page_key].pack(in_=self.content_area, fill=tk.BOTH, expand=True)

        if page_key == "service":
            self.pages["service"].update_status()

    def _update_status(self):
        running = self.service.is_running()
        service_status = self.service.get_service_status()
        strategy = self.config.get("last_strategy", "general")
        strategy_names = {"general": "General", "general_alt": "General (ALT)", "general_fake": "General (FAKE TLS)"}
        strategy_name = strategy_names.get(strategy, strategy)

        self.pages["home"].update_status(running, service_status, strategy_name)

        if running:
            self.status_indicator.configure(text="● Работает", text_color="#66bb6a")
        else:
            self.status_indicator.configure(text="● Остановлен", text_color="#ef5350")

        self.after(2000, self._update_status)

    def start_zapret(self):
        strategy = self.pages["strategy"].get_selected()
        self.log_panel.log(f"Запуск стратегии: {strategy}", "INFO")
        ok, msg = self.strategy_manager.run_strategy(strategy)
        self.log_panel.log(msg, "OK" if ok else "ERROR")

    def stop_zapret(self):
        self.log_panel.log("Остановка всех процессов...", "INFO")
        ok, msg = self.strategy_manager.stop_all()
        self.log_panel.log(msg, "OK" if ok else "ERROR")

    def _quit(self):
        self.log_panel.log("Завершение работы...", "INFO")
        self.after(300, self.destroy)


if __name__ == "__main__":
    app = AntiZapretApp()
    app.mainloop()
