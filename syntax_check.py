#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка синтаксиса и импортов
"""

import ast
import sys
import os

def check_syntax(filename):
    """Проверка синтаксиса файла"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"Синтаксическая ошибка в {filename}: {e}"
    except Exception as e:
        return False, f"Ошибка чтения {filename}: {e}"

def main():
    files_to_check = [
        'config.py',
        'main.py', 
        'ui_components.py',
        'image_processor.py',
        'utils.py'
    ]
    
    print("Проверка синтаксиса файлов:")
    
    for filename in files_to_check:
        if os.path.exists(filename):
            is_valid, error = check_syntax(filename)
            if is_valid:
                print(f"✓ {filename}: OK")
            else:
                print(f"✗ {filename}: {error}")
        else:
            print(f"✗ {filename}: файл не найден")
    
    # Проверка config.py на наличие необходимых переменных
    try:
        with open('config.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        required_vars = ['COLORS', 'APP_CONFIG', 'FONTS', 'SIZES']
        for var in required_vars:
            if var in content:
                print(f"✓ {var}: найден в config.py")
            else:
                print(f"✗ {var}: НЕ найден в config.py")
                
        # Проверка наличия цвета 'text'
        if "'text':" in content:
            print("✓ Цвет 'text': найден в COLORS")
        else:
            print("✗ Цвет 'text': НЕ найден в COLORS")
            
    except Exception as e:
        print(f"Ошибка проверки config.py: {e}")

if __name__ == '__main__':
    main()