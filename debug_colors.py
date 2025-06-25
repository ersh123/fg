#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отладочный скрипт для проверки цветов
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import COLORS, logger
    print("✓ Успешный импорт config")
    
    # Проверяем все цвета, используемые в приложении
    required_colors = [
        'primary', 'primary_dark', 'primary_darker',
        'secondary', 'secondary_dark', 'secondary_darker',
        'accent', 'success', 'warning', 'error', 'danger',
        'background', 'surface', 'white', 'text',
        'text_primary', 'text_secondary', 'border', 'hover'
    ]
    
    print("\nПроверка цветов:")
    missing_colors = []
    
    for color in required_colors:
        if color in COLORS:
            print(f"✓ {color}: {COLORS[color]}")
        else:
            print(f"✗ {color}: ОТСУТСТВУЕТ")
            missing_colors.append(color)
    
    if missing_colors:
        print(f"\n❌ Отсутствующие цвета: {missing_colors}")
        sys.exit(1)
    else:
        print("\n✅ Все цвета присутствуют")
        
    # Проверяем импорт ui_components
    try:
        from ui_components import ModernButton
        print("✓ Успешный импорт ui_components")
    except Exception as e:
        print(f"✗ Ошибка импорта ui_components: {e}")
        sys.exit(1)
        
    print("\n🎉 Все проверки пройдены успешно!")
    
except Exception as e:
    print(f"❌ Критическая ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)