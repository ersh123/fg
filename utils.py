# -*- coding: utf-8 -*-
"""
utils.py - Вспомогательные функции для LogoMaster Pro

Содержит утилиты для:
- Работы с файлами и директориями
- Валидации данных
- Форматирования
- Резервного копирования
- Обработки ошибок
"""

import os
import shutil
import zipfile
import json
import hashlib
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import logging

from config import get_config, is_supported_format, logger

def ensure_directory(directory_path: str) -> bool:
    """
    Убеждается, что директория существует, создает если нет
    
    Args:
        directory_path: Путь к директории
        
    Returns:
        True если директория существует или была создана
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Ошибка создания директории {directory_path}: {e}")
        return False

def get_file_size_mb(file_path: str) -> float:
    """
    Возвращает размер файла в мегабайтах
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        Размер файла в МБ
    """
    try:
        if os.path.exists(file_path):
            return os.path.getsize(file_path) / (1024 * 1024)
        return 0.0
    except Exception as e:
        logger.error(f"Ошибка получения размера файла {file_path}: {e}")
        return 0.0

def format_file_size(size_bytes: int) -> str:
    """
    Форматирует размер файла в читаемый вид
    
    Args:
        size_bytes: Размер в байтах
        
    Returns:
        Отформатированная строка размера
    """
    if size_bytes == 0:
        return "0 Б"
    
    size_names = ["Б", "КБ", "МБ", "ГБ", "ТБ"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def validate_image_file(file_path: str) -> Tuple[bool, str]:
    """
    Валидирует файл изображения
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        Кортеж (валиден, сообщение об ошибке)
    """
    try:
        # Проверяем существование файла
        if not os.path.exists(file_path):
            return False, "Файл не найден"
        
        # Проверяем формат
        if not is_supported_format(file_path, 'input'):
            return False, "Неподдерживаемый формат файла"
        
        # Проверяем размер файла
        max_size_mb = get_config('image')['max_file_size_mb']
        file_size_mb = get_file_size_mb(file_path)
        
        if file_size_mb > max_size_mb:
            return False, f"Файл слишком большой ({file_size_mb:.1f} МБ > {max_size_mb} МБ)"
        
        # Проверяем, что файл можно открыть как изображение
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                # Проверяем размеры
                max_dimensions = get_config('image')['max_image_size']
                if img.size[0] > max_dimensions[0] or img.size[1] > max_dimensions[1]:
                    return False, f"Изображение слишком большое ({img.size[0]}x{img.size[1]} > {max_dimensions[0]}x{max_dimensions[1]})"
                
        except Exception as e:
            return False, f"Не удается открыть как изображение: {e}"
        
        return True, "OK"
        
    except Exception as e:
        return False, f"Ошибка валидации: {e}"

def get_unique_filename(directory: str, base_name: str, extension: str) -> str:
    """
    Генерирует уникальное имя файла в директории
    
    Args:
        directory: Директория
        base_name: Базовое имя файла
        extension: Расширение файла (с точкой)
        
    Returns:
        Уникальное имя файла
    """
    counter = 1
    original_name = f"{base_name}{extension}"
    file_path = os.path.join(directory, original_name)
    
    while os.path.exists(file_path):
        new_name = f"{base_name}_{counter}{extension}"
        file_path = os.path.join(directory, new_name)
        counter += 1
    
    return os.path.basename(file_path)

def create_backup(file_path: str, backup_dir: str = None) -> Optional[str]:
    """
    Создает резервную копию файла
    
    Args:
        file_path: Путь к файлу для резервирования
        backup_dir: Директория для резервных копий (опционально)
        
    Returns:
        Путь к резервной копии или None при ошибке
    """
    try:
        if not os.path.exists(file_path):
            return None
        
        if backup_dir is None:
            backup_dir = get_config('paths')['backup_dir']
        
        ensure_directory(backup_dir)
        
        # Генерируем имя резервной копии с временной меткой
        file_name = Path(file_path).name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{timestamp}_{file_name}"
        backup_path = os.path.join(backup_dir, backup_name)
        
        # Копируем файл
        shutil.copy2(file_path, backup_path)
        
        logger.info(f"Создана резервная копия: {file_path} -> {backup_path}")
        return backup_path
        
    except Exception as e:
        logger.error(f"Ошибка создания резервной копии {file_path}: {e}")
        return None

def cleanup_old_backups(backup_dir: str, max_age_days: int = 30, max_count: int = 100):
    """
    Очищает старые резервные копии
    
    Args:
        backup_dir: Директория с резервными копиями
        max_age_days: Максимальный возраст файлов в днях
        max_count: Максимальное количество файлов
    """
    try:
        if not os.path.exists(backup_dir):
            return
        
        backup_path = Path(backup_dir)
        backup_files = list(backup_path.glob('*'))
        
        # Сортируем по времени модификации (новые первыми)
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        current_time = datetime.now().timestamp()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        deleted_count = 0
        
        for i, backup_file in enumerate(backup_files):
            should_delete = False
            
            # Удаляем если файл слишком старый
            file_age = current_time - backup_file.stat().st_mtime
            if file_age > max_age_seconds:
                should_delete = True
            
            # Удаляем если превышено максимальное количество
            if i >= max_count:
                should_delete = True
            
            if should_delete:
                try:
                    backup_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Ошибка удаления резервной копии {backup_file}: {e}")
        
        if deleted_count > 0:
            logger.info(f"Удалено {deleted_count} старых резервных копий")
            
    except Exception as e:
        logger.error(f"Ошибка очистки резервных копий: {e}")

def create_zip_archive(files: List[str], archive_path: str, 
                      progress_callback=None) -> bool:
    """
    Создает ZIP архив из списка файлов
    
    Args:
        files: Список путей к файлам
        archive_path: Путь к создаваемому архиву
        progress_callback: Функция обратного вызова для прогресса
        
    Returns:
        True если архив создан успешно
    """
    try:
        # Создаем директорию для архива если не существует
        ensure_directory(os.path.dirname(archive_path))
        
        total_files = len(files)
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, file_path in enumerate(files):
                if os.path.exists(file_path):
                    # Используем только имя файла в архиве
                    arcname = os.path.basename(file_path)
                    zipf.write(file_path, arcname)
                    
                    if progress_callback:
                        progress_callback(i + 1, total_files, f"Добавление {arcname}")
        
        logger.info(f"Создан архив: {archive_path} ({total_files} файлов)")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка создания архива {archive_path}: {e}")
        return False

def extract_zip_archive(archive_path: str, extract_to: str, 
                       progress_callback=None) -> List[str]:
    """
    Извлекает файлы из ZIP архива
    
    Args:
        archive_path: Путь к архиву
        extract_to: Директория для извлечения
        progress_callback: Функция обратного вызова для прогресса
        
    Returns:
        Список путей к извлеченным файлам
    """
    extracted_files = []
    
    try:
        ensure_directory(extract_to)
        
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            file_list = zipf.namelist()
            total_files = len(file_list)
            
            for i, file_name in enumerate(file_list):
                if not file_name.endswith('/'):
                    # Извлекаем файл
                    extracted_path = zipf.extract(file_name, extract_to)
                    extracted_files.append(extracted_path)
                    
                    if progress_callback:
                        progress_callback(i + 1, total_files, f"Извлечение {file_name}")
        
        logger.info(f"Извлечено {len(extracted_files)} файлов из {archive_path}")
        return extracted_files
        
    except Exception as e:
        logger.error(f"Ошибка извлечения архива {archive_path}: {e}")
        return extracted_files

def calculate_file_hash(file_path: str, algorithm: str = 'md5') -> Optional[str]:
    """
    Вычисляет хеш файла
    
    Args:
        file_path: Путь к файлу
        algorithm: Алгоритм хеширования ('md5', 'sha1', 'sha256')
        
    Returns:
        Хеш файла в виде строки или None при ошибке
    """
    try:
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
        
    except Exception as e:
        logger.error(f"Ошибка вычисления хеша {file_path}: {e}")
        return None

def find_duplicate_files(directory: str) -> Dict[str, List[str]]:
    """
    Находит дублирующиеся файлы в директории
    
    Args:
        directory: Директория для поиска
        
    Returns:
        Словарь {хеш: [список_файлов]}
    """
    file_hashes = {}
    duplicates = {}
    
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Вычисляем хеш файла
                file_hash = calculate_file_hash(file_path)
                if file_hash:
                    if file_hash in file_hashes:
                        # Найден дубликат
                        if file_hash not in duplicates:
                            duplicates[file_hash] = [file_hashes[file_hash]]
                        duplicates[file_hash].append(file_path)
                    else:
                        file_hashes[file_hash] = file_path
        
        logger.info(f"Найдено {len(duplicates)} групп дублирующихся файлов")
        return duplicates
        
    except Exception as e:
        logger.error(f"Ошибка поиска дубликатов в {directory}: {e}")
        return {}

def save_json(data: Any, file_path: str, indent: int = 2) -> bool:
    """
    Сохраняет данные в JSON файл
    
    Args:
        data: Данные для сохранения
        file_path: Путь к файлу
        indent: Отступ для форматирования
        
    Returns:
        True если сохранение успешно
    """
    try:
        ensure_directory(os.path.dirname(file_path))
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка сохранения JSON {file_path}: {e}")
        return False

def load_json(file_path: str, default=None) -> Any:
    """
    Загружает данные из JSON файла
    
    Args:
        file_path: Путь к файлу
        default: Значение по умолчанию при ошибке
        
    Returns:
        Загруженные данные или значение по умолчанию
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default
        
    except Exception as e:
        logger.error(f"Ошибка загрузки JSON {file_path}: {e}")
        return default

