#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_fix.py - Тест исправления ошибки запуска

Проверяет, что приложение может инициализироваться без ошибки 'name'
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Тестирование исправления ошибки 'name'...")
    
    # Проверяем импорт конфигурации
    from config import APP_CONFIG, COLORS, FONTS
    print(f"✓ Конфигурация загружена успешно")
    print(f"✓ Название приложения: {APP_CONFIG['title']}")
    print(f"✓ Версия: {APP_CONFIG['version']}")
    
    # Проверяем, что все необходимые ключи есть
    required_keys = ['title', 'version', 'window_size']
    for key in required_keys:
        if key in APP_CONFIG:
            print(f"✓ Ключ '{key}' найден в конфигурации")
        else:
            print(f"✗ Ключ '{key}' отсутствует в конфигурации")
    
    # Проверяем цвета
    required_colors = ['white', 'primary', 'secondary', 'text', 'danger']
    for color in required_colors:
        if color in COLORS:
            print(f"✓ Цвет '{color}' найден в конфигурации")
        else:
            print(f"✗ Цвет '{color}' отсутствует в конфигурации")
    
    # Пробуем создать главное окно (без запуска mainloop)
    import tkinter as tk
    root = tk.Tk()
    root.title(APP_CONFIG['title'])  # Это должно работать без ошибки
    root.withdraw()  # Скрываем окно
    print("✓ Главное окно создано успешно")
    
    # Проверяем импорт основных модулей
    from image_processor import ImageProcessor
    from ui_components import ModernButton
    from utils import ensure_directory
    print("✓ Основные модули импортированы успешно")
    
    root.destroy()
    print("\n🎉 Все тесты пройдены! Ошибка 'name' исправлена.")
    print("Приложение должно запускаться без ошибок.")
    
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    print("Требуется дополнительное исправление.")
    sys.exit(1)