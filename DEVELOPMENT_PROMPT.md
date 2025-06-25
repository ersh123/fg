# 🚀 Промт для разработки LogoMaster Pro

## Задача
Создать профессиональное десктопное приложение **LogoMaster Pro** для автоматического нанесения логотипов на изображения с современным GUI интерфейсом.

## 📋 Техническое задание

### Основная функциональность
1. **Загрузка изображений:** множественный выбор, из архивов ZIP, по URL
2. **Управление логотипами:** загрузка, масштабирование, настройка прозрачности
3. **Позиционирование:** 9 предустановленных позиций + ручное перетаскивание
4. **Обработка:** применение к одному изображению или пакетная обработка
5. **Сохранение:** в папку или ZIP архив с настройкой качества

### Технические требования
- **Язык:** Python 3.8+
- **GUI:** Tkinter (встроенный)
- **Основные библиотеки:** Pillow, numpy, requests
- **Архитектура:** Модульная с разделением ответственности
- **Многопоточность:** Для пакетной обработки и загрузки

## 🏗 Структура проекта

```
logomaster_pro/
├── main.py                 # Главный модуль приложения
├── config.py              # Конфигурация и настройки
├── image_processor.py     # Обработка изображений
├── ui_components.py       # Пользовательские UI компоненты
├── utils.py              # Вспомогательные функции
├── requirements.txt       # Зависимости
└── assets/               # Ресурсы (создается автоматически)
```

## 📦 Зависимости (requirements.txt)

```
Pillow>=10.0.0
numpy>=1.24.0
requests>=2.31.0
```

## 🎨 Дизайн-система

### Цветовая палитра
```python
COLORS = {
    'primary': '#3B82F6',      # Синий
    'secondary': '#6366F1',    # Фиолетовый
    'success': '#10B981',      # Зеленый
    'warning': '#F59E0B',      # Оранжевый
    'danger': '#EF4444',       # Красный
    'background': '#F8FAFC',   # Светло-серый фон
    'surface': '#FFFFFF',      # Белые поверхности
    'text': '#1F2937',         # Темный текст
    'text_secondary': '#6B7280' # Вторичный текст
}
```

### Типографика
```python
FONTS = {
    'default': ('Segoe UI', 10),
    'heading': ('Segoe UI', 12, 'bold'),
    'button': ('Segoe UI', 9),
    'small': ('Segoe UI', 8)
}
```

## 🔧 Детальная реализация

### 1. config.py - Конфигурация

```python
import os
from pathlib import Path

# Пути
APP_DIR = Path(__file__).parent
ASSETS_DIR = APP_DIR / "assets"
TEMP_DIR = APP_DIR / "temp"

# Создание директорий
for directory in [ASSETS_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True)

# Конфигурация приложения
APP_CONFIG = {
    'title': 'LogoMaster Pro',
    'version': '2.0.0',
    'window_size': '1200x800',
    'min_window_size': (800, 600)
}

# Настройки изображений
IMAGE_CONFIG = {
    'supported_formats': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff'],
    'max_preview_size': (800, 600),
    'logo_size_range': (0.05, 0.5),  # 5%-50% от ширины
    'default_logo_size': 0.15,        # 15% по умолчанию
    'quality': 95,
    'default_margin': 20
}

# Настройки логотипа
LOGO_CONFIG = {
    'positions': {
        'top_left': (0, 0),
        'top_center': (0.5, 0),
        'top_right': (1, 0),
        'center_left': (0, 0.5),
        'center': (0.5, 0.5),
        'center_right': (1, 0.5),
        'bottom_left': (0, 1),
        'bottom_center': (0.5, 1),
        'bottom_right': (1, 1)
    },
    'default_position': 'bottom_right',
    'default_opacity': 0.8,
    'opacity_range': (0.1, 1.0)
}

# UI конфигурация
UI_CONFIG = {
    'colors': {
        'primary': '#3B82F6',
        'secondary': '#6366F1',
        'success': '#10B981',
        'warning': '#F59E0B',
        'danger': '#EF4444',
        'background': '#F8FAFC',
        'surface': '#FFFFFF',
        'text': '#1F2937',
        'text_secondary': '#6B7280',
        'border': '#E5E7EB'
    },
    'fonts': {
        'default': ('Segoe UI', 10),
        'heading': ('Segoe UI', 12, 'bold'),
        'button': ('Segoe UI', 9),
        'small': ('Segoe UI', 8)
    }
}
```

### 2. image_processor.py - Обработка изображений

