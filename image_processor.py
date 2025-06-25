# -*- coding: utf-8 -*-
"""
image_processor.py - Модуль обработки изображений для LogoMaster Pro

Содержит класс ImageProcessor для загрузки, обработки и сохранения изображений,
а также применения логотипов с различными настройками позиционирования и стилизации.
"""

import os
import io
import zipfile
import requests
from pathlib import Path
from typing import List, Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import numpy as np
import logging

from config import (
    IMAGE_CONFIG, LOGO_POSITIONS, NETWORK_CONFIG, 
    get_config, is_supported_format, logger
)

class ImageProcessor:
    """
    Класс для обработки изображений и применения логотипов
    
    Основные возможности:
    - Загрузка изображений из файлов, архивов и URL
    - Применение логотипов с настройкой позиции, размера и прозрачности
    - Пакетная обработка изображений
    - Сохранение результатов в различных форматах
    """
    
    def __init__(self):
        """
        Инициализация процессора изображений
        """
        self.logger = logger
        self.current_logo = None
        self.logo_cache = {}
        
        # Настройки по умолчанию
        self.default_settings = {
            'position': IMAGE_CONFIG['default_position'],
            'size': IMAGE_CONFIG['default_logo_size'],
            'opacity': IMAGE_CONFIG['default_opacity'],
            'margin': IMAGE_CONFIG['logo_margin'],
        }
        
        self.logger.info("ImageProcessor инициализирован")
    
    def load_image(self, file_path: str) -> Optional[Image.Image]:
        """
        Загружает изображение из файла
        
        Args:
            file_path: Путь к файлу изображения
            
        Returns:
            PIL Image объект или None при ошибке
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"Файл не найден: {file_path}")
                return None
            
            if not is_supported_format(file_path, 'input'):
                self.logger.error(f"Неподдерживаемый формат: {file_path}")
                return None
            
            # Проверка размера файла
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > IMAGE_CONFIG['max_file_size_mb']:
                self.logger.error(f"Файл слишком большой: {file_size_mb:.1f} МБ")
                return None
            
            # Загрузка изображения
            with Image.open(file_path) as img:
                # Конвертируем в RGB если необходимо
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Создаем белый фон для прозрачных изображений
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Проверка размеров
                max_size = IMAGE_CONFIG['max_image_size']
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    self.logger.warning(f"Изображение слишком большое, изменяем размер: {img.size}")
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Создаем копию для возврата
                result = img.copy()
                
            self.logger.info(f"Изображение загружено: {file_path} ({result.size})")
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки изображения {file_path}: {e}")
            return None
    
    def load_images_from_directory(self, directory_path: str) -> List[str]:
        """
        Загружает пути ко всем изображениям из директории
        
        Args:
            directory_path: Путь к директории
            
        Returns:
            Список путей к изображениям
        """
        image_paths = []
        
        try:
            directory = Path(directory_path)
            if not directory.exists() or not directory.is_dir():
                self.logger.error(f"Директория не найдена: {directory_path}")
                return image_paths
            
            supported_extensions = IMAGE_CONFIG['supported_formats']['input']
            
            for file_path in directory.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                    image_paths.append(str(file_path))
            
            image_paths.sort()  # Сортируем по алфавиту
            self.logger.info(f"Найдено {len(image_paths)} изображений в {directory_path}")
            
        except Exception as e:
            self.logger.error(f"Ошибка сканирования директории {directory_path}: {e}")
        
        return image_paths
    
    def load_images_from_archive(self, archive_path: str, extract_to: str = None) -> List[str]:
        """
        Извлекает изображения из архива
        
        Args:
            archive_path: Путь к архиву
            extract_to: Путь для извлечения (по умолчанию temp)
            
        Returns:
            Список путей к извлеченным изображениям
        """
        image_paths = []
        
        try:
            if extract_to is None:
                extract_to = get_config('paths')['temp_dir'] / 'extracted'
            
            extract_path = Path(extract_to)
            extract_path.mkdir(parents=True, exist_ok=True)
            
            supported_extensions = IMAGE_CONFIG['supported_formats']['input']
            
            with zipfile.ZipFile(archive_path, 'r') as zip_file:
                for file_info in zip_file.filelist:
                    if not file_info.is_dir():
                        file_extension = Path(file_info.filename).suffix.lower()
                        if file_extension in supported_extensions:
                            # Извлекаем файл
                            extracted_path = zip_file.extract(file_info, extract_path)
                            image_paths.append(extracted_path)
            
            self.logger.info(f"Извлечено {len(image_paths)} изображений из {archive_path}")
            
        except Exception as e:
            self.logger.error(f"Ошибка извлечения архива {archive_path}: {e}")
        
        return image_paths
    
    def download_image(self, url: str, save_path: str = None) -> Optional[str]:
        """
        Загружает изображение по URL
        
        Args:
            url: URL изображения
            save_path: Путь для сохранения (опционально)
            
        Returns:
            Путь к сохраненному файлу или None при ошибке
        """
        try:
            headers = {'User-Agent': NETWORK_CONFIG['user_agent']}
            
            response = requests.get(
                url, 
                headers=headers, 
                timeout=NETWORK_CONFIG['timeout'],
                stream=True
            )
            response.raise_for_status()
            
            # Проверяем размер файла
            content_length = response.headers.get('content-length')
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                if size_mb > NETWORK_CONFIG['max_download_size_mb']:
                    self.logger.error(f"Файл слишком большой для загрузки: {size_mb:.1f} МБ")
                    return None
            
            # Определяем путь сохранения
            if save_path is None:
                temp_dir = get_config('paths')['temp_dir']
                filename = Path(url).name or 'downloaded_image.jpg'
                save_path = temp_dir / filename
            
            # Сохраняем файл
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.logger.info(f"Изображение загружено: {url} -> {save_path}")
            return str(save_path)
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки изображения {url}: {e}")
            return None
    
    def load_logo(self, logo_path: str) -> bool:
        """
        Загружает логотип
        
        Args:
            logo_path: Путь к файлу логотипа
            
        Returns:
            True если логотип загружен успешно
        """
        try:
            if not os.path.exists(logo_path):
                self.logger.error(f"Файл логотипа не найден: {logo_path}")
                return False
            
            if not is_supported_format(logo_path, 'logo'):
                self.logger.error(f"Неподдерживаемый формат логотипа: {logo_path}")
                return False
            
            # Загружаем логотип
            with Image.open(logo_path) as logo:
                # Сохраняем прозрачность для PNG
                if logo.mode in ('RGBA', 'LA'):
                    self.current_logo = logo.convert('RGBA')
                else:
                    self.current_logo = logo.convert('RGB')
                
                # Создаем копию
                self.current_logo = self.current_logo.copy()
            
            self.logger.info(f"Логотип загружен: {logo_path} ({self.current_logo.size})")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки логотипа {logo_path}: {e}")
            return False
    
    def apply_logo(self, image: Image.Image, **kwargs) -> Optional[Image.Image]:
        """
        Применяет логотип к изображению
        
        Args:
            image: Исходное изображение
            **kwargs: Параметры применения логотипа
                - position: позиция ('top_left', 'center', etc.)
                - size: размер логотипа (0.0-1.0)
                - opacity: прозрачность (0.0-1.0)
                - margin: отступ от краев (пиксели)
                - custom_position: кастомная позиция (x, y)
                
        Returns:
            Изображение с логотипом или None при ошибке
        """
        if self.current_logo is None:
            self.logger.error("Логотип не загружен")
            return None
        
        try:
            # Получаем параметры
            settings = self.default_settings.copy()
            settings.update(kwargs)
            
            position = settings['position']
            logo_size = settings['size']
            opacity = settings['opacity']
            margin = settings['margin']
            custom_position = settings.get('custom_position')
            
            # Создаем копию изображения
            result = image.copy()
            
            # Вычисляем размер логотипа
            img_width, img_height = result.size
            logo_width = int(img_width * logo_size)
            logo_height = int(self.current_logo.size[1] * (logo_width / self.current_logo.size[0]))
            
            # Изменяем размер логотипа
            resized_logo = self.current_logo.resize(
                (logo_width, logo_height), 
                Image.Resampling.LANCZOS
            )
            
            # Применяем прозрачность
            if opacity < 1.0:
                if resized_logo.mode != 'RGBA':
                    resized_logo = resized_logo.convert('RGBA')
                
                # Создаем маску прозрачности
                alpha = resized_logo.split()[-1]
                alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
                resized_logo.putalpha(alpha)
            
            # Вычисляем позицию
            if custom_position:
                x, y = custom_position
            else:
                if position in LOGO_POSITIONS:
                    rel_x, rel_y = LOGO_POSITIONS[position]
                else:
                    rel_x, rel_y = LOGO_POSITIONS['bottom_right']
                
                # Вычисляем абсолютные координаты
                x = int((img_width - logo_width) * rel_x)
                y = int((img_height - logo_height) * rel_y)
                
                # Применяем отступы
                if rel_x == 0:  # Левая сторона
                    x += margin
                elif rel_x == 1:  # Правая сторона
                    x -= margin
                
                if rel_y == 0:  # Верх
                    y += margin
                elif rel_y == 1:  # Низ
                    y -= margin
            
            # Убеждаемся, что логотип помещается в изображение
            x = max(0, min(x, img_width - logo_width))
            y = max(0, min(y, img_height - logo_height))
            
            # Накладываем логотип
            if resized_logo.mode == 'RGBA':
                result.paste(resized_logo, (x, y), resized_logo)
            else:
                result.paste(resized_logo, (x, y))
            
            self.logger.info(f"Логотип применен: позиция=({x}, {y}), размер={logo_width}x{logo_height}")
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка применения логотипа: {e}")
            return None
    
    def create_preview(self, image: Image.Image, max_size: Tuple[int, int] = None) -> Image.Image:
        """
        Создает превью изображения
        
        Args:
            image: Исходное изображение
            max_size: Максимальный размер превью
            
        Returns:
            Превью изображения
        """
        if max_size is None:
            max_size = IMAGE_CONFIG['preview_size']
        
        try:
            # Создаем копию
            preview = image.copy()
            
            # Изменяем размер с сохранением пропорций
            preview.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            return preview
            
        except Exception as e:
            self.logger.error(f"Ошибка создания превью: {e}")
            return image
    
    def save_image(self, image: Image.Image, file_path: str, quality: int = None) -> bool:
        """
        Сохраняет изображение в файл
        
        Args:
            image: Изображение для сохранения
            file_path: Путь для сохранения
            quality: Качество JPEG (опционально)
            
        Returns:
            True если сохранение успешно
        """
        try:
            if not is_supported_format(file_path, 'output'):
                self.logger.error(f"Неподдерживаемый формат для сохранения: {file_path}")
                return False
            
            # Создаем директорию если не существует
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Определяем параметры сохранения
            save_kwargs = {}
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension in ['.jpg', '.jpeg']:
                # Конвертируем в RGB для JPEG
                if image.mode != 'RGB':
                    if image.mode == 'RGBA':
                        # Создаем белый фон
                        background = Image.new('RGB', image.size, (255, 255, 255))
                        background.paste(image, mask=image.split()[-1])
                        image = background
                    else:
                        image = image.convert('RGB')
                
                save_kwargs['quality'] = quality or IMAGE_CONFIG['jpeg_quality']
                save_kwargs['optimize'] = True
                
            elif file_extension == '.png':
                save_kwargs['compress_level'] = IMAGE_CONFIG['png_compression']
                save_kwargs['optimize'] = True
            
            # Сохраняем изображение
            image.save(file_path, **save_kwargs)
            
            self.logger.info(f"Изображение сохранено: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения изображения {file_path}: {e}")
            return False
    
    def batch_process(self, image_paths: List[str], output_dir: str, 
                     progress_callback=None, **logo_settings) -> List[str]:
        """
        Пакетная обработка изображений
        
        Args:
            image_paths: Список путей к изображениям
            output_dir: Директория для сохранения
            progress_callback: Функция обратного вызова для прогресса
            **logo_settings: Настройки логотипа
            
        Returns:
            Список путей к обработанным изображениям
        """
        if self.current_logo is None:
            self.logger.error("Логотип не загружен для пакетной обработки")
            return []
        
        processed_paths = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        total_images = len(image_paths)
        
        for i, image_path in enumerate(image_paths):
            try:
                # Обновляем прогресс
                if progress_callback:
                    progress_callback(i, total_images, f"Обработка {Path(image_path).name}")
                
                # Загружаем изображение
                image = self.load_image(image_path)
                if image is None:
                    continue
                
                # Применяем логотип
                processed_image = self.apply_logo(image, **logo_settings)
                if processed_image is None:
                    continue
                
                # Сохраняем результат
                original_name = Path(image_path).stem
                output_file = output_path / f"{original_name}_with_logo.jpg"
                
                if self.save_image(processed_image, str(output_file)):
                    processed_paths.append(str(output_file))
                
            except Exception as e:
                self.logger.error(f"Ошибка обработки {image_path}: {e}")
                continue
        
        if progress_callback:
            progress_callback(total_images, total_images, "Обработка завершена")
        
        self.logger.info(f"Пакетная обработка завершена: {len(processed_paths)}/{total_images}")
        return processed_paths
    
    def get_image_info(self, image_path: str) -> dict:
        """
        Получает информацию об изображении
        
        Args:
            image_path: Путь к изображению
            
        Returns:
            Словарь с информацией об изображении
        """
        info = {
            'path': image_path,
            'exists': False,
            'size': None,
            'dimensions': None,
            'format': None,
            'mode': None,
            'file_size': 0,
        }
        
        try:
            if os.path.exists(image_path):
                info['exists'] = True
                info['file_size'] = os.path.getsize(image_path)
                
                with Image.open(image_path) as img:
                    info['dimensions'] = img.size
                    info['format'] = img.format
                    info['mode'] = img.mode
                    
        except Exception as e:
            self.logger.error(f"Ошибка получения информации об изображении {image_path}: {e}")
        
        return info
    
    def cleanup_temp_files(self):
        """
        Очищает временные файлы
        """
        try:
            temp_dir = get_config('paths')['temp_dir']
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)
                temp_dir.mkdir(exist_ok=True)
                self.logger.info("Временные файлы очищены")
        except Exception as e:
            self.logger.error(f"Ошибка очистки временных файлов: {e}")

if __name__ == '__main__':
    # Тестирование модуля
    processor = ImageProcessor()
    print(f"ImageProcessor инициализирован")
    print(f"Поддерживаемые форматы ввода: {IMAGE_CONFIG['supported_formats']['input']}")
    print(f"Поддерживаемые форматы вывода: {IMAGE_CONFIG['supported_formats']['output']}")
    print(f"Позиции логотипа: {list(LOGO_POSITIONS.keys())}")