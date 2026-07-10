#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AntiZapret GUI - Современный интерфейс для обхода DPI
С использованием CustomTkinter и автозапросом прав администратора
"""

import sys
import os
import ctypes
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime

# Проверка и запрос прав администратора
def is_admin():
    """Проверка, запущена ли программа с правами администратора"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Перезапуск программы с правами администратора"""
    if not is_admin():
        try:
            script = os.path.abspath(sys.argv[0])
            params = ' '.join(sys.argv[1:])
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{script}" {params}', None, 1
            )
            sys.exit()
        except Exception as e:
            print(f"Не удалось получить права администратора: {e}")
            print("Программа требует прав администратора для работы!")
            input("Нажмите Enter для выхода...")
            sys.exit(1)

# Запрашиваем права администратора при запуске
run_as_admin()

# Импортируем customtkinter после проверки прав
import customtkinter as ctk
from tkinter import messagebox, filedialog, scrolledtext

# Импортируем наши модули
from core.strategy import StrategyManager
from core.service import ServiceManager
from core.config import Config


class AntiZapretGUI(ctk.CTk):
    """Главное окно приложения AntiZapret"""
    
    def __init__(self):
        super().__init__()
        
        # Настройка окна
        self.title("AntiZapret - Обход DPI блокировок")
        self.geometry("1000x650")
        self.minsize(900, 600)
        
        # Настройка темы
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Инициализация менеджеров
        self.base_dir = Path(__file__).parent
        self.config = Config(str(self.base_dir / 'config.json'))
        self.strategy_manager = StrategyManager(self.base_dir)
        self.service_manager = ServiceManager()
        
        # Переменные состояния
        self.current_process = None
        self.is_running = False
        self.log_buffer = []
        
        # Создание интерфейса
        self._create_ui()
        
        # Запуск обновления статуса
        self._update_status_loop()
        
        # Обработчик закрытия
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_ui(self):
        """Создание пользовательского интерфейса"""
        
        # Контейнер для боковой панели и основного контента
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # === БОКОВАЯ ПАНЕЛЬ ===
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)
        
        # Логотип/Заголовок
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="🛡️ AntiZapret",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Версия
        self.version_label = ctk.CTkLabel(
            self.sidebar,
            text="v1.0.0",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.version_label.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        # Кнопки навигации
        nav_buttons = [
            ("🏠  Главная", self._show_home),
            ("⚡  Стратегии", self._show_strategies),
            ("⚙️  Службы", self._show_services),
            ("📋  Списки доменов", self._show_lists),
            ("📝  Логи", self._show_logs),
            ("ℹ️  О программе", self._show_about),
        ]
        
        self.nav_buttons = []
        for i, (text, command) in enumerate(nav_buttons):
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                anchor="w",
                height=40,
                font=ctk.CTkFont(size=13),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30")
            )
            btn.grid(row=i+2, column=0, padx=10, pady=3, sticky="ew")
            self.nav_buttons.append(btn)
        
        # Статус внизу боковой панели
        self.admin_status = ctk.CTkLabel(
            self.sidebar,
            text="👑 Администратор",
            font=ctk.CTkFont(size=11),
            text_color="#2ecc71" if is_admin() else "#e74c3c"
        )
        self.admin_status.grid(row=7, column=0, padx=20, pady=10, sticky="s")
        
        # === ОСНОВНОЙ КОНТЕНТ ===
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Заголовок основной области
        self.header_frame = ctk.CTkFrame(self.main_frame, height=60, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        self.page_title = ctk.CTkLabel(
            self.header_frame,
            text="🏠 Главная",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.page_title.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Индикатор статуса
        self.status_indicator = ctk.CTkLabel(
            self.header_frame,
            text="● Остановлено",
            font=ctk.CTkFont(size=13),
            text_color="#e74c3c"
        )
        self.status_indicator.grid(row=0, column=1, padx=20, pady=15, sticky="e")
        
        # Контейнер для страниц
        self.content_frame = ctk.CTkFrame(self.main_frame, corner_radius=0)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Создание страниц
        self.pages = {}
        self._create_home_page()
        self._create_strategies_page()
        self._create_services_page()
        self._create_lists_page()
        self._create_logs_page()
        self._create_about_page()
        
        # Показываем главную страницу
        self._show_home()
    
    def _create_home_page(self):
        """Создание главной страницы"""
        page = ctk.CTkScrollableFrame(self.content_frame)
        self.pages['home'] = page
        
        # Приветствие
        welcome = ctk.CTkLabel(
            page,
            text="Добро пожаловать в AntiZapret!",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        welcome.pack(pady=(20, 10), padx=20, anchor="w")
        
        description = ctk.CTkLabel(
            page,
            text="Инструмент для обхода DPI блокировок с помощью стратегий zapret",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        description.pack(pady=(0, 30), padx=20, anchor="w")
        
        # Карточки с информацией
        cards_frame = ctk.CTkFrame(page, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20, pady=10)
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")
        
        # Карточка 1: Стратегия
        card1 = ctk.CTkFrame(cards_frame)
        card1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(card1, text="⚡", font=ctk.CTkFont(size=32)).pack(pady=(15, 5))
        ctk.CTkLabel(card1, text="Стратегия", font=ctk.CTkFont(size=14, weight="bold")).pack()
        self.home_strategy_label = ctk.CTkLabel(
            card1, 
            text=self.config.get('last_strategy', 'general.bat'),
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.home_strategy_label.pack(pady=(5, 15))
        
        # Карточка 2: Служба
        card2 = ctk.CTkFrame(cards_frame)
        card2.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(card2, text="⚙️", font=ctk.CTkFont(size=32)).pack(pady=(15, 5))
        ctk.CTkLabel(card2, text="Служба", font=ctk.CTkFont(size=14, weight="bold")).pack()
        self.home_service_label = ctk.CTkLabel(
            card2,
            text="Не установлена",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.home_service_label.pack(pady=(5, 15))
        
        # Карточка 3: Статус
        card3 = ctk.CTkFrame(cards_frame)
        card3.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(card3, text="📊", font=ctk.CTkFont(size=32)).pack(pady=(15, 5))
        ctk.CTkLabel(card3, text="Статус", font=ctk.CTkFont(size=14, weight="bold")).pack()
        self.home_status_label = ctk.CTkLabel(
            card3,
            text="Остановлено",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.home_status_label.pack(pady=(5, 15))
        
        # Быстрые действия
        actions_frame = ctk.CTkFrame(page, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            actions_frame,
            text="Быстрые действия",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(0, 10))
        
        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        self.home_start_btn = ctk.CTkButton(
            buttons_frame,
            text="▶ Запустить стратегию",
            command=self._quick_start,
            height=45,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#27ae60",
            hover_color="#229954"
        )
        self.home_start_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        self.home_stop_btn = ctk.CTkButton(
            buttons_frame,
            text="⏹ Остановить",
            command=self._quick_stop,
            height=45,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        self.home_stop_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        # Информация
        info_frame = ctk.CTkFrame(page)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="💡 Подсказка",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            info_frame,
            text="Для работы программы необходимо:\n"
                 "1. Установить зависимости: pip install -r requirements.txt\n"
                 "2. Поместить файлы zapret (winws.exe, WinDivert) в папку bin/\n"
                 "3. Запускать от имени администратора",
            font=ctk.CTkFont(size=12),
            justify="left",
            text_color="gray"
        ).pack(anchor="w", padx=15, pady=(0, 15))
    
    def _create_strategies_page(self):
        """Создание страницы стратегий"""
        page = ctk.CTkScrollableFrame(self.content_frame)
        self.pages['strategies'] = page
        
        ctk.CTkLabel(
            page,
            text="Выбор стратегии обхода",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(20, 10), padx=20, anchor="w")
        
        # Список стратегий
        self.strategies_frame = ctk.CTkFrame(page)
        self.strategies_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self._refresh_strategies_list()
        
        # Кнопки управления
        buttons_frame = ctk.CTkFrame(page, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=10)
        
        self.strategy_run_btn = ctk.CTkButton(
            buttons_frame,
            text="▶ Запустить выбранную стратегию",
            command=self._run_selected_strategy,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#27ae60",
            hover_color="#229954"
        )
        self.strategy_run_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        self.strategy_stop_btn = ctk.CTkButton(
            buttons_frame,
            text="⏹ Остановить",
            command=self._stop_strategy,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        self.strategy_stop_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(
            buttons_frame,
            text="🔄 Обновить",
            command=self._refresh_strategies_list,
            height=40,
            width=100
        ).pack(side="right", padx=5)
    
    def _create_services_page(self):
        """Создание страницы служб"""
        page = ctk.CTkScrollableFrame(self.content_frame)
        self.pages['services'] = page
        
        ctk.CTkLabel(
            page,
            text="Управление службой Windows",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(20, 10), padx=20, anchor="w")
        
        # Статус службы
        status_frame = ctk.CTkFrame(page)
        status_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            status_frame,
            text="Статус службы:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.service_status_label = ctk.CTkLabel(
            status_frame,
            text="Проверка...",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.service_status_label.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Описание
        desc_frame = ctk.CTkFrame(page)
        desc_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            desc_frame,
            text="ℹ️ О службе",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            desc_frame,
            text="Служба позволяет автоматически запускать выбранную стратегию\n"
                 "при старте Windows. Это удобно, если вам нужен постоянный\n"
                 "обход блокировок без ручного запуска программы.",
            font=ctk.CTkFont(size=12),
            justify="left",
            text_color="gray"
        ).pack(anchor="w", padx=15, pady=(0, 15))
        
        # Кнопки управления службой
        buttons_frame = ctk.CTkFrame(page, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(
            buttons_frame,
            text="📥 Установить службу",
            command=self._install_service,
            height=40,
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=5, pady=5, fill="x", expand=True)
        
        ctk.CTkButton(
            buttons_frame,
            text="▶ Запустить службу",
            command=self._start_service,
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color="#27ae60",
            hover_color="#229954"
        ).pack(side="left", padx=5, pady=5, fill="x", expand=True)
        
        ctk.CTkButton(
            buttons_frame,
            text="⏹ Остановить службу",
            command=self._stop_service,
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color="#e67e22",
            hover_color="#d35400"
        ).pack(side="left", padx=5, pady=5, fill="x", expand=True)
        
        ctk.CTkButton(
            buttons_frame,
            text="🗑️ Удалить службу",
            command=self._remove_service,
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color="#e74c3c",
            hover_color="#c0392b"
        ).pack(side="left", padx=5, pady=5, fill="x", expand=True)
    
    def _create_lists_page(self):
        """Создание страницы списков доменов"""
        page = ctk.CTkFrame(self.content_frame)
        self.pages['lists'] = page
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)
        
        # Верхняя панель
        top_frame = ctk.CTkFrame(page, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            top_frame,
            text="Списки доменов и IP",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # Выбор файла
        files_frame = ctk.CTkFrame(page)
        files_frame.grid(row=0, column=0, sticky="e", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(files_frame, text="Файл:").pack(side="left", padx=5)
        
        self.list_file_var = ctk.StringVar(value="list-general.txt")
        self.list_file_menu = ctk.CTkOptionMenu(
            files_frame,
            variable=self.list_file_var,
            values=["list-general.txt", "list-general-user.txt", "ipset-all.txt"],
            command=self._load_list_file,
            width=200
        )
        self.list_file_menu.pack(side="left", padx=5)
        
        ctk.CTkButton(
            files_frame,
            text="💾 Сохранить",
            command=self._save_list_file,
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            files_frame,
            text="🔄 Обновить",
            command=self._load_list_file,
            width=100
        ).pack(side="left", padx=5)
        
        # Текстовое поле для редактирования
        self.list_text = ctk.CTkTextbox(page, font=ctk.CTkFont(size=12, family="Consolas"))
        self.list_text.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Загружаем первый файл
        self.after(100, self._load_list_file)
    
    def _create_logs_page(self):
        """Создание страницы логов"""
        page = ctk.CTkFrame(self.content_frame)
        self.pages['logs'] = page
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)
        
        # Заголовок
        header_frame = ctk.CTkFrame(page, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="Журнал событий",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            header_frame,
            text="🗑️ Очистить",
            command=self._clear_logs,
            width=100
        ).pack(side="right")
        
        # Текстовое поле для логов
        self.log_text = ctk.CTkTextbox(
            page, 
            font=ctk.CTkFont(size=11, family="Consolas"),
            state="disabled"
        )
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Начальное сообщение
        self._add_log("AntiZapret GUI запущен")
        self._add_log(f"Рабочая директория: {self.base_dir}")
        self._add_log(f"Права администратора: {'Да' if is_admin() else 'Нет'}")
    
    def _create_about_page(self):
        """Создание страницы 'О программе'"""
        page = ctk.CTkScrollableFrame(self.content_frame)
        self.pages['about'] = page
        
        # Логотип
        ctk.CTkLabel(
            page,
            text="🛡️",
            font=ctk.CTkFont(size=64)
        ).pack(pady=(30, 10))
        
        ctk.CTkLabel(
            page,
            text="AntiZapret",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=5)
        
        ctk.CTkLabel(
            page,
            text="Версия 1.0.0",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        ).pack(pady=5)
        
        ctk.CTkLabel(
            page,
            text="Современный GUI для обхода DPI блокировок\nна базе zapret от bol-van",
            font=ctk.CTkFont(size=13),
            justify="center",
            text_color="gray"
        ).pack(pady=20)
        
        # Информация
        info_frame = ctk.CTkFrame(page)
        info_frame.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="📦 Используемые компоненты",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        info_text = (
            "• zapret-win-bundle от bol-van\n"
            "• CustomTkinter - современная GUI библиотека\n"
            "• WinDivert - драйвер для перехвата пакетов\n\n"
            "📝 Лицензия: MIT\n"
            "🔗 GitHub: github.com/Ernest1101/AntiZapret"
        )
        
        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 15))
    
    # === МЕТОДЫ НАВИГАЦИИ ===
    
    def _show_page(self, page_name, title):
        """Показать указанную страницу"""
        # Скрыть все страницы
        for page in self.pages.values():
            page.grid_forget()
        
        # Показать нужную
        self.pages[page_name].grid(row=0, column=0, sticky="nsew")
        
        # Обновить заголовок
        self.page_title.configure(text=title)
        
        # Обновить выделение кнопки
        page_map = {
            'home': 0, 'strategies': 1, 'services': 2,
            'lists': 3, 'logs': 4, 'about': 5
        }
        for i, btn in enumerate(self.nav_buttons):
            if i == page_map.get(page_name, -1):
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")
    
    def _show_home(self):
        self._show_page('home', "🏠 Главная")
        self._update_home_info()
    
    def _show_strategies(self):
        self._show_page('strategies', "⚡ Стратегии")
    
    def _show_services(self):
        self._show_page('services', "⚙️ Службы")
        self._update_service_status()
    
    def _show_lists(self):
        self._show_page('lists', "📋 Списки доменов")
    
    def _show_logs(self):
        self._show_page('logs', "📝 Логи")
    
    def _show_about(self):
        self._show_page('about', "ℹ️ О программе")
    
    # === МЕТОДЫ СТРАТЕГИЙ ===
    
    def _refresh_strategies_list(self):
        """Обновление списка стратегий"""
        self.strategy_manager.load_strategies()
        
        # Очистить старый список
        for widget in self.strategies_frame.winfo_children():
            widget.destroy()
        
        strategies = self.strategy_manager.list_strategies()
        
        if not strategies:
            ctk.CTkLabel(
                self.strategies_frame,
                text="Стратегии не найдены!\n\nУбедитесь, что файлы .bat находятся в корне репозитория.",
                font=ctk.CTkFont(size=13),
                text_color="gray"
            ).pack(pady=40)
            return
        
        self.strategy_var = ctk.StringVar()
        last = self.config.get('last_strategy', strategies[0])
        if last in strategies:
            self.strategy_var.set(last)
        
        for strategy_name in strategies:
            strategy = self.strategy_manager.get_strategy(strategy_name)
            
            card = ctk.CTkFrame(self.strategies_frame)
            card.pack(fill="x", padx=5, pady=5)
            
            # Радио-кнопка для выбора
            radio = ctk.CTkRadioButton(
                card,
                text=strategy['name'],
                variable=self.strategy_var,
                value=strategy_name,
                font=ctk.CTkFont(size=13, weight="bold")
            )
            radio.pack(anchor="w", padx=15, pady=(10, 2))
            
            # Описание
            ctk.CTkLabel(
                card,
                text=strategy['description'],
                font=ctk.CTkFont(size=11),
                text_color="gray"
            ).pack(anchor="w", padx=40, pady=(0, 10))
    
    def _run_selected_strategy(self):
        """Запуск выбранной стратегии"""
        if not hasattr(self, 'strategy_var') or not self.strategy_var.get():
            messagebox.showwarning("Внимание", "Выберите стратегию!")
            return
        
        strategy_name = self.strategy_var.get()
        self.config.set('last_strategy', strategy_name)
        
        self._add_log(f"Запуск стратегии: {strategy_name}")
        
        try:
            self.current_process = self.strategy_manager.run_strategy(strategy_name)
            self.is_running = True
            self._update_status_indicator(True)
            self._add_log(f"✓ Стратегия запущена")
        except Exception as e:
            self._add_log(f"✗ Ошибка запуска: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось запустить стратегию:\n{str(e)}")
    
    def _stop_strategy(self):
        """Остановка стратегии"""
        self._add_log("Остановка стратегии...")
        try:
            self.strategy_manager.stop_strategy()
            self.is_running = False
            self._update_status_indicator(False)
            self._add_log("✓ Стратегия остановлена")
        except Exception as e:
            self._add_log(f"✗ Ошибка остановки: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось остановить:\n{str(e)}")
    
    def _quick_start(self):
        """Быстрый запуск последней стратегии"""
        last = self.config.get('last_strategy')
        if last and last in self.strategy_manager.strategies:
            self.strategy_var = ctk.StringVar(value=last)
            self._run_selected_strategy()
        else:
            messagebox.showinfo("Информация", "Сначала выберите стратегию во вкладке 'Стратегии'")
            self._show_strategies()
    
    def _quick_stop(self):
        """Быстрая остановка"""
        self._stop_strategy()
    
    # === МЕТОДЫ СЛУЖБ ===
    
    def _update_service_status(self):
        """Обновление статуса службы"""
        status = self.service_manager.get_status()
        status_map = {
            "RUNNING": ("● Служба запущена", "#2ecc71"),
            "STOPPED": ("● Служба остановлена", "#e67e22"),
            "NOT_INSTALLED": ("● Служба не установлена", "#e74c3c")
        }
        text, color = status_map.get(status, ("● Неизвестно", "gray"))
        self.service_status_label.configure(text=text, text_color=color)
    
    def _install_service(self):
        """Установка службы"""
        last = self.config.get('last_strategy', 'general.bat')
        strategy_path = self.base_dir / last
        
        if not strategy_path.exists():
            messagebox.showerror("Ошибка", f"Файл стратегии не найден:\n{strategy_path}")
            return
        
        if messagebox.askyesno("Подтверждение", f"Установить службу со стратегией:\n{last}?"):
            try:
                self.service_manager.install_service(str(strategy_path))
                self._add_log(f"✓ Служба установлена: {last}")
                self._update_service_status()
                messagebox.showinfo("Успех", "Служба успешно установлена!")
            except Exception as e:
                self._add_log(f"✗ Ошибка установки службы: {str(e)}")
                messagebox.showerror("Ошибка", str(e))
    
    def _remove_service(self):
        """Удаление службы"""
        if messagebox.askyesno("Подтверждение", "Удалить службу AntiZapret?"):
            try:
                self.service_manager.remove_service()
                self._add_log("✓ Служба удалена")
                self._update_service_status()
                messagebox.showinfo("Успех", "Служба удалена!")
            except Exception as e:
                self._add_log(f"✗ Ошибка удаления: {str(e)}")
                messagebox.showerror("Ошибка", str(e))
    
    def _start_service(self):
        """Запуск службы"""
        try:
            self.service_manager.start_service()
            self._add_log("✓ Служба запущена")
            self._update_service_status()
        except Exception as e:
            self._add_log(f"✗ Ошибка запуска: {str(e)}")
            messagebox.showerror("Ошибка", str(e))
    
    def _stop_service(self):
        """Остановка службы"""
        try:
            self.service_manager.stop_service()
            self._add_log("✓ Служба остановлена")
            self._update_service_status()
        except Exception as e:
            self._add_log(f"✗ Ошибка остановки: {str(e)}")
            messagebox.showerror("Ошибка", str(e))
    
    # === МЕТОДЫ СПИСКОВ ===
    
    def _load_list_file(self, *args):
        """Загрузка файла списка"""
        filename = self.list_file_var.get()
        filepath = self.base_dir / "lists" / filename
        
        self.list_text.delete("1.0", "end")
        
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.list_text.insert("1.0", content)
                self._add_log(f"Загружен файл: {filename}")
            except Exception as e:
                self.list_text.insert("1.0", f"Ошибка загрузки: {str(e)}")
        else:
            self.list_text.insert("1.0", "# Файл не найден\n# Создайте новый список")
    
    def _save_list_file(self):
        """Сохранение файла списка"""
        filename = self.list_file_var.get()
        filepath = self.base_dir / "lists" / filename
        
        try:
            content = self.list_text.get("1.0", "end").strip()
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self._add_log(f"✓ Сохранён файл: {filename}")
            messagebox.showinfo("Успех", f"Файл сохранён:\n{filename}")
        except Exception as e:
            self._add_log(f"✗ Ошибка сохранения: {str(e)}")
            messagebox.showerror("Ошибка", str(e))
    
    # === МЕТОДЫ ЛОГОВ ===
    
    def _add_log(self, message):
        """Добавление сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_buffer.append(log_entry)
        
        if hasattr(self, 'log_text'):
            self.log_text.configure(state="normal")
            self.log_text.insert("end", log_entry)
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
    
    def _clear_logs(self):
        """Очистка логов"""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self.log_buffer.clear()
        self._add_log("Логи очищены")
    
    # === ОБНОВЛЕНИЕ СТАТУСА ===
    
    def _update_status_indicator(self, running):
        """Обновление индикатора статуса"""
        if running:
            self.status_indicator.configure(text="● Запущено", text_color="#2ecc71")
        else:
            self.status_indicator.configure(text="● Остановлено", text_color="#e74c3c")
    
    def _update_home_info(self):
        """Обновление информации на главной странице"""
        # Стратегия
        last = self.config.get('last_strategy', 'general.bat')
        self.home_strategy_label.configure(text=last)
        
        # Служба
        status = self.service_manager.get_status()
        status_text = {
            "RUNNING": "Запущена",
            "STOPPED": "Остановлена",
            "NOT_INSTALLED": "Не установлена"
        }.get(status, "Неизвестно")
        self.home_service_label.configure(text=status_text)
        
        # Статус
        running = self.strategy_manager.is_running()
        self.home_status_label.configure(
            text="Работает" if running else "Остановлено",
            text_color="#2ecc71" if running else "gray"
        )
        self._update_status_indicator(running)
    
    def _update_status_loop(self):
        """Цикл обновления статуса"""
        try:
            # Проверяем, запущен ли winws.exe
            running = self.strategy_manager.is_running()
            if running != self.is_running:
                self.is_running = running
                self._update_status_indicator(running)
                if running:
                    self._add_log("Стратегия запущена (обнаружен winws.exe)")
                else:
                    self._add_log("Стратегия остановлена")
            
            # Обновляем главную страницу если она видима
            if self.pages['home'].winfo_ismapped():
                self._update_home_info()
            
            # Обновляем статус службы если страница видима
            if self.pages['services'].winfo_ismapped():
                self._update_service_status()
        
        except Exception as e:
            pass
        
        # Повторяем каждые 2 секунды
        self.after(2000, self._update_status_loop)
    
    def _on_closing(self):
        """Обработчик закрытия окна"""
        if self.is_running:
            if messagebox.askyesno("Подтверждение", 
                "Стратегия всё ещё запущена!\nОстановить перед выходом?"):
                self._stop_strategy()
        self.destroy()


def main():
    """Главная функция"""
    app = AntiZapretGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
