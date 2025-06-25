# -*- coding: utf-8 -*-
"""
config.py - Конфигурация приложения LogoMaster Pro

Содержит все настройки приложения, включая UI параметры,
пути к файлам, настройки обработки изображений и другие конфигурации.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Tuple

# =============================================================================
# ОСНОВНЫЕ НАСТРОЙКИ ПРИЛОЖЕНИЯ
# =============================================================================

APP_CONFIG = {
    'title': 'LogoMaster Pro',
    'version': '2.0.0',
    'author': 'LogoMaster Team',
    'description': 'Профессиональное приложение для нанесения логотипов на изображения',
    'window_size': (1200, 800),
    'min_window_size': (800, 600),
    'icon_path': None,  # Путь к иконке приложения
}

# =============================================================================
# НАСТРОЙКИ UI И ДИЗАЙНА
# =============================================================================

# Цветовая схема
COLORS = {
    'primary': '#2E3440',      # Темно-серый (основной)
    'primary_dark': '#242933', # Темнее основного
    'primary_darker': '#1a1f26', # Еще темнее основного
    'secondary': '#3B4252',    # Серый (вторичный)
    'secondary_dark': '#2f3541', # Темнее вторичного
    'secondary_darker': '#252a35', # Еще темнее вторичного
    'accent': '#5E81AC',       # Синий (акцент)
    'success': '#A3BE8C',      # Зеленый (успех)
    'warning': '#EBCB8B',      # Желтый (предупреждение)
    'error': '#BF616A',        # Красный (ошибка)
    'danger': '#BF616A',       # Красный (опасность)
    'background': '#ECEFF4',   # Светло-серый (фон)
    'surface': '#FFFFFF',      # Белый (поверхность)
    'white': '#FFFFFF',        # Белый цвет
    'text': '#2E3440',         # Основной текст
    'text_primary': '#2E3440', # Темный текст
    'text_secondary': '#4C566A', # Серый текст
    'border': '#D8DEE9',       # Граница
    'hover': '#E5E9F0',        # Наведение
}

# Шрифты
FONTS = {
    'default': ('Segoe UI', 9),
    'heading': ('Segoe UI', 12, 'bold'),
    'button': ('Segoe UI', 9),
    'status': ('Segoe UI', 8),
    'monospace': ('Consolas', 9),
}

# Размеры и отступы
SIZES = {
    'padding': 10,
    'margin': 5,
    'button_height': 32,
    'button_width': 120,
    'toolbar_height': 40,
    'status_height': 25,
    'sidebar_width': 300,
    'preview_size': (400, 300),
}

# =============================================================================
# НАСТРОЙКИ ОБРАБОТКИ ИЗОБРАЖЕНИЙ
# =============================================================================

IMAGE_CONFIG = {
    # Поддерживаемые форматы
    'supported_formats': {
        'input': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'],
        'output': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff'],
        'logo': ['.png', '.jpg', '.jpeg', '.bmp', '.tiff'],
    },
    
    # Ограничения размеров
    'max_image_size': (8192, 8192),  # Максимальный размер изображения
    'max_file_size_mb': 50,          # Максимальный размер файла в МБ
    'preview_size': (800, 600),      # Размер превью
    'thumbnail_size': (150, 150),    # Размер миниатюр
    
    # Настройки качества
    'jpeg_quality': 95,              # Качество JPEG (1-100)
    'png_compression': 6,            # Сжатие PNG (0-9)
    
    # Настройки логотипа по умолчанию
    'default_logo_size': 0.1,        # 10% от размера изображения
    'default_opacity': 0.8,          # 80% непрозрачности
    'default_position': 'bottom_right',
    'logo_margin': 20,               # Отступ от краев в пикселях
}

# Позиции для размещения логотипа
LOGO_POSITIONS = {
    'top_left': (0, 0),
    'top_center': (0.5, 0),
    'top_right': (1, 0),
    'center_left': (0, 0.5),
    'center': (0.5, 0.5),
    'center_right': (1, 0.5),
    'bottom_left': (0, 1),
    'bottom_center': (0.5, 1),
    'bottom_right': (1, 1),
}

# Названия позиций на русском
POSITION_NAMES = {
    'top_left': 'Верх слева',
    'top_center': 'Верх по центру',
    'top_right': 'Верх справа',
    'center_left': 'Центр слева',
    'center': 'По центру',
    'center_right': 'Центр справа',
    'bottom_left': 'Низ слева',
    'bottom_center': 'Низ по центру',
    'bottom_right': 'Низ справа',
}

# =============================================================================
# НАСТРОЙКИ ФАЙЛОВОЙ СИСТЕМЫ
# =============================================================================

# Базовые пути
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / 'assets'
TEMP_DIR = BASE_DIR / 'temp'
LOGS_DIR = BASE_DIR / 'logs'
CONFIG_DIR = BASE_DIR / 'config'

# Создание необходимых директорий
for directory in [ASSETS_DIR, TEMP_DIR, LOGS_DIR, CONFIG_DIR]:
    directory.mkdir(exist_ok=True)

# Пути к файлам
FILE_PATHS = {
    'user_config': CONFIG_DIR / 'user_settings.json',
    'recent_files': CONFIG_DIR / 'recent_files.json',
    'log_file': LOGS_DIR / 'logomaster.log',
    'temp_dir': TEMP_DIR,
    'assets_dir': ASSETS_DIR,
}

# =============================================================================
# НАСТРОЙКИ ЛОГИРОВАНИЯ
# =============================================================================

LOGGING_CONFIG = {
    'level': logging.INFO,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'file_path': FILE_PATHS['log_file'],
    'max_file_size': 10 * 1024 * 1024,  # 10 МБ
    'backup_count': 5,
}

# =============================================================================
# НАСТРОЙКИ ПРОИЗВОДИТЕЛЬНОСТИ
# =============================================================================

PERFORMANCE_CONFIG = {
    'max_threads': 4,                # Максимальное количество потоков
    'chunk_size': 10,               # Размер чанка для пакетной обработки
    'memory_limit_mb': 1024,        # Лимит памяти в МБ
    'cache_size': 50,               # Размер кэша превью
    'progress_update_interval': 100, # Интервал обновления прогресса (мс)
}

# =============================================================================
# НАСТРОЙКИ СЕТИ
# =============================================================================

NETWORK_CONFIG = {
    'timeout': 30,                  # Таймаут для сетевых запросов (сек)
    'max_retries': 3,               # Максимальное количество повторов
    'user_agent': f"LogoMaster Pro {APP_CONFIG['version']}",
    'max_download_size_mb': 100,    # Максимальный размер загружаемого файла
}

# =============================================================================
# НАСТРОЙКИ ИНТЕРФЕЙСА
# =============================================================================

UI_CONFIG = {
    'auto_save_settings': True,     # Автосохранение настроек
    'show_tooltips': True,          # Показывать подсказки
    'confirm_exit': True,           # Подтверждение выхода
    'remember_window_state': True,  # Запоминать состояние окна
    'recent_files_limit': 10,       # Лимит недавних файлов
    'preview_auto_update': True,    # Автообновление превью
    'show_grid': False,             # Показывать сетку в превью
    'zoom_step': 0.1,               # Шаг зума (10%)
    'min_zoom': 0.1,                # Минимальный зум (10%)
    'max_zoom': 5.0,                # Максимальный зум (500%)
}

# =============================================================================
# ГОРЯЧИЕ КЛАВИШИ
# =============================================================================

HOTKEYS = {
    'open_images': '<Control-o>',
    'open_logo': '<Control-l>',
    'save_current': '<Control-s>',
    'save_all': '<Control-Shift-s>',
    'apply_logo': '<Control-Return>',
    'apply_all': '<Control-Shift-Return>',
    'next_image': '<Right>',
    'prev_image': '<Left>',
    'zoom_in': '<Control-plus>',
    'zoom_out': '<Control-minus>',
    'zoom_fit': '<Control-0>',
    'toggle_preview': '<F5>',
    'show_about': '<F1>',
    'exit': '<Control-q>',
}

# =============================================================================
# СООБЩЕНИЯ И ТЕКСТЫ
# =============================================================================

MESSAGES = {
    'app_title': APP_CONFIG['title'],
    'loading': 'Загрузка...',
    'processing': 'Обработка...',
    'saving': 'Сохранение...',
    'done': 'Готово',
    'error': 'Ошибка',
    'warning': 'Предупреждение',
    'info': 'Информация',
    
    # Сообщения об ошибках
    'error_load_image': 'Не удалось загрузить изображение',
    'error_load_logo': 'Не удалось загрузить логотип',
    'error_save_image': 'Не удалось сохранить изображение',
    'error_process_image': 'Ошибка обработки изображения',
    'error_invalid_format': 'Неподдерживаемый формат файла',
    'error_file_too_large': 'Файл слишком большой',
    'error_no_images': 'Изображения не загружены',
    'error_no_logo': 'Логотип не загружен',
    
    # Информационные сообщения
    'images_loaded': 'Изображения загружены',
    'logo_loaded': 'Логотип загружен',
    'logo_applied': 'Логотип применен',
    'images_saved': 'Изображения сохранены',
    'processing_complete': 'Обработка завершена',
}

# =============================================================================
# ФУНКЦИИ КОНФИГУРАЦИИ
# =============================================================================

def get_config(section: str = None) -> Dict[str, Any]:
    """
    Получает конфигурацию приложения
    
    Args:
        section: Название секции конфигурации
        
    Returns:
        Словарь с настройками
    """
    configs = {
        'app': APP_CONFIG,
        'colors': COLORS,
        'fonts': FONTS,
        'sizes': SIZES,
        'image': IMAGE_CONFIG,
        'performance': PERFORMANCE_CONFIG,
        'network': NETWORK_CONFIG,
        'ui': UI_CONFIG,
        'hotkeys': HOTKEYS,
        'messages': MESSAGES,
        'paths': FILE_PATHS,
        'logging': LOGGING_CONFIG,
    }
    
    if section:
        return configs.get(section, {})
    return configs

def get_color(color_name: str) -> str:
    """
    Получает цвет по названию
    
    Args:
        color_name: Название цвета
        
    Returns:
        Hex код цвета
    """
    return COLORS.get(color_name, '#000000')

def get_font(font_name: str) -> Tuple[str, int, str]:
    """
    Получает шрифт по названию
    
    Args:
        font_name: Название шрифта
        
    Returns:
        Кортеж (семейство, размер, стиль)
    """
    return FONTS.get(font_name, FONTS['default'])

def get_size(size_name: str) -> int:
    """
    Получает размер по названию
    
    Args:
        size_name: Название размера
        
    Returns:
        Размер в пикселях
    """
    return SIZES.get(size_name, 0)

def is_supported_format(file_path: str, format_type: str = 'input') -> bool:
    """
    Проверяет, поддерживается ли формат файла
    
    Args:
        file_path: Путь к файлу
        format_type: Тип формата ('input', 'output', 'logo')
        
    Returns:
        True если формат поддерживается
    """
    extension = Path(file_path).suffix.lower()
    supported = IMAGE_CONFIG['supported_formats'].get(format_type, [])
    return extension in supported

def setup_logging() -> logging.Logger:
    """
    Настраивает систему логирования
    
    Returns:
        Настроенный логгер
    """
    # Создаем логгер
    logger = logging.getLogger('logomaster')
    logger.setLevel(LOGGING_CONFIG['level'])
    
    # Очищаем существующие обработчики
    logger.handlers.clear()
    
    # Создаем форматтер
    formatter = logging.Formatter(
        LOGGING_CONFIG['format'],
        LOGGING_CONFIG['date_format']
    )
    
    # Обработчик для файла
    try:
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            LOGGING_CONFIG['file_path'],
            maxBytes=LOGGING_CONFIG['max_file_size'],
            backupCount=LOGGING_CONFIG['backup_count'],
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Ошибка настройки файлового логирования: {e}")
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# Инициализация логгера
logger = setup_logging()

if __name__ == '__main__':
    # Тестирование конфигурации
    print(f"Приложение: {APP_CONFIG['title']} v{APP_CONFIG['version']}")
    print(f"Поддерживаемые форматы: {IMAGE_CONFIG['supported_formats']['input']}")
    print(f"Цвета: {list(COLORS.keys())}")
    print(f"Шрифты: {list(FONTS.keys())}")
    print(f"Пути: {list(FILE_PATHS.keys())}")
    
    logger.info("Конфигурация загружена успешно")