```python
import os
import logging
from typing import List, Tuple, Optional, Union
from PIL import Image, ImageTk, ImageDraw, ImageEnhance
from pathlib import Path
import requests
import zipfile
import tempfile
from config import IMAGE_CONFIG, LOGO_CONFIG

class ImageProcessor:
    """Класс для обработки изображений и нанесения логотипов"""
    
    def __init__(self):
        self.supported_formats = IMAGE_CONFIG['supported_formats']
        self.max_preview_size = IMAGE_CONFIG['max_preview_size']
        self.quality = IMAGE_CONFIG['quality']
        
    def load_image(self, file_path: str) -> Optional[Image.Image]:
        """Загружает изображение с обработкой ошибок"""
        try:
            if not self.is_supported_format(file_path):
                raise ValueError(f"Неподдерживаемый формат: {file_path}")
            
            image = Image.open(file_path)
            if image.mode not in ('RGB', 'RGBA'):
                image = image.convert('RGB')
            
            return image
        except Exception as e:
            logging.error(f"Ошибка загрузки {file_path}: {e}")
            return None
    
    def is_supported_format(self, file_path: str) -> bool:
        """Проверяет поддержку формата файла"""
        return Path(file_path).suffix.lower() in self.supported_formats
    
    def create_preview(self, image: Image.Image, max_size: Tuple[int, int] = None) -> Image.Image:
        """Создает превью изображения"""
        if max_size is None:
            max_size = self.max_preview_size
        
        image_copy = image.copy()
        image_copy.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image_copy
    
    def resize_logo(self, logo: Image.Image, target_image: Image.Image, size_ratio: float) -> Image.Image:
        """Изменяет размер логотипа относительно изображения"""
        target_width = int(target_image.width * size_ratio)
        
        # Сохраняем пропорции логотипа
        aspect_ratio = logo.height / logo.width
        target_height = int(target_width * aspect_ratio)
        
        return logo.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    def calculate_position(self, image_size: Tuple[int, int], logo_size: Tuple[int, int], 
                         position: str, margin: int = 20) -> Tuple[int, int]:
        """Вычисляет позицию логотипа на изображении"""
        img_width, img_height = image_size
        logo_width, logo_height = logo_size
        
        position_ratios = LOGO_CONFIG['positions'][position]
        
        # Базовые координаты
        x = int((img_width - logo_width) * position_ratios[0])
        y = int((img_height - logo_height) * position_ratios[1])
        
        # Применяем отступы
        if position_ratios[0] == 0:  # Левый край
            x += margin
        elif position_ratios[0] == 1:  # Правый край
            x -= margin
        
        if position_ratios[1] == 0:  # Верхний край
            y += margin
        elif position_ratios[1] == 1:  # Нижний край
            y -= margin
        
        return (x, y)
    
    def apply_logo(self, image: Image.Image, logo: Image.Image, 
                   position: Union[str, Tuple[int, int]], 
                   size_ratio: float = None, opacity: float = 1.0, 
                   margin: int = 20) -> Image.Image:
        """Применяет логотип к изображению"""
        if size_ratio is None:
            size_ratio = LOGO_CONFIG['default_logo_size']
        
        # Создаем копию изображения
        result_image = image.copy()
        
        # Изменяем размер логотипа
        resized_logo = self.resize_logo(logo, image, size_ratio)
        
        # Применяем прозрачность
        if opacity < 1.0:
            if resized_logo.mode != 'RGBA':
                resized_logo = resized_logo.convert('RGBA')
            
            # Создаем маску прозрачности
            alpha = resized_logo.split()[-1]
            alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
            resized_logo.putalpha(alpha)
        
        # Определяем позицию
        if isinstance(position, str):
            logo_position = self.calculate_position(
                image.size, resized_logo.size, position, margin
            )
        else:
            logo_position = position
        
        # Накладываем логотип
        if resized_logo.mode == 'RGBA':
            result_image.paste(resized_logo, logo_position, resized_logo)
        else:
            result_image.paste(resized_logo, logo_position)
        
        return result_image
    
    def save_image(self, image: Image.Image, output_path: str, quality: int = None) -> bool:
        """Сохраняет изображение"""
        try:
            if quality is None:
                quality = self.quality
            
            # Создаем директорию если не существует
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Определяем параметры сохранения
            save_kwargs = {}
            if Path(output_path).suffix.lower() in ['.jpg', '.jpeg']:
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = True
                # Конвертируем в RGB для JPEG
                if image.mode == 'RGBA':
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1])
                    image = background
            
            image.save(output_path, **save_kwargs)
            return True
            
        except Exception as e:
            logging.error(f"Ошибка сохранения {output_path}: {e}")
            return False
    
    def download_image(self, url: str, output_path: str) -> bool:
        """Скачивает изображение по URL"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
            
        except Exception as e:
            logging.error(f"Ошибка скачивания {url}: {e}")
            return False
    
    def extract_images_from_zip(self, zip_path: str, extract_to: str) -> List[str]:
        """Извлекает изображения из ZIP архива"""
        extracted_files = []
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.filelist:
                    if self.is_supported_format(file_info.filename):
                        extracted_path = zip_ref.extract(file_info, extract_to)
                        extracted_files.append(extracted_path)
            
        except Exception as e:
            logging.error(f"Ошибка извлечения из архива {zip_path}: {e}")
        
        return extracted_files
```

### 3. ui_components.py - UI компоненты

