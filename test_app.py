#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_app.py - Тестовый скрипт для проверки LogoMaster Pro

Проверяет:
- Импорт всех модулей
- Создание основных компонентов
- Базовую функциональность
"""

import sys
import os
import traceback
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """
    Тестирование импорта всех модулей
    """
    print("=== Тестирование импорта модулей ===")
    
    modules_to_test = [
        ('tkinter', 'Tkinter (GUI)'),
        ('PIL', 'Pillow (обработка изображений)'),
        ('numpy', 'NumPy (вычисления)'),
        ('requests', 'Requests (сеть)'),
        ('config', 'Конфигурация приложения'),
        ('image_processor', 'Обработчик изображений'),
        ('ui_components', 'UI компоненты'),
        ('utils', 'Утилиты'),
    ]
    
    failed_imports = []
    
    for module_name, description in modules_to_test:
        try:
            if module_name == 'tkinter':
                import tkinter as tk
                from tkinter import ttk, filedialog, messagebox
                print(f"✓ {description} - OK")
            elif module_name == 'PIL':
                from PIL import Image, ImageTk
                print(f"✓ {description} - OK")
            elif module_name == 'numpy':
                import numpy as np
                print(f"✓ {description} - OK")
            elif module_name == 'requests':
                import requests
                print(f"✓ {description} - OK")
            else:
                __import__(module_name)
                print(f"✓ {description} - OK")
                
        except ImportError as e:
            print(f"✗ {description} - ОШИБКА: {e}")
            failed_imports.append((module_name, description, str(e)))
        except Exception as e:
            print(f"✗ {description} - НЕОЖИДАННАЯ ОШИБКА: {e}")
            failed_imports.append((module_name, description, str(e)))
    
    return failed_imports

def test_config():
    """
    Тестирование конфигурации
    """
    print("\n=== Тестирование конфигурации ===")
    
    try:
        from config import (
            APP_CONFIG, COLORS, FONTS, SIZES, UI_CONFIG, MESSAGES,
            get_config, logger, setup_logging
        )
        
        print(f"✓ Название приложения: {APP_CONFIG['title']}")
        print(f"✓ Версия: {APP_CONFIG['version']}")
        print(f"✓ Размер окна: {APP_CONFIG['window_size']}")
        print(f"✓ Цветовая схема загружена: {len(COLORS)} цветов")
        print(f"✓ Шрифты загружены: {len(FONTS)} шрифтов")
        print(f"✓ Сообщения загружены: {len(MESSAGES)} сообщений")
        
        # Тестируем логирование
        setup_logging()
        logger.info("Тест логирования")
        print("✓ Логирование работает")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка конфигурации: {e}")
        traceback.print_exc()
        return False

def test_image_processor():
    """
    Тестирование обработчика изображений
    """
    print("\n=== Тестирование обработчика изображений ===")
    
    try:
        from image_processor import ImageProcessor
        
        processor = ImageProcessor()
        print("✓ ImageProcessor создан")
        
        # Тестируем создание тестового изображения
        from PIL import Image
        test_image = Image.new('RGB', (100, 100), color='red')
        print("✓ Тестовое изображение создано")
        
        # Тестируем получение информации
        info = processor._get_image_info_from_pil(test_image)
        print(f"✓ Информация об изображении: {info['dimensions']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка обработчика изображений: {e}")
        traceback.print_exc()
        return False

def test_ui_components():
    """
    Тестирование UI компонентов
    """
    print("\n=== Тестирование UI компонентов ===")
    
    try:
        import tkinter as tk
        from ui_components import (
            ModernButton, ImageViewer, ProgressDialog, 
            SettingsPanel, StatusBar
        )
        
        # Создаем тестовое окно
        root = tk.Tk()
        root.withdraw()  # Скрываем окно
        
        # Тестируем создание компонентов
        button = ModernButton(root, text="Тест", command=lambda: None)
        print("✓ ModernButton создан")
        
        viewer = ImageViewer(root)
        print("✓ ImageViewer создан")
        
        settings = SettingsPanel(root, on_change_callback=lambda x: None)
        print("✓ SettingsPanel создан")
        
        status = StatusBar(root)
        print("✓ StatusBar создан")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Ошибка UI компонентов: {e}")
        traceback.print_exc()
        return False

def test_utils():
    """
    Тестирование утилит
    """
    print("\n=== Тестирование утилит ===")
    
    try:
        from utils import (
            ensure_directory, validate_image_file, format_file_size,
            PerformanceTimer, get_unique_filename
        )
        
        # Тестируем форматирование размера файла
        size_str = format_file_size(1024 * 1024)
        print(f"✓ Форматирование размера: {size_str}")
        
        # Тестируем таймер производительности
        with PerformanceTimer("Тест") as timer:
            import time
            time.sleep(0.01)
        print(f"✓ Таймер производительности: {timer.get_duration():.3f} сек")
        
        # Тестируем создание уникального имени файла
        unique_name = get_unique_filename("/tmp", "test", ".txt")
        print(f"✓ Уникальное имя файла: {unique_name}")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка утилит: {e}")
        traceback.print_exc()
        return False

def test_main_app():
    """
    Тестирование главного приложения
    """
    print("\n=== Тестирование главного приложения ===")
    
    try:
        # Импортируем без запуска GUI
        import main
        print("✓ Модуль main импортирован")
        
        # Проверяем, что класс LogoMasterApp существует
        app_class = getattr(main, 'LogoMasterApp', None)
        if app_class:
            print("✓ Класс LogoMasterApp найден")
        else:
            print("✗ Класс LogoMasterApp не найден")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка главного приложения: {e}")
        traceback.print_exc()
        return False

def test_file_structure():
    """
    Проверка структуры файлов
    """
    print("\n=== Проверка структуры файлов ===")
    
    required_files = [
        'main.py',
        'config.py',
        'image_processor.py',
        'ui_components.py',
        'utils.py',
        'requirements.txt'
    ]
    
    current_dir = Path.cwd()
    missing_files = []
    
    for file_name in required_files:
        file_path = current_dir / file_name
        if file_path.exists():
            print(f"✓ {file_name} - найден")
        else:
            print(f"✗ {file_name} - НЕ НАЙДЕН")
            missing_files.append(file_name)
    
    return len(missing_files) == 0

def main():
    """
    Главная функция тестирования
    """
    print("LogoMaster Pro - Тестирование компонентов")
    print("=" * 50)
    
    # Информация о системе
    print(f"Python версия: {sys.version}")
    print(f"Рабочая директория: {os.getcwd()}")
    print(f"Путь к скрипту: {__file__}")
    print()
    
    # Запускаем тесты
    tests = [
        ("Структура файлов", test_file_structure),
        ("Импорт модулей", test_imports),
        ("Конфигурация", test_config),
        ("Обработчик изображений", test_image_processor),
        ("UI компоненты", test_ui_components),
        ("Утилиты", test_utils),
        ("Главное приложение", test_main_app),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed_tests += 1
                print(f"\n✓ {test_name} - ПРОЙДЕН")
            else:
                print(f"\n✗ {test_name} - ПРОВАЛЕН")
        except Exception as e:
            print(f"\n✗ {test_name} - ОШИБКА: {e}")
            traceback.print_exc()
    
    # Итоги
    print("\n" + "=" * 50)
    print(f"РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"Пройдено: {passed_tests}/{total_tests} тестов")
    
    if passed_tests == total_tests:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Приложение готово к запуску.")
        print("\nДля запуска приложения выполните:")
        print("python main.py")
        return True
    else:
        print(f"\n⚠️  НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ ({total_tests - passed_tests} из {total_tests})")
        print("\nПроверьте ошибки выше и установите недостающие зависимости.")
        print("\nДля установки зависимостей выполните:")
        print("pip install -r requirements.txt")
        return False

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nТестирование прервано пользователем.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nКритическая ошибка тестирования: {e}")
        traceback.print_exc()
        sys.exit(1)