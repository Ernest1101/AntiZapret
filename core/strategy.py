#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль управления стратегиями
"""

import os
import subprocess
from pathlib import Path


class StrategyManager:
    """Менеджер стратегий обхода"""
    
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.strategies = {}
        self.load_strategies()
    
    def load_strategies(self):
        """Загрузка списка доступных стратегий"""
        self.strategies = {}
        
        for bat_file in self.base_dir.glob("*.bat"):
            if bat_file.name.startswith("general"):
                self.strategies[bat_file.name] = {
                    'path': str(bat_file),
                    'name': bat_file.stem,
                    'description': self._get_strategy_description(bat_file.name)
                }
    
    def _get_strategy_description(self, filename):
        """Получение описания стратегии"""
        descriptions = {
            'general.bat': 'Базовая стратегия обхода',
            'general (ALT).bat': 'Альтернативная стратегия',
            'general (ALT2).bat': 'Альтернативная стратегия 2',
            'general (FAKE TLS).bat': 'Стратегия с подменой TLS handshake',
            'general (SIMPLE FAKE).bat': 'Упрощенная fake стратегия'
        }
        return descriptions.get(filename, 'Пользовательская стратегия')
    
    def get_strategy(self, name):
        """Получение информации о стратегии"""
        return self.strategies.get(name)
    
    def list_strategies(self):
        """Получение списка всех стратегий"""
        return list(self.strategies.keys())
    
    def run_strategy(self, strategy_name):
        """Запуск стратегии"""
        strategy = self.get_strategy(strategy_name)
        if not strategy:
            raise ValueError(f"Стратегия не найдена: {strategy_name}")
        
        try:
            process = subprocess.Popen(
                ["cmd", "/c", "start", strategy['path']],
                shell=True
            )
            return process
        except Exception as e:
            raise RuntimeError(f"Не удалось запустить стратегию: {str(e)}")
    
    def stop_strategy(self):
        """Остановка текущей стратегии"""
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", "winws.exe"],
                capture_output=True,
                text=True
            )
            return True
        except Exception as e:
            raise RuntimeError(f"Не удалось остановить стратегию: {str(e)}")
    
    def is_running(self):
        """Проверка, запущена ли стратегия"""
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq winws.exe"],
                capture_output=True,
                text=True
            )
            return "winws.exe" in result.stdout
        except:
            return False