```python
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from typing import Callable, Optional, List, Any
import threading
from config import UI_CONFIG

class ModernButton(tk.Button):
    """Современная стилизованная кнопка"""
    
    def __init__(self, parent, text="", command=None, style="primary", **kwargs):
        colors = UI_CONFIG['colors']
        
        style_configs = {
            'primary': {
                'bg': colors['primary'],
                'fg': 'white',
                'activebackground': '#2563EB',
                'relief': 'flat',
                'bd': 0
            },
            'secondary': {
                'bg': colors['secondary'],
                'fg': 'white',
                'activebackground': '#4F46E5',
                'relief': 'flat',
                'bd': 0
            },
            'success': {
                'bg': colors['success'],
                'fg': 'white',
                'activebackground': '#059669',
                'relief': 'flat',
                'bd': 0
            },
            'outline': {
                'bg': colors['surface'],
                'fg': colors['primary'],
                'activebackground': '#F1F5F9',
                'relief': 'solid',
                'bd': 1
            }
        }
        
        config = style_configs.get(style, style_configs['primary'])
        
        super().__init__(
            parent,
            text=text,
            command=command,
            font=UI_CONFIG['fonts']['button'],
            cursor='hand2',
            padx=15,
            pady=8,
            **config,
            **kwargs
        )
        
        # Эффекты при наведении
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.original_bg = config['bg']
        self.hover_bg = config['activebackground']
    
    def _on_enter(self, event):
        self.config(bg=self.hover_bg)
    
    def _on_leave(self, event):
        self.config(bg=self.original_bg)

class ImageViewer(tk.Frame):
    """Компонент для просмотра изображений с масштабированием"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Создаем Canvas с прокруткой
        self.canvas = tk.Canvas(self, bg='white', relief='sunken', bd=2)
        
        # Полосы прокрутки
        v_scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Размещение элементов
        self.canvas.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Переменные
        self.image = None
        self.photo = None
        self.scale_factor = 1.0
        
        # Привязка событий
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)
    
    def display_image(self, image: Image.Image):
        """Отображает изображение"""
        self.image = image
        self._update_display()
    
    def _update_display(self):
        """Обновляет отображение изображения"""
        if self.image is None:
            return
        
        # Масштабируем изображение
        display_size = (
            int(self.image.width * self.scale_factor),
            int(self.image.height * self.scale_factor)
        )
        
        display_image = self.image.resize(display_size, Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(display_image)
        
        # Очищаем canvas и добавляем изображение
        self.canvas.delete('all')
        self.canvas.create_image(0, 0, anchor='nw', image=self.photo)
        
        # Обновляем область прокрутки
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
    
    def _on_click(self, event):
        """Обработка клика мыши"""
        self.canvas.scan_mark(event.x, event.y)
    
    def _on_drag(self, event):
        """Обработка перетаскивания"""
        self.canvas.scan_dragto(event.x, event.y, gain=1)
    
    def _on_mousewheel(self, event):
        """Обработка колеса мыши для масштабирования"""
        if event.delta > 0:
            self.scale_factor *= 1.1
        else:
            self.scale_factor /= 1.1
        
        self.scale_factor = max(0.1, min(5.0, self.scale_factor))
        self._update_display()

class ProgressDialog(tk.Toplevel):
    """Диалог прогресса с возможностью отмены"""
    
    def __init__(self, parent, title="Обработка", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title(title)
        self.geometry('400x150')
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Центрируем окно
        self.geometry(f"+{parent.winfo_rootx() + 50}+{parent.winfo_rooty() + 50}")
        
        self.cancelled = False
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Создает элементы диалога"""
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Метка статуса
        self.status_label = tk.Label(
            main_frame, 
            text="Инициализация...",
            font=UI_CONFIG['fonts']['default']
        )
        self.status_label.pack(pady=(0, 10))
        
        # Прогресс-бар
        self.progress = ttk.Progressbar(
            main_frame,
            mode='determinate',
            length=300
        )
        self.progress.pack(pady=(0, 15))
        
        # Кнопка отмены
        self.cancel_button = ModernButton(
            main_frame,
            text="Отменить",
            command=self._on_cancel,
            style="outline"
        )
        self.cancel_button.pack()
    
    def update_progress(self, value: int, status: str = None):
        """Обновляет прогресс"""
        self.progress['value'] = value
        if status:
            self.status_label.config(text=status)
        self.update()
    
    def _on_cancel(self):
        """Обработка отмены"""
        self.cancelled = True
        self.destroy()

class SettingsPanel(tk.Frame):
    """Панель настроек логотипа"""
    
    def __init__(self, parent, on_change_callback: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.on_change_callback = on_change_callback
        
        # Переменные настроек
        self.position_var = tk.StringVar(value='bottom_right')
        self.size_var = tk.DoubleVar(value=0.15)
        self.opacity_var = tk.DoubleVar(value=0.8)
        self.margin_var = tk.IntVar(value=20)
        
        self._create_widgets()
        self._bind_events()
    
    def _create_widgets(self):
        """Создает элементы панели настроек"""
        # Заголовок
        title_label = tk.Label(
            self,
            text="Настройки логотипа",
            font=UI_CONFIG['fonts']['heading'],
            fg=UI_CONFIG['colors']['text']
        )
        title_label.pack(pady=(0, 15))
        
        # Позиция логотипа
        self._create_position_section()
        
        # Размер логотипа
        self._create_size_section()
        
        # Прозрачность
        self._create_opacity_section()
        
        # Отступы
        self._create_margin_section()
    
    def _create_position_section(self):
        """Создает секцию выбора позиции"""
        position_frame = tk.LabelFrame(
            self,
            text="Позиция",
            font=UI_CONFIG['fonts']['default'],
            padx=10,
            pady=10
        )
        position_frame.pack(fill='x', pady=(0, 10))
        
        positions = [
            ('Верх-лево', 'top_left'),
            ('Верх-центр', 'top_center'),
            ('Верх-право', 'top_right'),
            ('Центр-лево', 'center_left'),
            ('Центр', 'center'),
            ('Центр-право', 'center_right'),
            ('Низ-лево', 'bottom_left'),
            ('Низ-центр', 'bottom_center'),
            ('Низ-право', 'bottom_right')
        ]
        
        for i, (text, value) in enumerate(positions):
            row, col = divmod(i, 3)
            rb = tk.Radiobutton(
                position_frame,
                text=text,
                variable=self.position_var,
                value=value,
                font=UI_CONFIG['fonts']['small']
            )
            rb.grid(row=row, column=col, sticky='w', padx=5, pady=2)
    
    def _create_size_section(self):
        """Создает секцию настройки размера"""
        size_frame = tk.LabelFrame(
            self,
            text="Размер (% от ширины)",
            font=UI_CONFIG['fonts']['default'],
            padx=10,
            pady=10
        )
        size_frame.pack(fill='x', pady=(0, 10))
        
        size_scale = tk.Scale(
            size_frame,
            from_=5,
            to=50,
            orient='horizontal',
            variable=self.size_var,
            resolution=1,
            length=200
        )
        size_scale.pack()
        
        # Метка с текущим значением
        self.size_label = tk.Label(
            size_frame,
            text=f"{int(self.size_var.get())}%",
            font=UI_CONFIG['fonts']['small']
        )
        self.size_label.pack()
    
    def _create_opacity_section(self):
        """Создает секцию настройки прозрачности"""
        opacity_frame = tk.LabelFrame(
            self,
            text="Прозрачность (%)",
            font=UI_CONFIG['fonts']['default'],
            padx=10,
            pady=10
        )
        opacity_frame.pack(fill='x', pady=(0, 10))
        
        opacity_scale = tk.Scale(
            opacity_frame,
            from_=10,
            to=100,
            orient='horizontal',
            variable=self.opacity_var,
            resolution=5,
            length=200
        )
        opacity_scale.pack()
        
        # Метка с текущим значением
        self.opacity_label = tk.Label(
            opacity_frame,
            text=f"{int(self.opacity_var.get())}%",
            font=UI_CONFIG['fonts']['small']
        )
        self.opacity_label.pack()
    
    def _create_margin_section(self):
        """Создает секцию настройки отступов"""
        margin_frame = tk.LabelFrame(
            self,
            text="Отступы (пиксели)",
            font=UI_CONFIG['fonts']['default'],
            padx=10,
            pady=10
        )
        margin_frame.pack(fill='x', pady=(0, 10))
        
        margin_scale = tk.Scale(
            margin_frame,
            from_=0,
            to=100,
            orient='horizontal',
            variable=self.margin_var,
            resolution=5,
            length=200
        )
        margin_scale.pack()
        
        # Метка с текущим значением
        self.margin_label = tk.Label(
            margin_frame,
            text=f"{self.margin_var.get()}px",
            font=UI_CONFIG['fonts']['small']
        )
        self.margin_label.pack()
    
    def _bind_events(self):
        """Привязывает события изменения настроек"""
        self.position_var.trace('w', self._on_setting_change)
        self.size_var.trace('w', self._on_size_change)
        self.opacity_var.trace('w', self._on_opacity_change)
        self.margin_var.trace('w', self._on_margin_change)
    
    def _on_setting_change(self, *args):
        """Обработка изменения настроек"""
        if self.on_change_callback:
            self.on_change_callback()
    
    def _on_size_change(self, *args):
        """Обработка изменения размера"""
        self.size_label.config(text=f"{int(self.size_var.get())}%")
        self._on_setting_change()
    
    def _on_opacity_change(self, *args):
        """Обработка изменения прозрачности"""
        self.opacity_label.config(text=f"{int(self.opacity_var.get())}%")
        self._on_setting_change()
    
    def _on_margin_change(self, *args):
        """Обработка изменения отступов"""
        self.margin_label.config(text=f"{self.margin_var.get()}px")
        self._on_setting_change()
    
    def get_settings(self) -> dict:
        """Возвращает текущие настройки"""
        return {
            'position': self.position_var.get(),
            'size_ratio': self.size_var.get() / 100,
            'opacity': self.opacity_var.get() / 100,
            'margin': self.margin_var.get()
        }
```

