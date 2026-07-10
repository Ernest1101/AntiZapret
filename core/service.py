#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль управления службами Windows
"""

import subprocess
import os


class ServiceManager:
    """Менеджер служб Windows"""
    
    SERVICE_NAME = "AntiZapret"
    WINDIVERT_SERVICE = "WinDivert"
    
    def __init__(self):
        pass
    
    def install_service(self, strategy_path):
        """Установка службы"""
        try:
            # Создание службы
            subprocess.run(
                ["sc", "create", self.SERVICE_NAME,
                 "binPath=", f'"{strategy_path}"',
                 "start=", "auto",
                 "DisplayName=", "AntiZapret DPI Bypass"],
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Не удалось установить службу: {e.stderr}")
    
    def remove_service(self):
        """Удаление службы"""
        try:
            # Остановка службы
            subprocess.run(
                ["sc", "stop", self.SERVICE_NAME],
                capture_output=True,
                text=True
            )
            
            # Удаление службы
            subprocess.run(
                ["sc", "delete", self.SERVICE_NAME],
                check=True,
                capture_output=True,
                text=True
            )
            
            # Удаление WinDivert
            subprocess.run(
                ["sc", "stop", self.WINDIVERT_SERVICE],
                capture_output=True,
                text=True
            )
            
            subprocess.run(
                ["sc", "delete", self.WINDIVERT_SERVICE],
                capture_output=True,
                text=True
            )
            
            return True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Не удалось удалить службу: {e.stderr}")
    
    def start_service(self):
        """Запуск службы"""
        try:
            subprocess.run(
                ["sc", "start", self.SERVICE_NAME],
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Не удалось запустить службу: {e.stderr}")
    
    def stop_service(self):
        """Остановка службы"""
        try:
            subprocess.run(
                ["sc", "stop", self.SERVICE_NAME],
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Не удалось остановить службу: {e.stderr}")
    
    def get_status(self):
        """Получение статуса службы"""
        try:
            result = subprocess.run(
                ["sc", "query", self.SERVICE_NAME],
                capture_output=True,
                text=True
            )
            
            if "RUNNING" in result.stdout:
                return "RUNNING"
            elif "STOPPED" in result.stdout:
                return "STOPPED"
            else:
                return "NOT_INSTALLED"
        except:
            return "NOT_INSTALLED"
    
    def is_installed(self):
        """Проверка установки службы"""
        return self.get_status() != "NOT_INSTALLED"
    
    def is_running(self):
        """Проверка запуска службы"""
        return self.get_status() == "RUNNING"
