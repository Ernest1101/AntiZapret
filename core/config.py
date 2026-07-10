#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль конфигурации
"""

import json
import os
from pathlib import Path


class Config:
    """Класс конфигурации приложения"""
    
    DEFAULT_CONFIG = {
        'last_strategy': 'general.bat',
        'auto_start': False,
        'game_filter': False,
        'ipset_filter': False,
        'lists_dir': 'lists',
        'bin_dir': 'bin',
        'log_level': 'INFO'
    }
    
    def __init__(self, config_file='config.json'):
        self.config_file = Path(config_file)
        self.config = self.load()
    
    def load(self):
        """Загрузка конфигурации"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.DEFAULT_CONFIG.copy()
        else:
            return self.DEFAULT_CONFIG.copy()
    
    def save(self):
        """Сохранение конфигурации"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
    
    def get(self, key, default=None):
        """Получение значения конфигурации"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Установка значения конфигурации"""
        self.config[key] = value
        self.save()
    
    def reset(self):
        """Сброс конфигурации"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