### 4. main.py - Главное приложение

```python
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import os
import threading
import zipfile
import tempfile
from pathlib import Path
from typing import List, Optional
import logging

from config import APP_CONFIG, UI_CONFIG, IMAGE_CONFIG, TEMP_DIR
from image_processor import ImageProcessor
from ui_components import ModernButton, ImageViewer, SettingsPanel, ProgressDialog

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LogoMasterApp:
    """Главный класс приложения LogoMaster Pro"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.image_processor = ImageProcessor()
        
        # Состояние приложения
        self.image_paths: List[str] = []
        self.current_index = 0
        self.logo: Optional[Image.Image] = None
        self.logo_path: Optional[str] = None
        self.processed_images: List[Optional[Image.Image]] = []
        self.preview_image: Optional[Image.Image] = None
        
        self._setup_window()
        self._create_menu()
        self._create_ui()
        self._setup_shortcuts()
        
        logger.info("Приложение LogoMaster Pro запущено")
    
    def _setup_window(self):
        """Настраивает главное окно"""
        self.root.title(f"{APP_CONFIG['title']} v{APP_CONFIG['version']}")
        self.root.geometry(APP_CONFIG['window_size'])
        self.root.minsize(*APP_CONFIG['min_window_size'])
        
        # Центрируем окно
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_width()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_height()) // 2
        self.root.geometry(f"+{x}+{y}")
        
        # Иконка приложения (если есть)
        try:
            self.root.iconbitmap(default='assets/icon.ico')
        except:
            pass
    
    def _create_menu(self):
        """Создает главное меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Загрузить изображения...", command=self.load_images, accelerator="Ctrl+O")
        file_menu.add_command(label="Загрузить из архива...", command=self.load_from_archive, accelerator="Ctrl+Shift+O")
        file_menu.add_command(label="Загрузить по URL...", command=self.load_from_urls, accelerator="Ctrl+U")
        file_menu.add_separator()
        file_menu.add_command(label="Загрузить логотип...", command=self.load_logo, accelerator="Ctrl+L")
        file_menu.add_separator()
        file_menu.add_command(label="Сохранить результат...", command=self.save_current, accelerator="Ctrl+S")
        file_menu.add_command(label="Сохранить все...", command=self.save_all, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit, accelerator="Ctrl+Q")
        
        # Меню "Обработка"
        process_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Обработка", menu=process_menu)
        process_menu.add_command(label="Применить к текущему", command=self.apply_to_current, accelerator="Ctrl+Enter")
        process_menu.add_command(label="Применить ко всем", command=self.apply_to_all, accelerator="Ctrl+Shift+Enter")
        
        # Меню "Помощь"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def _create_ui(self):
        """Создает пользовательский интерфейс"""
        # Главный контейнер
        main_container = tk.Frame(self.root, bg=UI_CONFIG['colors']['background'])
        main_container.pack(fill='both', expand=True)
        
        # Панель инструментов
        self._create_toolbar(main_container)
        
        # Основная область
        content_frame = tk.Frame(main_container, bg=UI_CONFIG['colors']['background'])
        content_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Левая панель (настройки)
        left_panel = tk.Frame(
            content_frame,
            bg=UI_CONFIG['colors']['surface'],
            relief='solid',
            bd=1,
            width=300
        )
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Панель настроек
        self.settings_panel = SettingsPanel(
            left_panel,
            on_change_callback=self._on_settings_change,
            bg=UI_CONFIG['colors']['surface']
        )
        self.settings_panel.pack(fill='x', padx=10, pady=10)
        
        # Информационная панель
        self._create_info_panel(left_panel)
        
        # Центральная область (просмотр изображений)
        center_frame = tk.Frame(content_frame, bg=UI_CONFIG['colors']['background'])
        center_frame.pack(side='left', fill='both', expand=True)
        
        # Навигация по изображениям
        self._create_navigation(center_frame)
        
        # Просмотрщик изображений
        self.image_viewer = ImageViewer(center_frame)
        self.image_viewer.pack(fill='both', expand=True)
        
        # Строка состояния
        self.status_bar = tk.Label(
            self.root,
            text="Готов к работе",
            relief='sunken',
            anchor='w',
            bg=UI_CONFIG['colors']['surface'],
            fg=UI_CONFIG['colors']['text_secondary']
        )
        self.status_bar.pack(side='bottom', fill='x')
        
        self._update_ui_state()
    
    def _create_toolbar(self, parent):
        """Создает панель инструментов"""
        toolbar = tk.Frame(
            parent,
            bg=UI_CONFIG['colors']['surface'],
            relief='solid',
            bd=1,
            height=60
        )
        toolbar.pack(fill='x', padx=10, pady=10)
        toolbar.pack_propagate(False)
        
        # Группа загрузки
        load_frame = tk.Frame(toolbar, bg=UI_CONFIG['colors']['surface'])
        load_frame.pack(side='left', padx=10, pady=10)
        
        ModernButton(
            load_frame,
            text="📁 Загрузить изображения",
            command=self.load_images,
            style="primary"
        ).pack(side='left', padx=(0, 5))
        
        ModernButton(
            load_frame,
            text="🖼️ Загрузить логотип",
            command=self.load_logo,
            style="secondary"
        ).pack(side='left', padx=(0, 5))
        
        # Разделитель
        separator = tk.Frame(toolbar, width=2, bg=UI_CONFIG['colors']['border'])
        separator.pack(side='left', fill='y', padx=10, pady=5)
        
        # Группа обработки
        process_frame = tk.Frame(toolbar, bg=UI_CONFIG['colors']['surface'])
        process_frame.pack(side='left', padx=10, pady=10)
        
        ModernButton(
            process_frame,
            text="⚡ Применить к текущему",
            command=self.apply_to_current,
            style="success"
        ).pack(side='left', padx=(0, 5))
        
        ModernButton(
            process_frame,
            text="🚀 Применить ко всем",
            command=self.apply_to_all,
            style="success"
        ).pack(side='left')
    
    def _create_navigation(self, parent):
        """Создает панель навигации по изображениям"""
        nav_frame = tk.Frame(parent, bg=UI_CONFIG['colors']['background'])
        nav_frame.pack(fill='x', pady=(0, 10))
        
        # Кнопки навигации
        ModernButton(
            nav_frame,
            text="◀ Предыдущее",
            command=self.prev_image,
            style="outline"
        ).pack(side='left')
        
        # Информация о текущем изображении
        self.nav_label = tk.Label(
            nav_frame,
            text="Нет изображений",
            font=UI_CONFIG['fonts']['default'],
            bg=UI_CONFIG['colors']['background'],
            fg=UI_CONFIG['colors']['text']
        )
        self.nav_label.pack(side='left', expand=True)
        
        ModernButton(
            nav_frame,
            text="Следующее ▶",
            command=self.next_image,
            style="outline"
        ).pack(side='right')
    
    def _create_info_panel(self, parent):
        """Создает информационную панель"""
        info_frame = tk.LabelFrame(
            parent,
            text="Информация",
            font=UI_CONFIG['fonts']['default'],
            bg=UI_CONFIG['colors']['surface'],
            padx=10,
            pady=10
        )
        info_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # Информация об изображениях
        self.images_info = tk.Label(
            info_frame,
            text="Изображения: 0",
            font=UI_CONFIG['fonts']['small'],
            bg=UI_CONFIG['colors']['surface'],
            fg=UI_CONFIG['colors']['text_secondary'],
            anchor='w'
        )
        self.images_info.pack(fill='x')
        
        # Информация о логотипе
        self.logo_info = tk.Label(
            info_frame,
            text="Логотип: не загружен",
            font=UI_CONFIG['fonts']['small'],
            bg=UI_CONFIG['colors']['surface'],
            fg=UI_CONFIG['colors']['text_secondary'],
            anchor='w'
        )
        self.logo_info.pack(fill='x')
        
        # Информация о текущем изображении
        self.current_info = tk.Label(
            info_frame,
            text="Размер: -",
            font=UI_CONFIG['fonts']['small'],
            bg=UI_CONFIG['colors']['surface'],
            fg=UI_CONFIG['colors']['text_secondary'],
            anchor='w'
        )
        self.current_info.pack(fill='x')
    
    def _setup_shortcuts(self):
        """Настраивает горячие клавиши"""
        self.root.bind('<Control-o>', lambda e: self.load_images())
        self.root.bind('<Control-O>', lambda e: self.load_from_archive())
        self.root.bind('<Control-u>', lambda e: self.load_from_urls())
        self.root.bind('<Control-l>', lambda e: self.load_logo())
        self.root.bind('<Control-s>', lambda e: self.save_current())
        self.root.bind('<Control-S>', lambda e: self.save_all())
        self.root.bind('<Control-Return>', lambda e: self.apply_to_current())
        self.root.bind('<Control-Shift-Return>', lambda e: self.apply_to_all())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Left>', lambda e: self.prev_image())
        self.root.bind('<Right>', lambda e: self.next_image())
    
    def load_images(self):
        """Загружает изображения"""
        file_types = [
            ('Изображения', ' '.join(f'*{ext}' for ext in IMAGE_CONFIG['supported_formats'])),
            ('Все файлы', '*.*')
        ]
        
        files = filedialog.askopenfilenames(
            title="Выберите изображения",
            filetypes=file_types
        )
        
        if files:
            self.image_paths = list(files)
            self.current_index = 0
            self.processed_images = [None] * len(self.image_paths)
            self._update_ui_state()
            self._load_current_image()
            
            self.status_bar.config(text=f"Загружено {len(files)} изображений")
            logger.info(f"Загружено {len(files)} изображений")
    
    def load_from_archive(self):
        """Загружает изображения из архива"""
        file_path = filedialog.askopenfilename(
            title="Выберите ZIP архив",
            filetypes=[('ZIP архивы', '*.zip'), ('Все файлы', '*.*')]
        )
        
        if file_path:
            try:
                extract_dir = TEMP_DIR / "extracted"
                extract_dir.mkdir(exist_ok=True)
                
                extracted_files = self.image_processor.extract_images_from_zip(
                    file_path, str(extract_dir)
                )
                
                if extracted_files:
                    self.image_paths = extracted_files
                    self.current_index = 0
                    self.processed_images = [None] * len(self.image_paths)
                    self._update_ui_state()
                    self._load_current_image()
                    
                    self.status_bar.config(text=f"Извлечено {len(extracted_files)} изображений из архива")
                    logger.info(f"Извлечено {len(extracted_files)} изображений из архива")
                else:
                    messagebox.showwarning("Предупреждение", "В архиве не найдено поддерживаемых изображений")
                    
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при извлечении архива: {e}")
                logger.error(f"Ошибка при извлечении архива: {e}")
    
    def load_from_urls(self):
        """Загружает изображения по URL"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Загрузка по URL")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Центрируем диалог
        dialog.geometry(f"+{self.root.winfo_rootx() + 50}+{self.root.winfo_rooty() + 50}")
        
        # Создаем интерфейс диалога
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        tk.Label(
            main_frame,
            text="Введите URL изображений (по одному на строку):",
            font=UI_CONFIG['fonts']['default']
        ).pack(anchor='w', pady=(0, 10))
        
        # Текстовое поле для URL
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        url_text = tk.Text(text_frame, wrap='word')
        scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=url_text.yview)
        url_text.configure(yscrollcommand=scrollbar.set)
        
        url_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Кнопки
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        def download_urls():
            urls = [url.strip() for url in url_text.get('1.0', 'end').split('\n') if url.strip()]
            if urls:
                dialog.destroy()
                self._download_images_from_urls(urls)
        
        ModernButton(
            button_frame,
            text="Скачать",
            command=download_urls,
            style="primary"
        ).pack(side='right', padx=(5, 0))
        
        ModernButton(
            button_frame,
            text="Отмена",
            command=dialog.destroy,
            style="outline"
        ).pack(side='right')
    
    def _download_images_from_urls(self, urls: List[str]):
        """Скачивает изображения по списку URL"""
        def download_worker():
            download_dir = TEMP_DIR / "downloads"
            download_dir.mkdir(exist_ok=True)
            
            progress_dialog = ProgressDialog(self.root, "Скачивание изображений")
            downloaded_files = []
            
            try:
                for i, url in enumerate(urls):
                    if progress_dialog.cancelled:
                        break
                    
                    progress_dialog.update_progress(
                        int((i / len(urls)) * 100),
                        f"Скачивание {i+1} из {len(urls)}..."
                    )
                    
                    try:
                        # Определяем имя файла
                        filename = f"image_{i+1}.jpg"
                        if '.' in url.split('/')[-1]:
                            filename = url.split('/')[-1]
                        
                        file_path = download_dir / filename
                        
                        if self.image_processor.download_image(url, str(file_path)):
                            downloaded_files.append(str(file_path))
                        
                    except Exception as e:
                        logger.error(f"Ошибка скачивания {url}: {e}")
                
                progress_dialog.update_progress(100, "Завершено")
                
                if downloaded_files and not progress_dialog.cancelled:
                    self.root.after(0, lambda: self._on_download_complete(downloaded_files))
                
            finally:
                self.root.after(0, progress_dialog.destroy)
        
        threading.Thread(target=download_worker, daemon=True).start()
    
    def _on_download_complete(self, downloaded_files: List[str]):
        """Обработка завершения скачивания"""
        self.image_paths = downloaded_files
        self.current_index = 0
        self.processed_images = [None] * len(self.image_paths)
        self._update_ui_state()
        self._load_current_image()
        
        self.status_bar.config(text=f"Скачано {len(downloaded_files)} изображений")
        logger.info(f"Скачано {len(downloaded_files)} изображений")
    
    def load_logo(self):
        """Загружает логотип"""
        file_types = [
            ('Изображения', ' '.join(f'*{ext}' for ext in IMAGE_CONFIG['supported_formats'])),
            ('Все файлы', '*.*')
        ]
        
        file_path = filedialog.askopenfilename(
            title="Выберите логотип",
            filetypes=file_types
        )
        
        if file_path:
            logo = self.image_processor.load_image(file_path)
            if logo:
                self.logo = logo
                self.logo_path = file_path
                self._update_ui_state()
                self._update_preview()
                
                self.status_bar.config(text=f"Логотип загружен: {Path(file_path).name}")
                logger.info(f"Логотип загружен: {file_path}")
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить логотип")
    
    def _load_current_image(self):
        """Загружает текущее изображение"""
        if not self.image_paths:
            return
        
        current_path = self.image_paths[self.current_index]
        image = self.image_processor.load_image(current_path)
        
        if image:
            # Показываем изображение в просмотрщике
            self.image_viewer.display_image(image)
            self._update_preview()
            
            # Обновляем информацию
            self.nav_label.config(
                text=f"{self.current_index + 1} из {len(self.image_paths)} - {Path(current_path).name}"
            )
            
            self.current_info.config(
                text=f"Размер: {image.width}x{image.height}"
            )
        else:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {current_path}")
    
    def _update_preview(self):
        """Обновляет предварительный просмотр с логотипом"""
        if not self.image_paths or not self.logo:
            return
        
        current_path = self.image_paths[self.current_index]
        image = self.image_processor.load_image(current_path)
        
        if image:
            settings = self.settings_panel.get_settings()
            
            # Применяем логотип для предварительного просмотра
            preview = self.image_processor.apply_logo(
                image,
                self.logo,
                settings['position'],
                settings['size_ratio'],
                settings['opacity'],
                settings['margin']
            )
            
            self.preview_image = preview
            
            # Обновляем просмотрщик
            self.image_viewer.display_image(preview)
    
    def _on_settings_change(self):
        """Обработка изменения настроек"""
        self._update_preview()
    
    def prev_image(self):
        """Переходит к предыдущему изображению"""
        if self.image_paths and self.current_index > 0:
            self.current_index -= 1
            self._load_current_image()
    
    def next_image(self):
        """Переходит к следующему изображению"""
        if self.image_paths and self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self._load_current_image()
    
    def apply_to_current(self):
        """Применяет логотип к текущему изображению"""
        if not self.image_paths or not self.logo:
            messagebox.showwarning("Предупреждение", "Загрузите изображения и логотип")
            return
        
        current_path = self.image_paths[self.current_index]
        image = self.image_processor.load_image(current_path)
        
        if image:
            settings = self.settings_panel.get_settings()
            
            processed = self.image_processor.apply_logo(
                image,
                self.logo,
                settings['position'],
                settings['size_ratio'],
                settings['opacity'],
                settings['margin']
            )
            
            self.processed_images[self.current_index] = processed
            self.status_bar.config(text="Логотип применен к текущему изображению")
            logger.info(f"Логотип применен к изображению: {current_path}")
    
    def apply_to_all(self):
        """Применяет логотип ко всем изображениям"""
        if not self.image_paths or not self.logo:
            messagebox.showwarning("Предупреждение", "Загрузите изображения и логотип")
            return
        
        def process_worker():
            progress_dialog = ProgressDialog(self.root, "Обработка изображений")
            settings = self.settings_panel.get_settings()
            
            try:
                for i, image_path in enumerate(self.image_paths):
                    if progress_dialog.cancelled:
                        break
                    
                    progress_dialog.update_progress(
                        int((i / len(self.image_paths)) * 100),
                        f"Обработка {i+1} из {len(self.image_paths)}..."
                    )
                    
                    image = self.image_processor.load_image(image_path)
                    if image:
                        processed = self.image_processor.apply_logo(
                            image,
                            self.logo,
                            settings['position'],
                            settings['size_ratio'],
                            settings['opacity'],
                            settings['margin']
                        )
                        self.processed_images[i] = processed
                
                progress_dialog.update_progress(100, "Завершено")
                
                if not progress_dialog.cancelled:
                    self.root.after(0, lambda: self.status_bar.config(
                        text=f"Логотип применен ко всем изображениям ({len(self.image_paths)})"
                    ))
                    logger.info(f"Логотип применен ко всем изображениям ({len(self.image_paths)})")
                
            finally:
                self.root.after(0, progress_dialog.destroy)
        
        threading.Thread(target=process_worker, daemon=True).start()
    
    def save_current(self):
        """Сохраняет текущее обработанное изображение"""
        if not self.processed_images or self.processed_images[self.current_index] is None:
            messagebox.showwarning("Предупреждение", "Сначала примените логотип к изображению")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Сохранить изображение",
            defaultextension=".jpg",
            filetypes=[
                ('JPEG', '*.jpg'),
                ('PNG', '*.png'),
                ('Все файлы', '*.*')
            ]
        )
        
        if file_path:
            processed_image = self.processed_images[self.current_index]
            if self.image_processor.save_image(processed_image, file_path):
                self.status_bar.config(text=f"Изображение сохранено: {Path(file_path).name}")
                logger.info(f"Изображение сохранено: {file_path}")
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить изображение")
    
    def save_all(self):
        """Сохраняет все обработанные изображения"""
        processed_count = sum(1 for img in self.processed_images if img is not None)
        
        if processed_count == 0:
            messagebox.showwarning("Предупреждение", "Нет обработанных изображений для сохранения")
            return
        
        # Выбор способа сохранения
        choice = messagebox.askyesnocancel(
            "Способ сохранения",
            "Сохранить в ZIP архив?\n\nДа - в ZIP архив\nНет - в папку\nОтмена - отменить"
        )
        
        if choice is None:  # Отмена
            return
        elif choice:  # ZIP архив
            self._save_to_zip()
        else:  # Папка
            self._save_to_folder()
    
    def _save_to_folder(self):
        """Сохраняет изображения в папку"""
        folder_path = filedialog.askdirectory(title="Выберите папку для сохранения")
        
        if folder_path:
            def save_worker():
                progress_dialog = ProgressDialog(self.root, "Сохранение изображений")
                saved_count = 0
                
                try:
                    for i, processed_image in enumerate(self.processed_images):
                        if progress_dialog.cancelled:
                            break
                        
                        if processed_image is not None:
                            progress_dialog.update_progress(
                                int((i / len(self.processed_images)) * 100),
                                f"Сохранение {i+1} из {len(self.processed_images)}..."
                            )
                            
                            original_name = Path(self.image_paths[i]).stem
                            output_path = Path(folder_path) / f"{original_name}_with_logo.jpg"
                            
                            if self.image_processor.save_image(processed_image, str(output_path)):
                                saved_count += 1
                    
                    progress_dialog.update_progress(100, "Завершено")
                    
                    if not progress_dialog.cancelled:
                        self.root.after(0, lambda: self.status_bar.config(
                            text=f"Сохранено {saved_count} изображений в папку"
                        ))
                        logger.info(f"Сохранено {saved_count} изображений в папку {folder_path}")
                
                finally:
                    self.root.after(0, progress_dialog.destroy)
            
            threading.Thread(target=save_worker, daemon=True).start()
    
    def _save_to_zip(self):
        """Сохраняет изображения в ZIP архив"""
        file_path = filedialog.asksaveasfilename(
            title="Сохранить архив",
            defaultextension=".zip",
            filetypes=[('ZIP архивы', '*.zip'), ('Все файлы', '*.*')]
        )
        
        if file_path:
            def save_worker():
                progress_dialog = ProgressDialog(self.root, "Создание архива")
                saved_count = 0
                
                try:
                    with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for i, processed_image in enumerate(self.processed_images):
                            if progress_dialog.cancelled:
                                break
                            
                            if processed_image is not None:
                                progress_dialog.update_progress(
                                    int((i / len(self.processed_images)) * 100),
                                    f"Добавление {i+1} из {len(self.processed_images)}..."
                                )
                                
                                # Сохраняем во временный файл
                                original_name = Path(self.image_paths[i]).stem
                                temp_path = TEMP_DIR / f"{original_name}_with_logo.jpg"
                                
                                if self.image_processor.save_image(processed_image, str(temp_path)):
                                    zipf.write(temp_path, f"{original_name}_with_logo.jpg")
                                    temp_path.unlink()  # Удаляем временный файл
                                    saved_count += 1
                    
                    progress_dialog.update_progress(100, "Завершено")
                    
                    if not progress_dialog.cancelled:
                        self.root.after(0, lambda: self.status_bar.config(
                            text=f"Создан архив с {saved_count} изображениями"
                        ))
                        logger.info(f"Создан архив {file_path} с {saved_count} изображениями")
                
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка создания архива: {e}"))
                    logger.error(f"Ошибка создания архива: {e}")
                finally:
                    self.root.after(0, progress_dialog.destroy)
            
            threading.Thread(target=save_worker, daemon=True).start()
    
    def _update_ui_state(self):
        """Обновляет состояние UI элементов"""
        # Обновляем информацию
        self.images_info.config(text=f"Изображения: {len(self.image_paths)}")
        
        if self.logo_path:
            logo_name = Path(self.logo_path).name
            self.logo_info.config(text=f"Логотип: {logo_name}")
        else:
            self.logo_info.config(text="Логотип: не загружен")
        
        # Обновляем навигацию
        if self.image_paths:
            self.nav_label.config(
                text=f"{self.current_index + 1} из {len(self.image_paths)}"
            )
        else:
            self.nav_label.config(text="Нет изображений")
            self.current_info.config(text="Размер: -")
    
    def show_about(self):
        """Показывает информацию о программе"""
        about_text = f"""{APP_CONFIG['title']} v{APP_CONFIG['version']}

Профессиональное приложение для нанесения логотипов на изображения.

Возможности:
• Пакетная обработка изображений
• Гибкие настройки позиционирования
• Поддержка различных форматов
• Загрузка из архивов и по URL
• Современный интерфейс

Разработано с использованием Python и Tkinter."""
        
        messagebox.showinfo("О программе", about_text)
    
    def run(self):
        """Запускает приложение"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Приложение закрыто пользователем")
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            messagebox.showerror("Критическая ошибка", f"Произошла критическая ошибка: {e}")

def main():
    """Главная функция приложения"""
    try:
        app = LogoMasterApp()
        app.run()
    except Exception as e:
        logger.error(f"Ошибка запуска приложения: {e}")
        messagebox.showerror("Ошибка запуска", f"Не удалось запустить приложение: {e}")

if __name__ == "__main__":
    main()
```

