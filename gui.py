#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AntiZapret GUI - Графический интерфейс для управления обходом блокировок
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os
import sys
import threading
from pathlib import Path

class AntiZapretGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AntiZapret - Обход блокировок DPI")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Проверка прав администратора
        if not self.is_admin():
            messagebox.showwarning(
                "Внимание",
                "Рекомендуется запустить программу от имени администратора!"
            )
        
        # Переменные состояния
        self.current_strategy = tk.StringVar(value="general.bat")
        self.is_running = False
        self.process = None
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка списка стратегий
        self.load_strategies()
        
    def is_admin(self):
        """Проверка прав администратора"""
        try:
            return os.getuid() == 0
        except AttributeError:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Заголовок
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(
            title_frame,
            text="🛡️ AntiZapret - Обход блокировок DPI",
            font=("Arial", 16, "bold")
        )
        title_label.pack()
        
        # Основная область с вкладками
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка "Стратегии"
        strategy_frame = ttk.Frame(notebook, padding="10")
        notebook.add(strategy_frame, text="🚀 Стратегии")
        self.create_strategy_tab(strategy_frame)
        
        # Вкладка "Службы"
        service_frame = ttk.Frame(notebook, padding="10")
        notebook.add(service_frame, text="⚙️ Службы")
        self.create_service_tab(service_frame)
        
        # Вкладка "Списки"
        lists_frame = ttk.Frame(notebook, padding="10")
        notebook.add(lists_frame, text="📋 Списки доменов")
        self.create_lists_tab(lists_frame)
        
        # Вкладка "Логи"
        logs_frame = ttk.Frame(notebook, padding="10")
        notebook.add(logs_frame, text="📊 Логи")
        self.create_logs_tab(logs_frame)
        
        # Статус бар
        status_frame = ttk.Frame(self.root, padding="5")
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Статус: Остановлен",
            foreground="red"
        )
        self.status_label.pack(side=tk.LEFT)
        
    def create_strategy_tab(self, parent):
        """Создание вкладки стратегий"""
        # Выбор стратегии
        strategy_select_frame = ttk.LabelFrame(parent, text="Выбор стратегии", padding="10")
        strategy_select_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(strategy_select_frame, text="Стратегия:").pack(side=tk.LEFT, padx=5)
        
        self.strategy_combo = ttk.Combobox(
            strategy_select_frame,
            textvariable=self.current_strategy,
            state="readonly",
            width=50
        )
        self.strategy_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Кнопки управления
        button_frame = ttk.Frame(parent, padding="10")
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(
            button_frame,
            text="▶️ Запустить",
            command=self.start_strategy,
            style="Accent.TButton"
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            button_frame,
            text="⏹️ Остановить",
            command=self.stop_strategy,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🔄 Обновить список",
            command=self.load_strategies
        ).pack(side=tk.LEFT, padx=5)
        
        # Информация о стратегии
        info_frame = ttk.LabelFrame(parent, text="Информация", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.info_text = scrolledtext.ScrolledText(
            info_frame,
            height=15,
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        self.info_text.insert(tk.END, "Выберите стратегию и нажмите 'Запустить'\n\n")
        self.info_text.insert(tk.END, "Доступные стратегии:\n")
        self.info_text.insert(tk.END, "- general.bat - базовая стратегия\n")
        self.info_text.insert(tk.END, "- general (ALT).bat - альтернативная стратегия\n")
        self.info_text.insert(tk.END, "- general (FAKE TLS).bat - стратегия с подменой TLS\n")
        self.info_text.insert(tk.END, "\nПробуйте разные стратегии, пока не найдете рабочую.\n")
        self.info_text.config(state=tk.DISABLED)
        
    def create_service_tab(self, parent):
        """Создание вкладки служб"""
        # Управление службами
        service_control_frame = ttk.LabelFrame(parent, text="Управление службами", padding="10")
        service_control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            service_control_frame,
            text="📥 Установить службу (автозапуск)",
            command=self.install_service,
            width=40
        ).pack(pady=5)
        
        ttk.Button(
            service_control_frame,
            text="🗑️ Удалить службы",
            command=self.remove_services,
            width=40
        ).pack(pady=5)
        
        ttk.Button(
            service_control_frame,
            text="🔍 Проверить статус",
            command=self.check_status,
            width=40
        ).pack(pady=5)
        
        # Дополнительные настройки
        settings_frame = ttk.LabelFrame(parent, text="Дополнительные настройки", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)
        
        self.game_filter_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            settings_frame,
            text="Игровой режим (Game Filter)",
            variable=self.game_filter_var,
            command=self.toggle_game_filter
        ).pack(anchor=tk.W, pady=2)
        
        self.ipset_filter_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            settings_frame,
            text="IPSet Filter",
            variable=self.ipset_filter_var,
            command=self.toggle_ipset_filter
        ).pack(anchor=tk.W, pady=2)
        
        # Информация
        info_frame = ttk.LabelFrame(parent, text="Информация", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        info_text = scrolledtext.ScrolledText(
            info_frame,
            height=10,
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        info_text.pack(fill=tk.BOTH, expand=True)
        
        info_text.insert(tk.END, "Управление службами:\n\n")
        info_text.insert(tk.END, "• Установить службу - добавляет выбранную стратегию в автозапуск\n")
        info_text.insert(tk.END, "• Удалить службы - удаляет все службы AntiZapret и WinDivert\n")
        info_text.insert(tk.END, "• Проверить статус - показывает текущее состояние служб\n\n")
        info_text.insert(tk.END, "Дополнительные настройки:\n")
        info_text.insert(tk.END, "• Игровой режим - обход для игр (UDP трафик)\n")
        info_text.insert(tk.END, "• IPSet Filter - фильтрация по IP адресам\n")
        info_text.config(state=tk.DISABLED)
        
    def create_lists_tab(self, parent):
        """Создание вкладки списков доменов"""
        # Выбор списка
        list_select_frame = ttk.Frame(parent, padding="5")
        list_select_frame.pack(fill=tk.X)
        
        ttk.Label(list_select_frame, text="Список:").pack(side=tk.LEFT, padx=5)
        
        self.list_combo = ttk.Combobox(
            list_select_frame,
            values=[
                "lists/list-general.txt",
                "lists/list-general-user.txt",
                "lists/ipset-all.txt"
            ],
            state="readonly",
            width=40
        )
        self.list_combo.pack(side=tk.LEFT, padx=5)
        self.list_combo.set("lists/list-general.txt")
        
        ttk.Button(
            list_select_frame,
            text="📂 Загрузить",
            command=self.load_list
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            list_select_frame,
            text="💾 Сохранить",
            command=self.save_list
        ).pack(side=tk.LEFT, padx=5)
        
        # Редактор списка
        list_editor_frame = ttk.LabelFrame(parent, text="Редактор списков", padding="10")
        list_editor_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.list_text = scrolledtext.ScrolledText(
            list_editor_frame,
            wrap=tk.NONE,
            font=("Consolas", 10)
        )
        self.list_text.pack(fill=tk.BOTH, expand=True)
        
        # Подсказка
        hint_label = ttk.Label(
            parent,
            text="💡 Каждый домен/IP на новой строке. Поддомены учитываются автоматически.",
            foreground="gray"
        )
        hint_label.pack(pady=5)
        
    def create_logs_tab(self, parent):
        """Создание вкладки логов"""
        # Кнопки управления логами
        log_control_frame = ttk.Frame(parent, padding="5")
        log_control_frame.pack(fill=tk.X)
        
        ttk.Button(
            log_control_frame,
            text="🗑️ Очистить логи",
            command=self.clear_logs
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            log_control_frame,
            text="💾 Сохранить логи",
            command=self.save_logs
        ).pack(side=tk.LEFT, padx=5)
        
        # Область логов
        log_frame = ttk.LabelFrame(parent, text="Логи выполнения", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#d4d4d4"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log_text.insert(tk.END, "[AntiZapret] Логи будут отображаться здесь...\n")
        self.log_text.config(state=tk.DISABLED)
        
    def load_strategies(self):
        """Загрузка списка доступных стратегий"""
        strategies = []
        
        # Поиск bat файлов в текущей директории
        for file in Path(".").glob("*.bat"):
            if file.name.startswith("general"):
                strategies.append(file.name)
        
        # Если не найдено, добавляем стандартные
        if not strategies:
            strategies = [
                "general.bat",
                "general (ALT).bat",
                "general (ALT2).bat",
                "general (FAKE TLS).bat",
                "general (SIMPLE FAKE).bat"
            ]
        
        self.strategy_combo['values'] = sorted(strategies)
        if strategies:
            self.strategy_combo.set(strategies[0])
        
        self.log(f"Загружено {len(strategies)} стратегий")
        
    def start_strategy(self):
        """Запуск выбранной стратегии"""
        strategy = self.current_strategy.get()
        
        if not os.path.exists(strategy):
            messagebox.showerror(
                "Ошибка",
                f"Файл стратегии не найден: {strategy}\n\n"
                f"Создайте файл стратегии или используйте service.bat"
            )
            return
        
        try:
            self.log(f"Запуск стратегии: {strategy}")
            
            # Запуск bat файла
            self.process = subprocess.Popen(
                ["cmd", "/c", "start", strategy],
                shell=True
            )
            
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="Статус: Запущен", foreground="green")
            
            self.log(f"✓ Стратегия {strategy} запущена")
            messagebox.showinfo("Успех", f"Стратегия {strategy} запущена!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить стратегию:\n{str(e)}")
            self.log(f"✗ Ошибка запуска: {str(e)}")
            
    def stop_strategy(self):
        """Остановка стратегии"""
        try:
            # Остановка процесса winws.exe
            subprocess.run(["taskkill", "/F", "/IM", "winws.exe"], 
                          capture_output=True, text=True)
            
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_label.config(text="Статус: Остановлен", foreground="red")
            
            self.log("Стратегия остановлена")
            messagebox.showinfo("Успех", "Стратегия остановлена!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось остановить:\n{str(e)}")
            
    def install_service(self):
        """Установка службы"""
        if not os.path.exists("service.bat"):
            messagebox.showerror(
                "Ошибка",
                "Файл service.bat не найден!\n\n"
                "Скачайте или создайте service.bat для управления службами."
            )
            return
        
        try:
            subprocess.Popen(["cmd", "/c", "start", "service.bat"])
            self.log("Открыт service.bat для установки службы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть service.bat:\n{str(e)}")
            
    def remove_services(self):
        """Удаление служб"""
        if messagebox.askyesno(
            "Подтверждение",
            "Вы уверены, что хотите удалить все службы AntiZapret?"
        ):
            try:
                subprocess.run(["sc", "stop", "AntiZapret"], capture_output=True)
                subprocess.run(["sc", "delete", "AntiZapret"], capture_output=True)
                subprocess.run(["sc", "stop", "WinDivert"], capture_output=True)
                subprocess.run(["sc", "delete", "WinDivert"], capture_output=True)
                
                self.log("Службы удалены")
                messagebox.showinfo("Успех", "Службы удалены!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить службы:\n{str(e)}")
                
    def check_status(self):
        """Проверка статуса служб"""
        try:
            result = subprocess.run(
                ["sc", "query", "AntiZapret"],
                capture_output=True,
                text=True
            )
            
            if "RUNNING" in result.stdout:
                status = "Служба AntiZapret: ЗАПУЩЕНА"
                self.status_label.config(text="Статус: Запущен", foreground="green")
            else:
                status = "Служба AntiZapret: ОСТАНОВЛЕНА"
                self.status_label.config(text="Статус: Остановлен", foreground="red")
            
            self.log(status)
            messagebox.showinfo("Статус", status)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось проверить статус:\n{str(e)}")
            
    def toggle_game_filter(self):
        """Переключение игрового режима"""
        state = "включен" if self.game_filter_var.get() else "выключен"
        self.log(f"Игровой режим: {state}")
        
    def toggle_ipset_filter(self):
        """Переключение IPSet фильтра"""
        state = "включен" if self.ipset_filter_var.get() else "выключен"
        self.log(f"IPSet Filter: {state}")
        
    def load_list(self):
        """Загрузка списка доменов"""
        list_file = self.list_combo.get()
        
        if not os.path.exists(list_file):
            # Создание файла если не существует
            os.makedirs(os.path.dirname(list_file), exist_ok=True)
            with open(list_file, "w", encoding="utf-8") as f:
                f.write("# Добавьте домены здесь\n")
        
        try:
            with open(list_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            self.list_text.delete(1.0, tk.END)
            self.list_text.insert(tk.END, content)
            self.log(f"Загружен список: {list_file}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить список:\n{str(e)}")
            
    def save_list(self):
        """Сохранение списка доменов"""
        list_file = self.list_combo.get()
        
        try:
            content = self.list_text.get(1.0, tk.END).strip()
            
            with open(list_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.log(f"Сохранен список: {list_file}")
            messagebox.showinfo("Успех", f"Список сохранен: {list_file}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить список:\n{str(e)}")
            
    def clear_logs(self):
        """Очистка логов"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def save_logs(self):
        """Сохранение логов в файл"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.log_text.get(1.0, tk.END))
                
                self.log(f"Логи сохранены: {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить логи:\n{str(e)}")
            
    def log(self, message):
        """Добавление сообщения в лог"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)


def main():
    """Главная функция"""
    root = tk.Tk()
    
    # Установка иконки (если есть)
    try:
        root.iconbitmap("icon.ico")
    except:
        pass
    
    # Применение темы
    style = ttk.Style()
    style.theme_use('clam')
    
    # Создание приложения
    app = AntiZapretGUI(root)
    
    # Обработчик закрытия
    def on_closing():
        if app.is_running:
            if messagebox.askokcancel(
                "Выход",
                "Стратегия все еще запущена. Остановить и выйти?"
            ):
                app.stop_strategy()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Запуск главного цикла
    root.mainloop()


if __name__ == "__main__":
    main()