def get_temp_directory() -> str:
    """
    Возвращает путь к временной директории приложения
    
    Returns:
        Путь к временной директории
    """
    temp_dir = get_config('paths')['temp_dir']
    ensure_directory(temp_dir)
    return str(temp_dir)

def cleanup_temp_directory():
    """
    Очищает временную директорию приложения
    """
    try:
        temp_dir = get_temp_directory()
        
        for item in Path(temp_dir).iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        
        logger.info("Временная директория очищена")
        
    except Exception as e:
        logger.error(f"Ошибка очистки временной директории: {e}")

def format_duration(seconds: float) -> str:
    """
    Форматирует продолжительность в читаемый вид
    
    Args:
        seconds: Продолжительность в секундах
        
    Returns:
        Отформатированная строка времени
    """
    if seconds < 60:
        return f"{seconds:.1f} сек"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} мин"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} ч"

def safe_filename(filename: str) -> str:
    """
    Создает безопасное имя файла, удаляя недопустимые символы
    
    Args:
        filename: Исходное имя файла
        
    Returns:
        Безопасное имя файла
    """
    # Символы, недопустимые в именах файлов Windows
    invalid_chars = '<>:"/\\|?*'
    
    safe_name = filename
    for char in invalid_chars:
        safe_name = safe_name.replace(char, '_')
    
    # Удаляем точки в конце и пробелы
    safe_name = safe_name.rstrip('. ')
    
    # Ограничиваем длину
    if len(safe_name) > 200:
        name, ext = os.path.splitext(safe_name)
        safe_name = name[:200-len(ext)] + ext
    
    return safe_name or 'unnamed'

