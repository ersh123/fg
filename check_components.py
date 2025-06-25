#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка компонентов LogoMaster Pro без GUI
"""

import sys
import os

def check_python_version():
    """Проверка версии Python"""
    print(f"Python версия: {sys.version}")
    if sys.version_info >= (3, 8):
        print("✓ Версия Python подходит")
        return True
    else:
        print("✗ Требуется Python 3.8 или выше")
        return False

def check_imports():
    """Проверка импорта модулей"""
    modules = {
        'tkinter': 'Tkinter GUI',
        'PIL': 'Pillow (обработка изображений)',
        'numpy': 'NumPy (математические операции)',
        'requests': 'Requests (HTTP запросы)',
        'json': 'JSON (встроенный)',
        'threading': 'Threading (встроенный)',
        'os': 'OS (встроенный)',
        'sys': 'Sys (встроенный)'
    }
    
    success = True
    for module, description in modules.items():
        try:
            __import__(module)
            print(f"✓ {module} - {description}")
        except ImportError as e:
            print(f"✗ {module} - {description} - ОШИБКА: {e}")
            success = False
    
    return success

def check_project_files():
    """Проверка наличия файлов проекта"""
    required_files = [
        'main.py',
        'config.py', 
        'image_processor.py',
        'ui_components.py',
        'utils.py',
        'requirements.txt'
    ]
    
    success = True
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✓ {file} ({size} байт)")
        else:
            print(f"✗ {file} - ОТСУТСТВУЕТ")
            success = False
    
    return success

def check_config():
    """Проверка конфигурации"""
    try:
        import config
        print(f"✓ Конфигурация загружена")
        print(f"  - Название: {config.APP_CONFIG.get('name', 'Не указано')}")
        print(f"  - Версия: {config.APP_CONFIG.get('version', 'Не указано')}")
        return True
    except Exception as e:
        print(f"✗ Ошибка загрузки конфигурации: {e}")
        return False

def check_image_processor():
    """Проверка модуля обработки изображений"""
    try:
        from image_processor import ImageProcessor
        processor = ImageProcessor()
        print("✓ ImageProcessor создан успешно")
        return True
    except Exception as e:
        print(f"✗ Ошибка создания ImageProcessor: {e}")
        return False

def check_utils():
    """Проверка утилит"""
    try:
        import utils
        print("✓ Модуль utils загружен")
        # Проверим несколько функций
        test_size = utils.format_file_size(1024)
        print(f"  - Форматирование размера: {test_size}")
        return True
    except Exception as e:
        print(f"✗ Ошибка загрузки utils: {e}")
        return False

def main():
    """Основная функция проверки"""
    print("=" * 60)
    print("ПРОВЕРКА КОМПОНЕНТОВ LOGOMASTER PRO")
    print("=" * 60)
    
    checks = [
        ("Версия Python", check_python_version),
        ("Импорт модулей", check_imports),
        ("Файлы проекта", check_project_files),
        ("Конфигурация", check_config),
        ("Обработчик изображений", check_image_processor),
        ("Утилиты", check_utils)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n--- {name} ---")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"✗ Критическая ошибка: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ПРОВЕРКИ")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (name, _) in enumerate(checks):
        status = "✓ ПРОЙДЕНО" if results[i] else "✗ ОШИБКА"
        print(f"{name}: {status}")
    
    print(f"\nИтого: {passed}/{total} проверок пройдено")
    
    if passed == total:
        print("\n🎉 Все компоненты работают корректно!")
        print("Приложение готово к запуску: python main.py")
    else:
        print(f"\n⚠️  Обнаружены проблемы в {total - passed} компонентах")
        print("Рекомендуется устранить ошибки перед запуском")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nПроверка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nКритическая ошибка: {e}")
        sys.exit(1)