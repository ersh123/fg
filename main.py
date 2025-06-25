# -*- coding: utf-8 -*-
"""
main.py - Главный модуль приложения LogoMaster Pro

Главное окно приложения с полным пользовательским интерфейсом:
- Загрузка и отображение изображений
- Применение логотипов с настройками
- Пакетная обработка
- Сохранение результатов
- Современный UI с drag & drop
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from PIL import Image, ImageTk

# Добавляем текущую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    APP_CONFIG, COLORS, FONTS, SIZES, UI_CONFIG, MESSAGES,
    get_config, logger, setup_logging
)
from image_processor import ImageProcessor
from ui_components import (
    ModernButton, ImageViewer, ProgressDialog, 
    SettingsPanel, StatusBar
)
from utils import (
    ensure_directory, validate_image_file, create_backup,
    create_zip_archive, get_unique_filename, format_file_size,
    PerformanceTimer, cleanup_temp_directory
)

class LogoMasterApp:
    """
    Главный класс приложения LogoMaster Pro
    """
    
    def __init__(self):
        """
        Инициализация приложения
        """
        # Настройка логирования
        setup_logging()
        logger.info("Запуск LogoMaster Pro")
        
        # Инициализация компонентов
        self.image_processor = ImageProcessor()
        self.current_images = []  # Список загруженных изображений
        self.current_image_index = 0
        self.processed_images = {}  # Кэш обработанных изображений
        self.logo_loaded = False
        self.is_processing = False
        
        # Создание главного окна
        self.root = tk.Tk()
        self._setup_window()
        self._create_ui()
        self._setup_drag_drop()
        
        # Очистка временных файлов при запуске
        cleanup_temp_directory()
        
        logger.info("Приложение инициализировано")
    
    def _setup_window(self):
        """
        Настройка главного окна
        """
        self.root.title(APP_CONFIG['title'])
        self.root.geometry(f"{APP_CONFIG['window_size'][0]}x{APP_CONFIG['window_size'][1]}")
        self.root.minsize(800, 600)
        self.root.configure(bg=COLORS['background'])
        
        # Иконка приложения (если есть)
        try:
            icon_path = get_config('paths')['assets_dir'] / 'icon.ico'
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception as e:
            logger.debug(f"Не удалось загрузить иконку: {e}")
        
        # Обработчик закрытия
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_ui(self):
        """
        Создание пользовательского интерфейса
        """
        # Главный контейнер
        main_container = tk.Frame(self.root, bg=COLORS['background'])
        main_container.pack(fill='both', expand=True)
        
        # Создаем компоненты
        self._create_toolbar(main_container)
        self._create_main_content(main_container)
        self._create_status_bar(main_container)
    
    def _create_toolbar(self, parent):
        """
        Создание панели инструментов
        """
        toolbar = tk.Frame(parent, bg=COLORS['secondary'], height=60)
        toolbar.pack(fill='x', pady=(0, 1))
        toolbar.pack_propagate(False)
        
        # Левая группа кнопок
        left_frame = tk.Frame(toolbar, bg=COLORS['secondary'])
        left_frame.pack(side='left', padx=10, pady=10)
        
        # Кнопка загрузки изображений
        self.load_images_btn = ModernButton(
            left_frame,
            text="📁 Загрузить изображения",
            command=self._load_images,
            style="primary",
            width=20
        )
        self.load_images_btn.pack(side='left', padx=(0, 5))
        
        # Кнопка загрузки логотипа
        self.load_logo_btn = ModernButton(
            left_frame,
            text="🏷️ Загрузить логотип",
            command=self._load_logo,
            style="secondary",
            width=18
        )
        self.load_logo_btn.pack(side='left', padx=5)
        
        # Кнопка применения логотипа
        self.apply_logo_btn = ModernButton(
            left_frame,
            text="✨ Применить логотип",
            command=self._apply_logo_to_current,
            style="success",
            width=18,
            state='disabled'
        )
        self.apply_logo_btn.pack(side='left', padx=5)
        
        # Правая группа кнопок
        right_frame = tk.Frame(toolbar, bg=COLORS['secondary'])
        right_frame.pack(side='right', padx=10, pady=10)
        
        # Кнопка пакетной обработки
        self.batch_btn = ModernButton(
            right_frame,
            text="⚡ Пакетная обработка",
            command=self._batch_process,
            style="primary",
            width=20,
            state='disabled'
        )
        self.batch_btn.pack(side='right', padx=5)
        
        # Кнопка сохранения
        self.save_btn = ModernButton(
            right_frame,
            text="💾 Сохранить",
            command=self._show_save_menu,
            style="success",
            width=15,
            state='disabled'
        )
        self.save_btn.pack(side='right', padx=5)
    
    def _create_main_content(self, parent):
        """
        Создание основного содержимого
        """
        content_frame = tk.Frame(parent, bg=COLORS['background'])
        content_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Левая панель (настройки и информация)
        left_panel = tk.Frame(content_frame, bg=COLORS['surface'], width=300)
        left_panel.pack(side='left', fill='y', padx=(0, 5))
        left_panel.pack_propagate(False)
        
        self._create_left_panel(left_panel)
        
        # Правая панель (просмотр изображений)
        right_panel = tk.Frame(content_frame, bg=COLORS['surface'])
        right_panel.pack(side='right', fill='both', expand=True)
        
        self._create_right_panel(right_panel)
    
    def _create_left_panel(self, parent):
        """
        Создание левой панели с настройками
        """
        # Заголовок панели
        header = tk.Label(
            parent,
            text="Настройки и информация",
            font=FONTS['heading'],
            fg=COLORS['text'],
            bg=COLORS['surface']
        )
        header.pack(pady=10, padx=10, anchor='w')
        
        # Панель настроек логотипа
        self.settings_panel = SettingsPanel(
            parent,
            on_change_callback=self._on_settings_change,
            bg=COLORS['surface']
        )
        self.settings_panel.pack(fill='x', padx=10, pady=(0, 10))
        
        # Разделитель
        separator = tk.Frame(parent, height=1, bg=COLORS['border'])
        separator.pack(fill='x', padx=10, pady=10)
        
        # Информация о текущем изображении
        info_frame = tk.Frame(parent, bg=COLORS['surface'])
        info_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        info_label = tk.Label(
            info_frame,
            text="Информация об изображении",
            font=FONTS['text'],
            fg=COLORS['text'],
            bg=COLORS['surface']
        )
        info_label.pack(anchor='w', pady=(0, 5))
        
        self.info_text = tk.Text(
            info_frame,
            height=8,
            width=35,
            font=FONTS['small'],
            fg=COLORS['text'],
            bg=COLORS['background'],
            relief='flat',
            borderwidth=1,
            state='disabled'
        )
        self.info_text.pack(fill='x')
        
        # Навигация по изображениям
        nav_frame = tk.Frame(parent, bg=COLORS['surface'])
        nav_frame.pack(fill='x', padx=10, pady=10)
        
        nav_label = tk.Label(
            nav_frame,
            text="Навигация",
            font=FONTS['text'],
            fg=COLORS['text'],
            bg=COLORS['surface']
        )
        nav_label.pack(anchor='w', pady=(0, 5))
        
        nav_buttons = tk.Frame(nav_frame, bg=COLORS['surface'])
        nav_buttons.pack(fill='x')
        
        self.prev_btn = ModernButton(
            nav_buttons,
            text="◀ Предыдущее",
            command=self._prev_image,
            style="secondary",
            state='disabled'
        )
        self.prev_btn.pack(side='left', fill='x', expand=True, padx=(0, 2))
        
        self.next_btn = ModernButton(
            nav_buttons,
            text="Следующее ▶",
            command=self._next_image,
            style="secondary",
            state='disabled'
        )
        self.next_btn.pack(side='right', fill='x', expand=True, padx=(2, 0))
        
        # Счетчик изображений
        self.image_counter = tk.Label(
            nav_frame,
            text="0 / 0",
            font=FONTS['small'],
            fg=COLORS['text_secondary'],
            bg=COLORS['surface']
        )
        self.image_counter.pack(pady=(5, 0))
    
    def _create_right_panel(self, parent):
        """
        Создание правой панели с просмотром изображений
        """
        # Заголовок
        header_frame = tk.Frame(parent, bg=COLORS['surface'], height=40)
        header_frame.pack(fill='x', padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(
            header_frame,
            text="Просмотр изображений",
            font=FONTS['heading'],
            fg=COLORS['text'],
            bg=COLORS['surface']
        )
        header_label.pack(side='left', pady=10)
        
        # Кнопки управления просмотром
        view_controls = tk.Frame(header_frame, bg=COLORS['surface'])
        view_controls.pack(side='right', pady=5)
        
        self.zoom_in_btn = ModernButton(
            view_controls,
            text="🔍+",
            command=self._zoom_in,
            style="secondary",
            width=5
        )
        self.zoom_in_btn.pack(side='left', padx=2)
        
        self.zoom_out_btn = ModernButton(
            view_controls,
            text="🔍-",
            command=self._zoom_out,
            style="secondary",
            width=5
        )
        self.zoom_out_btn.pack(side='left', padx=2)
        
        self.fit_btn = ModernButton(
            view_controls,
            text="📐",
            command=self._fit_to_window,
            style="secondary",
            width=5
        )
        self.fit_btn.pack(side='left', padx=2)
        
        # Просмотрщик изображений
        viewer_frame = tk.Frame(parent, bg=COLORS['background'])
        viewer_frame.pack(fill='both', expand=True, padx=10, pady=(5, 10))
        
        self.image_viewer = ImageViewer(viewer_frame, bg=COLORS['background'])
        self.image_viewer.pack(fill='both', expand=True)
    
    def _create_status_bar(self, parent):
        """
        Создание строки состояния
        """
        self.status_bar = StatusBar(parent)
        self.status_bar.pack(fill='x', side='bottom')
        self.status_bar.set_status(MESSAGES['ready'])
    
    def _setup_drag_drop(self):
        """
        Настройка drag & drop функциональности
        """
        try:
            # Простая реализация drag & drop через tkinter
            self.root.drop_target_register('DND_Files')
            self.root.dnd_bind('<<Drop>>', self._on_drop)
        except Exception as e:
            logger.debug(f"Drag & drop не поддерживается: {e}")
            # Альтернативная реализация через события мыши
            self._setup_alternative_drop()
    
    def _setup_alternative_drop(self):
        """
        Альтернативная реализация drag & drop
        """
        # Привязываем события к области просмотра изображений
        self.image_viewer.bind('<Button-1>', self._on_click_for_file_dialog)
        
        # Добавляем подсказку
        drop_hint = tk.Label(
            self.image_viewer,
            text="Нажмите здесь для выбора файлов\nили используйте кнопку 'Загрузить изображения'",
            font=FONTS['text'],
            fg=COLORS['text_secondary'],
            bg=COLORS['background']
        )
        drop_hint.place(relx=0.5, rely=0.5, anchor='center')
        self.drop_hint = drop_hint
    
    def _on_click_for_file_dialog(self, event):
        """
        Обработчик клика для открытия диалога выбора файлов
        """
        if not self.current_images:
            self._load_images()
    
    def _on_drop(self, event):
        """
        Обработчик события drop
        """
        try:
            files = event.data.split()
            image_files = []
            
            for file_path in files:
                file_path = file_path.strip('{}"')  # Очистка от лишних символов
                if os.path.isfile(file_path):
                    is_valid, _ = validate_image_file(file_path)
                    if is_valid:
                        image_files.append(file_path)
                elif os.path.isdir(file_path):
                    # Сканируем директорию
                    dir_images = self.image_processor.load_images_from_directory(file_path)
                    image_files.extend(dir_images)
            
            if image_files:
                self._load_image_files(image_files)
            else:
                messagebox.showwarning(
                    "Предупреждение",
                    "Не найдено подходящих изображений"
                )
                
        except Exception as e:
            logger.error(f"Ошибка обработки drop: {e}")
            messagebox.showerror("Ошибка", f"Ошибка загрузки файлов: {e}")
    
    def _load_images(self):
        """
        Загрузка изображений через диалог
        """
        try:
            file_types = [
                ("Изображения", "*.jpg *.jpeg *.png *.bmp *.tiff *.gif"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("Все файлы", "*.*")
            ]
            
            files = filedialog.askopenfilenames(
                title="Выберите изображения",
                filetypes=file_types,
                initialdir=get_config('paths')['last_open_dir']
            )
            
            if files:
                # Сохраняем последнюю директорию
                last_dir = os.path.dirname(files[0])
                # Здесь можно сохранить в настройки
                
                self._load_image_files(list(files))
                
        except Exception as e:
            logger.error(f"Ошибка загрузки изображений: {e}")
            messagebox.showerror("Ошибка", f"Ошибка загрузки изображений: {e}")
    
    def _load_image_files(self, file_paths: List[str]):
        """
        Загружает список файлов изображений
        
        Args:
            file_paths: Список путей к файлам
        """
        try:
            valid_files = []
            
            # Валидируем файлы
            for file_path in file_paths:
                is_valid, error_msg = validate_image_file(file_path)
                if is_valid:
                    valid_files.append(file_path)
                else:
                    logger.warning(f"Пропуск файла {file_path}: {error_msg}")
            
            if not valid_files:
                messagebox.showwarning(
                    "Предупреждение",
                    "Не найдено подходящих изображений"
                )
                return
            
            # Загружаем изображения
            self.current_images = valid_files
            self.current_image_index = 0
            self.processed_images.clear()
            
            # Обновляем UI
            self._update_ui_state()
            self._display_current_image()
            self._update_image_info()
            
            # Скрываем подсказку
            if hasattr(self, 'drop_hint'):
                self.drop_hint.place_forget()
            
            self.status_bar.set_status(
                f"Загружено {len(valid_files)} изображений",
                f"Размер: {sum(os.path.getsize(f) for f in valid_files) / (1024*1024):.1f} МБ"
            )
            
            logger.info(f"Загружено {len(valid_files)} изображений")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки файлов: {e}")
            messagebox.showerror("Ошибка", f"Ошибка загрузки файлов: {e}")
    
    def _load_logo(self):
        """
        Загрузка логотипа
        """
        try:
            file_types = [
                ("Изображения логотипов", "*.png *.jpg *.jpeg *.bmp"),
                ("PNG (рекомендуется)", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("Все файлы", "*.*")
            ]
            
            file_path = filedialog.askopenfilename(
                title="Выберите логотип",
                filetypes=file_types,
                initialdir=get_config('paths')['last_logo_dir']
            )
            
            if file_path:
                # Валидируем логотип
                is_valid, error_msg = validate_image_file(file_path)
                if not is_valid:
                    messagebox.showerror("Ошибка", f"Неподходящий файл логотипа: {error_msg}")
                    return
                
                # Загружаем логотип
                if self.image_processor.load_logo(file_path):
                    self.logo_loaded = True
                    self._update_ui_state()
                    
                    # Обновляем статус
                    logo_name = os.path.basename(file_path)
                    self.status_bar.set_status(
                        f"Логотип загружен: {logo_name}",
                        f"Размер: {format_file_size(os.path.getsize(file_path))}"
                    )
                    
                    logger.info(f"Логотип загружен: {file_path}")
                else:
                    messagebox.showerror("Ошибка", "Не удалось загрузить логотип")
                
        except Exception as e:
            logger.error(f"Ошибка загрузки логотипа: {e}")
            messagebox.showerror("Ошибка", f"Ошибка загрузки логотипа: {e}")
    
    def _apply_logo_to_current(self):
        """
        Применение логотипа к текущему изображению
        """
        if not self.current_images or not self.logo_loaded:
            return
        
        try:
            current_file = self.current_images[self.current_image_index]
            
            # Загружаем изображение если не в кэше
            if current_file not in self.processed_images:
                image = self.image_processor.load_image(current_file)
                if image is None:
                    messagebox.showerror("Ошибка", "Не удалось загрузить изображение")
                    return
            else:
                image = self.processed_images[current_file]['original']
            
            # Получаем настройки
            settings = self.settings_panel.get_settings()
            
            # Применяем логотип
            with PerformanceTimer("Применение логотипа") as timer:
                processed_image = self.image_processor.apply_logo(image, **settings)
            
            if processed_image:
                # Сохраняем в кэш
                self.processed_images[current_file] = {
                    'original': image,
                    'processed': processed_image,
                    'settings': settings.copy()
                }
                
                # Отображаем результат
                self._display_processed_image(processed_image)
                
                # Обновляем UI
                self._update_ui_state()
                
                self.status_bar.set_status(
                    "Логотип применен к изображению",
                    f"Время: {timer.get_duration():.2f} сек"
                )
                
                logger.info(f"Логотип применен к {current_file}")
            else:
                messagebox.showerror("Ошибка", "Не удалось применить логотип")
                
        except Exception as e:
            logger.error(f"Ошибка применения логотипа: {e}")
            messagebox.showerror("Ошибка", f"Ошибка применения логотипа: {e}")
    
    def _batch_process(self):
        """
        Пакетная обработка всех изображений
        """
        if not self.current_images or not self.logo_loaded:
            return
        
        try:
            # Выбираем директорию для сохранения
            output_dir = filedialog.askdirectory(
                title="Выберите папку для сохранения обработанных изображений",
                initialdir=get_config('paths')['last_save_dir']
            )
            
            if not output_dir:
                return
            
            # Получаем настройки
            settings = self.settings_panel.get_settings()
            
            # Создаем диалог прогресса
            progress_dialog = ProgressDialog(
                self.root,
                "Пакетная обработка",
                "Обработка изображений..."
            )
            
            def progress_callback(current, total, message):
                if not progress_dialog.is_cancelled():
                    progress_dialog.update_progress(current, total, message)
            
            def process_thread():
                try:
                    self.is_processing = True
                    self._update_ui_state()
                    
                    with PerformanceTimer("Пакетная обработка") as timer:
                        processed_files = self.image_processor.batch_process(
                            self.current_images,
                            output_dir,
                            progress_callback,
                            **settings
                        )
                    
                    if not progress_dialog.is_cancelled():
                        progress_dialog.close()
                        
                        if processed_files:
                            messagebox.showinfo(
                                "Успех",
                                f"Обработано {len(processed_files)} из {len(self.current_images)} изображений\n"
                                f"Время: {timer.get_duration():.1f} сек\n"
                                f"Результаты сохранены в: {output_dir}"
                            )
                            
                            self.status_bar.set_status(
                                f"Пакетная обработка завершена: {len(processed_files)} файлов",
                                f"Время: {timer.get_duration():.1f} сек"
                            )
                        else:
                            messagebox.showwarning(
                                "Предупреждение",
                                "Не удалось обработать ни одного изображения"
                            )
                    
                except Exception as e:
                    progress_dialog.close()
                    logger.error(f"Ошибка пакетной обработки: {e}")
                    messagebox.showerror("Ошибка", f"Ошибка пакетной обработки: {e}")
                
                finally:
                    self.is_processing = False
                    self.root.after(0, self._update_ui_state)
            
            # Запускаем обработку в отдельном потоке
            thread = threading.Thread(target=process_thread, daemon=True)
            thread.start()
            
        except Exception as e:
            logger.error(f"Ошибка запуска пакетной обработки: {e}")
            messagebox.showerror("Ошибка", f"Ошибка запуска пакетной обработки: {e}")
    
    def _show_save_menu(self):
        """
        Показывает меню сохранения
        """
        menu = tk.Menu(self.root, tearoff=0)
        
        menu.add_command(
            label="Сохранить текущее изображение",
            command=self._save_current_image
        )
        
        menu.add_command(
            label="Сохранить все обработанные",
            command=self._save_all_processed
        )
        
        menu.add_separator()
        
        menu.add_command(
            label="Сохранить в папку",
            command=self._save_to_folder
        )
        
        menu.add_command(
            label="Сохранить в ZIP архив",
            command=self._save_to_zip
        )
        
        # Показываем меню рядом с кнопкой
        try:
            x = self.save_btn.winfo_rootx()
            y = self.save_btn.winfo_rooty() + self.save_btn.winfo_height()
            menu.post(x, y)
        except:
            menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
    
    def _save_current_image(self):
        """
        Сохранение текущего обработанного изображения
        """
        if not self.current_images:
            return
        
        current_file = self.current_images[self.current_image_index]
        if current_file not in self.processed_images:
            messagebox.showwarning(
                "Предупреждение",
                "Текущее изображение не обработано"
            )
            return
        
        try:
            # Предлагаем имя файла
            original_name = Path(current_file).stem
            default_name = f"{original_name}_with_logo.jpg"
            
            file_path = filedialog.asksaveasfilename(
                title="Сохранить изображение",
                defaultextension=".jpg",
                initialfilename=default_name,
                filetypes=[
                    ("JPEG", "*.jpg"),
                    ("PNG", "*.png"),
                    ("Все файлы", "*.*")
                ]
            )
            
            if file_path:
                processed_image = self.processed_images[current_file]['processed']
                
                if self.image_processor.save_image(processed_image, file_path):
                    self.status_bar.set_status(
                        f"Изображение сохранено: {os.path.basename(file_path)}",
                        f"Размер: {format_file_size(os.path.getsize(file_path))}"
                    )
                    logger.info(f"Изображение сохранено: {file_path}")
                else:
                    messagebox.showerror("Ошибка", "Не удалось сохранить изображение")
                    
        except Exception as e:
            logger.error(f"Ошибка сохранения изображения: {e}")
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
    
    def _save_all_processed(self):
        """
        Сохранение всех обработанных изображений
        """
        if not self.processed_images:
            messagebox.showwarning(
                "Предупреждение",
                "Нет обработанных изображений для сохранения"
            )
            return
        
        try:
            output_dir = filedialog.askdirectory(
                title="Выберите папку для сохранения"
            )
            
            if not output_dir:
                return
            
            saved_count = 0
            
            for file_path, data in self.processed_images.items():
                try:
                    original_name = Path(file_path).stem
                    save_name = get_unique_filename(
                        output_dir,
                        f"{original_name}_with_logo",
                        ".jpg"
                    )
                    save_path = os.path.join(output_dir, save_name)
                    
                    if self.image_processor.save_image(data['processed'], save_path):
                        saved_count += 1
                        
                except Exception as e:
                    logger.error(f"Ошибка сохранения {file_path}: {e}")
            
            if saved_count > 0:
                messagebox.showinfo(
                    "Успех",
                    f"Сохранено {saved_count} из {len(self.processed_images)} изображений\n"
                    f"Папка: {output_dir}"
                )
                
                self.status_bar.set_status(
                    f"Сохранено {saved_count} изображений",
                    f"Папка: {os.path.basename(output_dir)}"
                )
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить ни одного изображения")
                
        except Exception as e:
            logger.error(f"Ошибка сохранения всех изображений: {e}")
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
    
    def _save_to_folder(self):
        """
        Сохранение в выбранную папку
        """
        self._save_all_processed()
    
    def _save_to_zip(self):
        """
        Сохранение в ZIP архив
        """
        if not self.processed_images:
            messagebox.showwarning(
                "Предупреждение",
                "Нет обработанных изображений для сохранения"
            )
            return
        
        try:
            zip_path = filedialog.asksaveasfilename(
                title="Сохранить архив",
                defaultextension=".zip",
                initialfilename="processed_images.zip",
                filetypes=[("ZIP архивы", "*.zip")]
            )
            
            if not zip_path:
                return
            
            # Создаем временные файлы
            temp_dir = get_config('paths')['temp_dir'] / 'zip_export'
            ensure_directory(str(temp_dir))
            
            temp_files = []
            
            try:
                for file_path, data in self.processed_images.items():
                    original_name = Path(file_path).stem
                    temp_name = f"{original_name}_with_logo.jpg"
                    temp_path = temp_dir / temp_name
                    
                    if self.image_processor.save_image(data['processed'], str(temp_path)):
                        temp_files.append(str(temp_path))
                
                # Создаем архив
                if create_zip_archive(temp_files, zip_path):
                    messagebox.showinfo(
                        "Успех",
                        f"Архив создан: {os.path.basename(zip_path)}\n"
                        f"Изображений: {len(temp_files)}"
                    )
                    
                    self.status_bar.set_status(
                        f"Архив создан: {os.path.basename(zip_path)}",
                        f"Размер: {format_file_size(os.path.getsize(zip_path))}"
                    )
                else:
                    messagebox.showerror("Ошибка", "Не удалось создать архив")
                    
            finally:
                # Очищаем временные файлы
                for temp_file in temp_files:
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                        
        except Exception as e:
            logger.error(f"Ошибка создания архива: {e}")
            messagebox.showerror("Ошибка", f"Ошибка создания архива: {e}")
    
    def _display_current_image(self):
        """
        Отображение текущего изображения
        """
        if not self.current_images:
            return
        
        try:
            current_file = self.current_images[self.current_image_index]
            
            # Проверяем, есть ли обработанная версия
            if current_file in self.processed_images:
                image = self.processed_images[current_file]['processed']
            else:
                # Загружаем оригинальное изображение
                image = self.image_processor.load_image(current_file)
                if image is None:
                    self.image_viewer.show_error("Не удалось загрузить изображение")
                    return
            
            # Отображаем изображение
            self.image_viewer.display_image(image)
            
        except Exception as e:
            logger.error(f"Ошибка отображения изображения: {e}")
            self.image_viewer.show_error(f"Ошибка отображения: {e}")
    
    def _display_processed_image(self, image: Image.Image):
        """
        Отображение обработанного изображения
        
        Args:
            image: Обработанное изображение
        """
        try:
            self.image_viewer.display_image(image)
        except Exception as e:
            logger.error(f"Ошибка отображения обработанного изображения: {e}")
    
    def _prev_image(self):
        """
        Переход к предыдущему изображению
        """
        if self.current_images and self.current_image_index > 0:
            self.current_image_index -= 1
            self._display_current_image()
            self._update_image_info()
            self._update_navigation_state()
    
    def _next_image(self):
        """
        Переход к следующему изображению
        """
        if self.current_images and self.current_image_index < len(self.current_images) - 1:
            self.current_image_index += 1
            self._display_current_image()
            self._update_image_info()
            self._update_navigation_state()
    
    def _zoom_in(self):
        """
        Увеличение масштаба
        """
        # Эмулируем событие колеса мыши для увеличения
        event = type('Event', (), {'delta': 120, 'num': 4})()
        self.image_viewer._zoom(event)
    
    def _zoom_out(self):
        """
        Уменьшение масштаба
        """
        # Эмулируем событие колеса мыши для уменьшения
        event = type('Event', (), {'delta': -120, 'num': 5})()
        self.image_viewer._zoom(event)
    
    def _fit_to_window(self):
        """
        Подгонка изображения под размер окна
        """
        if self.image_viewer.current_image:
            self.image_viewer.zoom_factor = 1.0
            self.image_viewer.display_image(self.image_viewer.current_image)
    
    def _update_image_info(self):
        """
        Обновление информации о текущем изображении
        """
        try:
            self.info_text.config(state='normal')
            self.info_text.delete(1.0, tk.END)
            
            if self.current_images:
                current_file = self.current_images[self.current_image_index]
                info = self.image_processor.get_image_info(current_file)
                
                info_lines = [
                    f"Файл: {os.path.basename(current_file)}",
                    f"Размер файла: {format_file_size(info['file_size'])}",
                    f"Разрешение: {info['dimensions'][0]}x{info['dimensions'][1]}" if info['dimensions'] else "Разрешение: неизвестно",
                    f"Формат: {info['format'] or 'неизвестно'}",
                    f"Режим: {info['mode'] or 'неизвестно'}",
                    "",
                    f"Статус: {'Обработано' if current_file in self.processed_images else 'Оригинал'}",
                ]
                
                if current_file in self.processed_images:
                    settings = self.processed_images[current_file]['settings']
                    info_lines.extend([
                        "",
                        "Настройки логотипа:",
                        f"  Позиция: {settings.get('position', 'неизвестно')}",
                        f"  Размер: {int(settings.get('size', 0) * 100)}%",
                        f"  Прозрачность: {int(settings.get('opacity', 0) * 100)}%",
                        f"  Отступ: {settings.get('margin', 0)}px",
                    ])
                
                self.info_text.insert(tk.END, "\n".join(info_lines))
            
            self.info_text.config(state='disabled')
            
        except Exception as e:
            logger.error(f"Ошибка обновления информации об изображении: {e}")
    
    def _update_navigation_state(self):
        """
        Обновление состояния кнопок навигации
        """
        if self.current_images:
            # Обновляем счетчик
            current = self.current_image_index + 1
            total = len(self.current_images)
            self.image_counter.config(text=f"{current} / {total}")
            
            # Обновляем состояние кнопок
            self.prev_btn.config(state='normal' if self.current_image_index > 0 else 'disabled')
            self.next_btn.config(state='normal' if self.current_image_index < total - 1 else 'disabled')
        else:
            self.image_counter.config(text="0 / 0")
            self.prev_btn.config(state='disabled')
            self.next_btn.config(state='disabled')
    
    def _update_ui_state(self):
        """
        Обновление состояния элементов интерфейса
        """
        has_images = bool(self.current_images)
        has_logo = self.logo_loaded
        has_processed = bool(self.processed_images)
        is_processing = self.is_processing
        
        # Кнопки в toolbar
        self.load_images_btn.config(state='normal' if not is_processing else 'disabled')
        self.load_logo_btn.config(state='normal' if not is_processing else 'disabled')
        self.apply_logo_btn.config(
            state='normal' if (has_images and has_logo and not is_processing) else 'disabled'
        )
        self.batch_btn.config(
            state='normal' if (has_images and has_logo and not is_processing) else 'disabled'
        )
        self.save_btn.config(
            state='normal' if (has_processed and not is_processing) else 'disabled'
        )
        
        # Навигация
        self._update_navigation_state()
        
        # Кнопки управления просмотром
        has_current_image = has_images and self.image_viewer.current_image is not None
        self.zoom_in_btn.config(state='normal' if has_current_image else 'disabled')
        self.zoom_out_btn.config(state='normal' if has_current_image else 'disabled')
        self.fit_btn.config(state='normal' if has_current_image else 'disabled')
    
    def _on_settings_change(self, settings: Dict[str, Any]):
        """
        Обработчик изменения настроек
        
        Args:
            settings: Новые настройки
        """
        # Можно добавить автоматическое применение настроек
        # или предварительный просмотр
        pass
    
    def _on_closing(self):
        """
        Обработчик закрытия приложения
        """
        try:
            # Останавливаем обработку если идет
            if self.is_processing:
                if messagebox.askokcancel(
                    "Выход",
                    "Идет обработка изображений. Прервать и выйти?"
                ):
                    self.is_processing = False
                else:
                    return
            
            # Очищаем временные файлы
            cleanup_temp_directory()
            
            # Сохраняем настройки (если нужно)
            # self._save_settings()
            
            logger.info("Приложение закрыто")
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"Ошибка при закрытии приложения: {e}")
            self.root.destroy()
    
    def run(self):
        """
        Запуск приложения
        """
        try:
            logger.info("Запуск главного цикла приложения")
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Критическая ошибка в главном цикле: {e}")
            messagebox.showerror(
                "Критическая ошибка",
                f"Произошла критическая ошибка:\n{e}\n\nПриложение будет закрыто."
            )

def main():
    """
    Главная функция запуска приложения
    """
    try:
        # Создаем и запускаем приложение
        app = LogoMasterApp()
        app.run()
        
    except Exception as e:
        # Логируем критическую ошибку
        try:
            logger.error(f"Критическая ошибка запуска: {e}")
        except:
            pass
        
        # Показываем сообщение пользователю
        try:
            import tkinter.messagebox as mb
            mb.showerror(
                "Ошибка запуска",
                f"Не удалось запустить приложение:\n{e}\n\n"
                f"Проверьте установку Python и необходимых библиотек."
            )
        except:
            print(f"Критическая ошибка: {e}")
        
        sys.exit(1)

if __name__ == '__main__':
    main()