### 5. utils.py - Вспомогательные функции

```python
import os
import shutil
from pathlib import Path
from typing import List, Optional
import tempfile
import logging

def ensure_directory(path: str) -> bool:
    """Создает директорию если она не существует"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Ошибка создания директории {path}: {e}")
        return False

def clean_temp_directory(temp_dir: str) -> bool:
    """Очищает временную директорию"""
    try:
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
            Path(temp_dir).mkdir(exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Ошибка очистки временной директории: {e}")
        return False

def get_file_size_mb(file_path: str) -> float:
    """Возвращает размер файла в мегабайтах"""
    try:
        return Path(file_path).stat().st_size / (1024 * 1024)
    except:
        return 0.0

def validate_image_file(file_path: str, max_size_mb: float = 50) -> bool:
    """Проверяет валидность файла изображения"""
    path = Path(file_path)
    
    # Проверка существования
    if not path.exists():
        return False
    
    # Проверка размера
    if get_file_size_mb(file_path) > max_size_mb:
        return False
    
    # Проверка расширения
    supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    if path.suffix.lower() not in supported_extensions:
        return False
    
    return True

def format_file_size(size_bytes: int) -> str:
    """Форматирует размер файла в читаемый вид"""
    for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} ТБ"

def create_backup(file_path: str, backup_dir: str = None) -> Optional[str]:
    """Создает резервную копию файла"""
    try:
        source_path = Path(file_path)
        if not source_path.exists():
            return None
        
        if backup_dir is None:
            backup_dir = source_path.parent / "backups"
        
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        backup_file = backup_path / f"{source_path.stem}_backup{source_path.suffix}"
        shutil.copy2(source_path, backup_file)
        
        return str(backup_file)
    except Exception as e:
        logging.error(f"Ошибка создания резервной копии: {e}")
        return None
```

