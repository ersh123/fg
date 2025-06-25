# -*- coding: utf-8 -*-
"""
ui_components.py - Современные UI компоненты для LogoMaster Pro

Содержит кастомные виджеты с современным дизайном:
- ModernButton: Стильные кнопки с эффектами
- ImageViewer: Компонент для отображения изображений
- ProgressDialog: Диалог прогресса
- SettingsPanel: Панель настроек
- StatusBar: Современная строка состояния
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading
from typing import Callable, Optional, Any
from pathlib import Path

from config import COLORS, FONTS, SIZES, UI_CONFIG, logger

class ModernButton(tk.Button):
    """
    Современная кнопка с эффектами наведения и анимацией
    """
    
    def __init__(self, parent, text="", command=None, style="primary", 
                 icon=None, width=None, height=None, **kwargs):
        """
        Инициализация современной кнопки
        
        Args:
            parent: Родительский виджет
            text: Текст кнопки
            command: Команда при нажатии
            style: Стиль кнопки ('primary', 'secondary', 'success', 'danger')
            icon: Иконка (PIL Image)
            width: Ширина кнопки
            height: Высота кнопки
        """
        self.style_name = style
        self.icon = icon
        self.is_hovered = False
        
        # Получаем цвета для стиля
        style_colors = self._get_style_colors(style)
        
        # Настройки по умолчанию
        default_config = {
            'text': text,
            'command': command,
            'font': FONTS['button'],
            'relief': 'flat',
            'borderwidth': 0,
            'cursor': 'hand2',
            'bg': style_colors['bg'],
            'fg': style_colors['fg'],
            'activebackground': style_colors['hover_bg'],
            'activeforeground': style_colors['hover_fg'],
        }
        
        if width:
            default_config['width'] = width
        if height:
            default_config['height'] = height
        
        # Объединяем с пользовательскими настройками
        default_config.update(kwargs)
        
        super().__init__(parent, **default_config)
        
        # Сохраняем цвета
        self.colors = style_colors
        
        # Подготавливаем иконку если есть
        if self.icon:
            self._prepare_icon()
        
        # Привязываем события
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)
        self.bind('<ButtonRelease-1>', self._on_release)
    
    def _get_style_colors(self, style: str) -> dict:
        """
        Получает цвета для указанного стиля
        """
        styles = {
            'primary': {
                'bg': COLORS['primary'],
                'fg': COLORS['white'],
                'hover_bg': COLORS['primary_dark'],
                'hover_fg': COLORS['white'],
                'active_bg': COLORS['primary_darker'],
            },
            'secondary': {
                'bg': COLORS['secondary'],
                'fg': COLORS['text'],
                'hover_bg': COLORS['secondary_dark'],
                'hover_fg': COLORS['text'],
                'active_bg': COLORS['secondary_darker'],
            },
            'success': {
                'bg': COLORS['success'],
                'fg': COLORS['white'],
                'hover_bg': '#28a745',
                'hover_fg': COLORS['white'],
                'active_bg': '#1e7e34',
            },
            'danger': {
                'bg': COLORS['danger'],
                'fg': COLORS['white'],
                'hover_bg': '#c82333',
                'hover_fg': COLORS['white'],
                'active_bg': '#bd2130',
            }
        }
        
        return styles.get(style, styles['primary'])
    
    def _prepare_icon(self):
        """
        Подготавливает иконку для отображения
        """
        try:
            # Изменяем размер иконки
            icon_size = SIZES['icon_small']
            if isinstance(self.icon, str):
                # Если передан путь к файлу
                icon_image = Image.open(self.icon)
            else:
                icon_image = self.icon
            
            icon_image = icon_image.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            self.icon_photo = ImageTk.PhotoImage(icon_image)
            
            # Устанавливаем иконку
            self.config(image=self.icon_photo, compound='left')
            
        except Exception as e:
            logger.error(f"Ошибка подготовки иконки: {e}")
    
    def _on_enter(self, event):
        """
        Обработчик наведения мыши
        """
        self.is_hovered = True
        self.config(
            bg=self.colors['hover_bg'],
            fg=self.colors['hover_fg']
        )
    
    def _on_leave(self, event):
        """
        Обработчик ухода мыши
        """
        self.is_hovered = False
        self.config(
            bg=self.colors['bg'],
            fg=self.colors['fg']
        )
    
    def _on_click(self, event):
        """
        Обработчик нажатия
        """
        self.config(bg=self.colors['active_bg'])
    
    def _on_release(self, event):
        """
        Обработчик отпускания
        """
        if self.is_hovered:
            self.config(bg=self.colors['hover_bg'])
        else:
            self.config(bg=self.colors['bg'])

class ImageViewer(tk.Frame):
    """
    Компонент для отображения изображений с масштабированием
    """
    
    def __init__(self, parent, **kwargs):
        """
        Инициализация просмотрщика изображений
        """
        super().__init__(parent, **kwargs)
        
        self.current_image = None
        self.current_photo = None
        self.zoom_factor = 1.0
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
        
        self._create_widgets()
        self._bind_events()
    
    def _create_widgets(self):
        """
        Создает виджеты просмотрщика
        """
        # Создаем Canvas с прокруткой
        self.canvas = tk.Canvas(
            self,
            bg=COLORS['background'],
            highlightthickness=0
        )
        
        # Полосы прокрутки
        self.v_scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        
        self.canvas.configure(
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )
        
        # Размещаем виджеты
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.v_scrollbar.grid(row=0, column=1, sticky='ns')
        self.h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Настраиваем растягивание
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Метка для отображения информации
        self.info_label = tk.Label(
            self,
            text="Перетащите изображение сюда или используйте кнопку 'Загрузить'",
            font=FONTS['text'],
            fg=COLORS['text_secondary'],
            bg=COLORS['background']
        )
        
        self.canvas.create_window(
            0, 0,
            window=self.info_label,
            anchor='center'
        )
    
    def _bind_events(self):
        """
        Привязывает события
        """
        # События мыши для перетаскивания
        self.canvas.bind('<Button-1>', self._start_drag)
        self.canvas.bind('<B1-Motion>', self._drag)
        self.canvas.bind('<ButtonRelease-1>', self._end_drag)
        
        # События колеса мыши для масштабирования
        self.canvas.bind('<MouseWheel>', self._zoom)
        self.canvas.bind('<Button-4>', self._zoom)  # Linux
        self.canvas.bind('<Button-5>', self._zoom)  # Linux
        
        # Обновление размера
        self.canvas.bind('<Configure>', self._on_canvas_configure)
    
    def display_image(self, image: Image.Image):
        """
        Отображает изображение
        
        Args:
            image: PIL Image для отображения
        """
        try:
            self.current_image = image.copy()
            self.zoom_factor = 1.0
            
            # Скрываем информационную метку
            self.info_label.place_forget()
            
            # Вычисляем размер для отображения
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                # Canvas еще не отрисован, используем размеры по умолчанию
                canvas_width = 800
                canvas_height = 600
            
            # Масштабируем изображение для помещения в canvas
            img_width, img_height = image.size
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            scale = min(scale_x, scale_y, 1.0)  # Не увеличиваем больше оригинала
            
            if scale < 1.0:
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                display_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            else:
                display_image = image
            
            # Конвертируем в PhotoImage
            self.current_photo = ImageTk.PhotoImage(display_image)
            
            # Очищаем canvas и отображаем изображение
            self.canvas.delete('all')
            
            # Центрируем изображение
            x = canvas_width // 2
            y = canvas_height // 2
            
            self.canvas.create_image(x, y, image=self.current_photo, anchor='center', tags='image')
            
            # Обновляем область прокрутки
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))
            
            logger.info(f"Изображение отображено: {image.size} -> {display_image.size}")
            
        except Exception as e:
            logger.error(f"Ошибка отображения изображения: {e}")
            self.show_error("Ошибка отображения изображения")
    
    def clear(self):
        """
        Очищает просмотрщик
        """
        self.canvas.delete('all')
        self.current_image = None
        self.current_photo = None
        self.zoom_factor = 1.0
        
        # Показываем информационную метку
        canvas_width = self.canvas.winfo_width() or 400
        canvas_height = self.canvas.winfo_height() or 300
        
        self.canvas.create_window(
            canvas_width // 2, canvas_height // 2,
            window=self.info_label,
            anchor='center'
        )
    
    def show_error(self, message: str):
        """
        Показывает сообщение об ошибке
        """
        self.canvas.delete('all')
        
        error_label = tk.Label(
            self.canvas,
            text=f"Ошибка: {message}",
            font=FONTS['text'],
            fg=COLORS['danger'],
            bg=COLORS['background']
        )
        
        canvas_width = self.canvas.winfo_width() or 400
        canvas_height = self.canvas.winfo_height() or 300
        
        self.canvas.create_window(
            canvas_width // 2, canvas_height // 2,
            window=error_label,
            anchor='center'
        )
    
    def _start_drag(self, event):
        """
        Начинает перетаскивание
        """
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.is_dragging = True
        self.canvas.config(cursor='fleur')
    
    def _drag(self, event):
        """
        Обрабатывает перетаскивание
        """
        if self.is_dragging and self.current_image:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            
            self.canvas.move('image', dx, dy)
            
            self.drag_start_x = event.x
            self.drag_start_y = event.y
    
    def _end_drag(self, event):
        """
        Заканчивает перетаскивание
        """
        self.is_dragging = False
        self.canvas.config(cursor='')
    
    def _zoom(self, event):
        """
        Обрабатывает масштабирование
        """
        if not self.current_image:
            return
        
        # Определяем направление прокрутки
        if event.delta > 0 or event.num == 4:
            scale = 1.1
        else:
            scale = 0.9
        
        # Ограничиваем масштаб
        new_zoom = self.zoom_factor * scale
        if new_zoom < 0.1 or new_zoom > 5.0:
            return
        
        self.zoom_factor = new_zoom
        
        # Пересоздаем изображение с новым масштабом
        img_width, img_height = self.current_image.size
        new_width = int(img_width * self.zoom_factor)
        new_height = int(img_height * self.zoom_factor)
        
        try:
            scaled_image = self.current_image.resize(
                (new_width, new_height), 
                Image.Resampling.LANCZOS
            )
            self.current_photo = ImageTk.PhotoImage(scaled_image)
            
            # Обновляем изображение на canvas
            self.canvas.delete('image')
            
            # Получаем текущую позицию центра
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            self.canvas.create_image(
                canvas_width // 2, canvas_height // 2,
                image=self.current_photo,
                anchor='center',
                tags='image'
            )
            
            # Обновляем область прокрутки
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))
            
        except Exception as e:
            logger.error(f"Ошибка масштабирования: {e}")
    
    def _on_canvas_configure(self, event):
        """
        Обрабатывает изменение размера canvas
        """
        if not self.current_image:
            # Обновляем позицию информационной метки
            canvas_width = event.width
            canvas_height = event.height
            
            self.canvas.coords(
                self.info_label,
                canvas_width // 2, canvas_height // 2
            )

class ProgressDialog:
    """
    Диалог прогресса для длительных операций
    """
    
    def __init__(self, parent, title="Обработка", message="Пожалуйста, подождите..."):
        """
        Инициализация диалога прогресса
        """
        self.parent = parent
        self.cancelled = False
        
        # Создаем окно
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("400x150")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Центрируем окно
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (150 // 2)
        self.window.geometry(f"400x150+{x}+{y}")
        
        # Создаем виджеты
        self._create_widgets(message)
        
        # Обработчик закрытия
        self.window.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def _create_widgets(self, message):
        """
        Создает виджеты диалога
        """
        main_frame = tk.Frame(self.window, bg=COLORS['background'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Сообщение
        self.message_label = tk.Label(
            main_frame,
            text=message,
            font=FONTS['text'],
            fg=COLORS['text'],
            bg=COLORS['background']
        )
        self.message_label.pack(pady=(0, 10))
        
        # Прогресс-бар
        self.progress = ttk.Progressbar(
            main_frame,
            mode='determinate',
            length=350
        )
        self.progress.pack(pady=(0, 10))
        
        # Метка с процентами
        self.percent_label = tk.Label(
            main_frame,
            text="0%",
            font=FONTS['small'],
            fg=COLORS['text_secondary'],
            bg=COLORS['background']
        )
        self.percent_label.pack(pady=(0, 10))
        
        # Кнопка отмены
        self.cancel_button = ModernButton(
            main_frame,
            text="Отмена",
            command=self.cancel,
            style="secondary"
        )
        self.cancel_button.pack()
    
    def update_progress(self, current, total, message=None):
        """
        Обновляет прогресс
        
        Args:
            current: Текущее значение
            total: Общее количество
            message: Сообщение (опционально)
        """
        if self.cancelled:
            return
        
        try:
            # Обновляем прогресс-бар
            progress_value = (current / total) * 100 if total > 0 else 0
            self.progress['value'] = progress_value
            
            # Обновляем процент
            self.percent_label.config(text=f"{progress_value:.1f}%")
            
            # Обновляем сообщение если передано
            if message:
                self.message_label.config(text=message)
            
            # Обновляем интерфейс
            self.window.update()
            
        except tk.TclError:
            # Окно было закрыто
            self.cancelled = True
    
    def cancel(self):
        """
        Отменяет операцию
        """
        self.cancelled = True
        self.close()
    
    def close(self):
        """
        Закрывает диалог
        """
        try:
            self.window.destroy()
        except tk.TclError:
            pass
    
    def is_cancelled(self):
        """
        Проверяет, была ли отменена операция
        """
        return self.cancelled

class SettingsPanel(tk.Frame):
    """
    Панель настроек приложения
    """
    
    def __init__(self, parent, on_change_callback=None, **kwargs):
        """
        Инициализация панели настроек
        
        Args:
            parent: Родительский виджет
            on_change_callback: Функция обратного вызова при изменении настроек
        """
        super().__init__(parent, **kwargs)
        
        self.on_change_callback = on_change_callback
        self.settings = {}
        
        self._create_widgets()
    
    def _create_widgets(self):
        """
        Создает виджеты панели настроек
        """
        # Заголовок
        title_label = tk.Label(
            self,
            text="Настройки логотипа",
            font=FONTS['heading'],
            fg=COLORS['text'],
            bg=COLORS['background']
        )
        title_label.pack(pady=(0, 10), anchor='w')
        
        # Позиция логотипа
        self._create_position_section()
        
        # Размер логотипа
        self._create_size_section()
        
        # Прозрачность
        self._create_opacity_section()
        
        # Отступы
        self._create_margin_section()
    
    def _create_position_section(self):
        """
        Создает секцию выбора позиции
        """
        frame = tk.Frame(self, bg=COLORS['background'])
        frame.pack(fill='x', pady=(0, 10))
        
        label = tk.Label(
            frame,
            text="Позиция:",
            font=FONTS['text'],
            fg=COLORS['text'],
            bg=COLORS['background']
        )
        label.pack(anchor='w')
        
        self.position_var = tk.StringVar(value="bottom_right")
        
        positions = [
            ("Верх слева", "top_left"),
            ("Верх по центру", "top_center"),
            ("Верх справа", "top_right"),
            ("По центру слева", "center_left"),
            ("По центру", "center"),
            ("По центру справа", "center_right"),
            ("Низ слева", "bottom_left"),
            ("Низ по центру", "bottom_center"),
            ("Низ справа", "bottom_right"),
        ]
        
        for text, value in positions:
            rb = tk.Radiobutton(
                frame,
                text=text,
                variable=self.position_var,
                value=value,
                font=FONTS['small'],
                fg=COLORS['text'],
                bg=COLORS['background'],
                selectcolor=COLORS['secondary'],
                command=self._on_setting_change
            )
            rb.pack(anchor='w')
    
    def _create_size_section(self):
        """
        Создает секцию настройки размера
        """
        frame = tk.Frame(self, bg=COLORS['background'])
        frame.pack(fill='x', pady=(0, 10))
        
        label = tk.Label(
            frame,
            text="Размер логотипа:",
            font=FONTS['text'],
            fg=COLORS['text'],
            bg=COLORS['background']
        )
        label.pack(anchor='w')
        
        self.size_var = tk.DoubleVar(value=0.2)
        
        size_frame = tk.Frame(frame, bg=COLORS['background'])
        size_frame.pack(fill='x', pady=(5, 0))
        
        self.size_scale = tk.Scale(
            size_frame,
            from_=0.05,
            to=0.5,
            resolution=0.01,
            orient='horizontal',
            variable=self.size_var,
            font=FONTS['small'],
            fg=COLORS['text'],
            bg=COLORS['background'],
            highlightthickness=0,
            command=self._on_setting_change
        )
        self.size_scale.pack(side='left', fill='x', expand=True)
        
        self.size_label = tk.Label(
            size_frame,
            text="20%",
            font=FONTS['small'],
            fg=COLORS['text_secondary'],
            bg=COLORS['background'],
            width=5
        )
        self.size_label.pack(side='right')
    
    def _create_opacity_section(self):
        """
        Создает секцию настройки прозрачности
        """
        frame = tk.Frame(self, bg=COLORS['background'])
        frame.pack(fill='x', pady=(0, 10))
        
        label = tk.Label(
            frame,
            text="Прозрачность:",
            font=FONTS['text'],
            fg=COLORS['text'],
            bg=COLORS['background']
        )
        label.pack(anchor='w')
        
        self.opacity_var = tk.DoubleVar(value=1.0)
        
        opacity_frame = tk.Frame(frame, bg=COLORS['background'])
        opacity_frame.pack(fill='x', pady=(5, 0))
        
        self.opacity_scale = tk.Scale(
            opacity_frame,
            from_=0.1,
            to=1.0,
            resolution=0.1,
            orient='horizontal',
            variable=self.opacity_var,
            font=FONTS['small'],
            fg=COLORS['text'],
            bg=COLORS['background'],
            highlightthickness=0,
            command=self._on_setting_change
        )
        self.opacity_scale.pack(side='left', fill='x', expand=True)
        
        self.opacity_label = tk.Label(
            opacity_frame,
            text="100%",
            font=FONTS['small'],
            fg=COLORS['text_secondary'],
            bg=COLORS['background'],
            width=5
        )
        self.opacity_label.pack(side='right')
    
    def _create_margin_section(self):
        """
        Создает секцию настройки отступов
        """
        frame = tk.Frame(self, bg=COLORS['background'])
        frame.pack(fill='x', pady=(0, 10))
        
        label = tk.Label(
            frame,
            text="Отступ от края:",
            font=FONTS['text'],
            fg=COLORS['text'],
            bg=COLORS['background']
        )
        label.pack(anchor='w')
        
        self.margin_var = tk.IntVar(value=20)
        
        margin_frame = tk.Frame(frame, bg=COLORS['background'])
        margin_frame.pack(fill='x', pady=(5, 0))
        
        self.margin_scale = tk.Scale(
            margin_frame,
            from_=0,
            to=100,
            resolution=5,
            orient='horizontal',
            variable=self.margin_var,
            font=FONTS['small'],
            fg=COLORS['text'],
            bg=COLORS['background'],
            highlightthickness=0,
            command=self._on_setting_change
        )
        self.margin_scale.pack(side='left', fill='x', expand=True)
        
        self.margin_label = tk.Label(
            margin_frame,
            text="20px",
            font=FONTS['small'],
            fg=COLORS['text_secondary'],
            bg=COLORS['background'],
            width=5
        )
        self.margin_label.pack(side='right')
    
    def _on_setting_change(self, *args):
        """
        Обрабатывает изменение настроек
        """
        # Обновляем метки
        self.size_label.config(text=f"{int(self.size_var.get() * 100)}%")
        self.opacity_label.config(text=f"{int(self.opacity_var.get() * 100)}%")
        self.margin_label.config(text=f"{self.margin_var.get()}px")
        
        # Собираем текущие настройки
        self.settings = {
            'position': self.position_var.get(),
            'size': self.size_var.get(),
            'opacity': self.opacity_var.get(),
            'margin': self.margin_var.get(),
        }
        
        # Вызываем callback если установлен
        if self.on_change_callback:
            self.on_change_callback(self.settings)
    
    def get_settings(self) -> dict:
        """
        Возвращает текущие настройки
        """
        return self.settings.copy()
    
    def set_settings(self, settings: dict):
        """
        Устанавливает настройки
        
        Args:
            settings: Словарь с настройками
        """
        if 'position' in settings:
            self.position_var.set(settings['position'])
        if 'size' in settings:
            self.size_var.set(settings['size'])
        if 'opacity' in settings:
            self.opacity_var.set(settings['opacity'])
        if 'margin' in settings:
            self.margin_var.set(settings['margin'])
        
        self._on_setting_change()

class StatusBar(tk.Frame):
    """
    Современная строка состояния
    """
    
    def __init__(self, parent, **kwargs):
        """
        Инициализация строки состояния
        """
        super().__init__(parent, **kwargs)
        
        self.config(
            bg=COLORS['secondary'],
            height=30,
            relief='flat',
            bd=1
        )
        
        self._create_widgets()
    
    def _create_widgets(self):
        """
        Создает виджеты строки состояния
        """
        # Основное сообщение
        self.status_label = tk.Label(
            self,
            text="Готов",
            font=FONTS['small'],
            fg=COLORS['text'],
            bg=COLORS['secondary'],
            anchor='w'
        )
        self.status_label.pack(side='left', padx=10, fill='x', expand=True)
        
        # Дополнительная информация
        self.info_label = tk.Label(
            self,
            text="",
            font=FONTS['small'],
            fg=COLORS['text_secondary'],
            bg=COLORS['secondary'],
            anchor='e'
        )
        self.info_label.pack(side='right', padx=10)
    
    def set_status(self, message: str, info: str = ""):
        """
        Устанавливает сообщение в строке состояния
        
        Args:
            message: Основное сообщение
            info: Дополнительная информация
        """
        self.status_label.config(text=message)
        self.info_label.config(text=info)
        self.update_idletasks()
    
    def clear(self):
        """
        Очищает строку состояния
        """
        self.set_status("Готов", "")

if __name__ == '__main__':
    # Тестирование компонентов
    root = tk.Tk()
    root.title("Тест UI компонентов")
    root.geometry("800x600")
    root.configure(bg=COLORS['background'])
    
    # Тестируем кнопки
    button_frame = tk.Frame(root, bg=COLORS['background'])
    button_frame.pack(pady=10)
    
    ModernButton(button_frame, text="Primary", style="primary").pack(side='left', padx=5)
    ModernButton(button_frame, text="Secondary", style="secondary").pack(side='left', padx=5)
    ModernButton(button_frame, text="Success", style="success").pack(side='left', padx=5)
    ModernButton(button_frame, text="Danger", style="danger").pack(side='left', padx=5)
    
    # Тестируем просмотрщик изображений
    viewer = ImageViewer(root)
    viewer.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Тестируем строку состояния
    status = StatusBar(root)
    status.pack(fill='x', side='bottom')
    status.set_status("Тестирование компонентов", "Все работает")
    
    root.mainloop()