def get_available_space(directory: str) -> int:
    """
    Возвращает доступное место на диске в байтах
    
    Args:
        directory: Путь к директории
        
    Returns:
        Доступное место в байтах
    """
    try:
        if os.name == 'nt':  # Windows
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(directory),
                ctypes.pointer(free_bytes),
                None,
                None
            )
            return free_bytes.value
        else:  # Unix-like
            statvfs = os.statvfs(directory)
            return statvfs.f_frsize * statvfs.f_bavail
    except Exception as e:
        logger.error(f"Ошибка получения свободного места: {e}")
        return 0

def check_disk_space(directory: str, required_mb: float) -> bool:
    """
    Проверяет, достаточно ли места на диске
    
    Args:
        directory: Директория для проверки
        required_mb: Требуемое место в МБ
        
    Returns:
        True если места достаточно
    """
    try:
        available_bytes = get_available_space(directory)
        available_mb = available_bytes / (1024 * 1024)
        
        return available_mb >= required_mb
        
    except Exception as e:
        logger.error(f"Ошибка проверки места на диске: {e}")
        return False

def copy_with_progress(src: str, dst: str, progress_callback=None) -> bool:
    """
    Копирует файл с отображением прогресса
    
    Args:
        src: Исходный файл
        dst: Файл назначения
        progress_callback: Функция обратного вызова для прогресса
        
    Returns:
        True если копирование успешно
    """
    try:
        file_size = os.path.getsize(src)
        copied = 0
        
        with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
            while True:
                chunk = fsrc.read(64 * 1024)  # 64KB chunks
                if not chunk:
                    break
                
                fdst.write(chunk)
                copied += len(chunk)
                
                if progress_callback:
                    progress = (copied / file_size) * 100 if file_size > 0 else 100
                    progress_callback(progress, f"Копирование {os.path.basename(src)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка копирования {src} -> {dst}: {e}")
        return False

class PerformanceTimer:
    """
    Контекстный менеджер для измерения времени выполнения
    """
    
    def __init__(self, operation_name: str = "Operation"):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        logger.debug(f"Начало операции: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        if exc_type is None:
            logger.info(f"Операция '{self.operation_name}' завершена за {format_duration(duration)}")
        else:
            logger.error(f"Операция '{self.operation_name}' завершилась с ошибкой за {format_duration(duration)}")
    
    def get_duration(self) -> float:
        """
        Возвращает продолжительность операции в секундах
        """
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

if __name__ == '__main__':
    # Тестирование утилит
    print("Тестирование утилит LogoMaster Pro")
    
    # Тест форматирования размера файла
    print(f"Размер 1024 байт: {format_file_size(1024)}")
    print(f"Размер 1048576 байт: {format_file_size(1048576)}")
    print(f"Размер 1073741824 байт: {format_file_size(1073741824)}")
    
    # Тест форматирования времени
    print(f"30 секунд: {format_duration(30)}")
    print(f"90 секунд: {format_duration(90)}")
    print(f"3700 секунд: {format_duration(3700)}")
    
    # Тест безопасного имени файла
    unsafe_name = 'test<file>name:with|invalid*chars?.jpg'
    safe_name = safe_filename(unsafe_name)
    print(f"Небезопасное имя: {unsafe_name}")
    print(f"Безопасное имя: {safe_name}")
    
    # Тест таймера производительности
    with PerformanceTimer("Тестовая операция") as timer:
        import time
        time.sleep(0.1)
    
    print(f"Продолжительность операции: {timer.get_duration():.3f} сек")
    
    print("Тестирование завершено")