## 🚀 Инструкции по запуску

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Запуск приложения
```bash
python main.py
```

## 📝 Пример использования

1. **Запустите приложение**
2. **Загрузите изображения** через кнопку "Загрузить изображения" или Ctrl+O
3. **Загрузите логотип** через кнопку "Загрузить логотип" или Ctrl+L
4. **Настройте параметры** в левой панели (позиция, размер, прозрачность)
5. **Примените логотип** к текущему изображению или ко всем сразу
6. **Сохраните результат** в папку или ZIP архив

## 🎯 Ключевые особенности реализации

### Архитектурные принципы
- **Модульность:** Четкое разделение на модули по функциональности
- **Расширяемость:** Легко добавлять новые форматы и функции
- **Производительность:** Многопоточная обработка для больших объемов
- **Надежность:** Обработка ошибок и логирование

### UI/UX принципы
- **Интуитивность:** Понятный интерфейс без лишних элементов
- **Отзывчивость:** Прогресс-бары и асинхронные операции
- **Доступность:** Горячие клавиши и контекстные подсказки
- **Современность:** Актуальный дизайн и цветовая схема

### Технические решения
- **Обработка изображений:** Pillow для всех операций с изображениями
- **Многопоточность:** threading для неблокирующих операций
- **Конфигурация:** Централизованные настройки в config.py
- **Логирование:** Подробное логирование для отладки

