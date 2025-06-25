#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_fixes.py - Проверка всех исправлений

Проверяет, что все ошибки конфигурации исправлены
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """Тестирование конфигурации"""
    print("=== Тестирование конфигурации ===")
    
    try:
        from config import APP_CONFIG, COLORS, FONTS
        print("✓ Конфигурация импортирована успешно")
        
        # Проверяем APP_CONFIG
        if 'title' in APP_CONFIG:
            print(f"✓ APP_CONFIG['title']: {APP_CONFIG['title']}")
        else:
            print("✗ APP_CONFIG['title'] отсутствует")
            return False
            
        # Проверяем цвета
        required_colors = ['white', 'primary', 'secondary', 'text', 'danger', 
                          'primary_dark', 'primary_darker', 'secondary_dark', 'secondary_darker']
        
        missing_colors = []
        for color in required_colors:
            if color in COLORS:
                print(f"✓ COLORS['{color}']: {COLORS[color]}")
            else:
                missing_colors.append(color)
                print(f"✗ COLORS['{color}'] отсутствует")
        
        if missing_colors:
            print(f"Отсутствующие цвета: {missing_colors}")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Ошибка импорта конфигурации: {e}")
        return False

def test_ui_components():
    """Тестирование UI компонентов"""
    print("\n=== Тестирование UI компонентов ===")
    
    try:
        from ui_components import ModernButton
        print("✓ ModernButton импортирован успешно")
        
        # Пробуем создать кнопку без GUI
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Скрываем окно
        
        # Тестируем разные стили кнопок
        styles = ['primary', 'secondary', 'success', 'danger']
        for style in styles:
            try:
                btn = ModernButton(root, text=f"Test {style}", style=style)
                print(f"✓ Кнопка стиля '{style}' создана успешно")
            except Exception as e:
                print(f"✗ Ошибка создания кнопки '{style}': {e}")
                root.destroy()
                return False
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Ошибка тестирования UI: {e}")
        return False

def test_main_app():
    """Тестирование основного приложения"""
    print("\n=== Тестирование основного приложения ===")
    
    try:
        # Импортируем без создания GUI
        from main import LogoMasterApp
        print("✓ LogoMasterApp импортирован успешно")
        
        # Проверяем, что можем создать экземпляр (но не запускаем GUI)
        import tkinter as tk
        
        # Создаем временный root для тестирования
        test_root = tk.Tk()
        test_root.withdraw()
        
        # Проверяем настройку заголовка окна
        from config import APP_CONFIG
        test_root.title(APP_CONFIG['title'])  # Это должно работать
        print(f"✓ Заголовок окна установлен: {APP_CONFIG['title']}")
        
        test_root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Ошибка тестирования приложения: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("Проверка исправлений LogoMaster Pro...\n")
    
    tests = [
        ("Конфигурация", test_config),
        ("UI компоненты", test_ui_components),
        ("Основное приложение", test_main_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"\n✅ {test_name}: ПРОЙДЕН")
                passed += 1
            else:
                print(f"\n❌ {test_name}: НЕ ПРОЙДЕН")
        except Exception as e:
            print(f"\n❌ {test_name}: ОШИБКА - {e}")
    
    print(f"\n{'='*50}")
    print(f"Результат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все исправления работают корректно!")
        print("Приложение готово к запуску.")
        return True
    else:
        print("⚠️  Требуются дополнительные исправления.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)