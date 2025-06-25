# 🚀 Инструкция по установке LogoMaster Pro

## Быстрый запуск (Windows)

### Вариант 1: Автоматическая установка
1. **Скачайте все файлы** проекта в одну папку
2. **Запустите** `run_app.bat` (двойной клик)
3. **Следуйте инструкциям** на экране

### Вариант 2: Ручная установка

#### Шаг 1: Установка Python
1. Перейдите на https://python.org/downloads/
2. Скачайте Python 3.8 или выше
3. **ВАЖНО**: При установке отметьте "Add Python to PATH"
4. Проверьте установку:
   ```cmd
   python --version
   ```

#### Шаг 2: Установка зависимостей
```cmd
pip install -r requirements.txt
```

Или установите вручную:
```cmd
pip install Pillow numpy requests
```

#### Шаг 3: Проверка компонентов
```cmd
python check_components.py
```

#### Шаг 4: Запуск приложения
```cmd
python main.py
```

## Установка на Linux/macOS

### Ubuntu/Debian
```bash
# Установка Python и pip
sudo apt update
sudo apt install python3 python3-pip python3-tk

# Установка зависимостей
pip3 install -r requirements.txt

# Запуск
python3 main.py
```

### macOS
```bash
# Установка через Homebrew
brew install python-tk

# Установка зависимостей
pip3 install -r requirements.txt

# Запуск
python3 main.py
```

## Устранение проблем

### Python не найден
- Переустановите Python с официального сайта
- Убедитесь, что отметили "Add to PATH"
- Перезагрузите компьютер

### Ошибки импорта
```cmd
# Обновите pip
pip install --upgrade pip

# Переустановите зависимости
pip install --force-reinstall -r requirements.txt
```

### Проблемы с tkinter (Linux)
```bash
sudo apt install python3-tk
```

### Приложение не запускается
1. Запустите проверку: `python check_components.py`
2. Проверьте логи в папке приложения
3. Попробуйте запустить в безопасном режиме:
   ```cmd
   python main.py --safe-mode
   ```

## Системные требования

- **Python**: 3.8+
- **ОС**: Windows 10+, Ubuntu 18.04+, macOS 10.14+
- **ОЗУ**: 4 ГБ (рекомендуется 8 ГБ)
- **Место**: 100 МБ свободного места

## Структура файлов

Убедитесь, что у вас есть все файлы:
```
📁 logomaster-pro/
├── 📄 main.py                 # Главное приложение
├── 📄 config.py              # Конфигурация
├── 📄 image_processor.py     # Обработка изображений
├── 📄 ui_components.py       # UI компоненты
├── 📄 utils.py               # Утилиты
├── 📄 requirements.txt       # Зависимости
├── 📄 check_components.py    # Проверка системы
├── 📄 run_app.bat           # Запуск (Windows)
├── 📄 README.md             # Документация
└── 📄 INSTALL.md            # Эта инструкция
```

## Первый запуск

1. **Загрузите изображения**: Кнопка "📁 Загрузить" или перетащите файлы
2. **Загрузите логотип**: Кнопка "🏷️ Логотип" (рекомендуется PNG)
3. **Настройте параметры**: Позиция, размер, прозрачность
4. **Примените логотип**: Кнопка "✨ Применить"
5. **Сохраните результат**: Меню "💾 Сохранить"

## Получение помощи

- 📖 Полная документация: `README.md`
- 🔧 Техническое задание: `TECHNICAL_SPECIFICATION.md`
- 🐛 Проблемы: Запустите `python check_components.py`

---

**Удачного использования LogoMaster Pro! 🎨**