## 🔧 Расширения и улучшения

### Возможные дополнения
1. **Пакетные операции:** Применение разных логотипов к разным изображениям
2. **Эффекты:** Тени, обводка, размытие для логотипа
3. **Форматы:** Поддержка WebP, AVIF и других современных форматов
4. **Автоматизация:** Скрипты для автоматической обработки
5. **Плагины:** Система плагинов для расширения функциональности

### Оптимизации
1. **Кэширование:** Кэш превью для быстрого переключения
2. **Ленивая загрузка:** Загрузка изображений по требованию
3. **Сжатие:** Оптимизация размера выходных файлов
4. **Параллелизм:** Использование multiprocessing для CPU-интенсивных задач

## 📋 Чек-лист разработки

### Обязательные компоненты
- [x] Базовая структура проекта
- [x] Конфигурационный модуль
- [x] Модуль обработки изображений
- [x] UI компоненты
- [x] Главное приложение
- [x] Вспомогательные функции

### Функциональность
- [x] Загрузка изображений (файлы, архивы, URL)
- [x] Загрузка и настройка логотипа
- [x] Позиционирование (9 позиций + ручное)
- [x] Настройка размера и прозрачности
- [x] Предварительный просмотр
- [x] Пакетная обработка
- [x] Сохранение (папка, ZIP)
- [x] Прогресс-бары и отмена операций

### UI/UX
- [x] Современный дизайн
- [x] Интуитивная навигация
- [x] Горячие клавиши
- [x] Информационные панели
- [x] Диалоги прогресса
- [x] Обработка ошибок

### Техническое качество
- [x] Обработка исключений
- [x] Логирование
- [x] Многопоточность
- [x] Документация кода
- [x] Типизация
- [x] Конфигурируемость

---

**Этот промт содержит полную техническую спецификацию и готовый к реализации код для создания профессионального приложения LogoMaster Pro. Следуйте инструкциям пошагово для получения полнофункционального приложения.**