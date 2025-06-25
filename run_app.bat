@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo    LOGOMASTER PRO - ЗАПУСК ПРИЛОЖЕНИЯ
echo ========================================
echo.

REM Проверка наличия Python
echo [1/5] Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo.
    echo Пожалуйста, установите Python 3.8+ с https://python.org
    echo При установке обязательно отметьте "Add Python to PATH"
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% найден
echo.

REM Проверка pip
echo [2/5] Проверка pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip не найден!
    echo Попробуйте переустановить Python
    pause
    exit /b 1
)
echo ✅ pip доступен
echo.

REM Установка зависимостей
echo [3/5] Установка зависимостей...
if exist requirements.txt (
    echo Установка пакетов из requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Ошибка установки зависимостей!
        echo Попробуйте запустить: pip install --upgrade pip
        pause
        exit /b 1
    )
    echo ✅ Зависимости установлены
) else (
    echo ⚠️  requirements.txt не найден, устанавливаем основные пакеты...
    pip install Pillow numpy requests
)
echo.

REM Проверка компонентов
echo [4/5] Проверка компонентов...
if exist check_components.py (
    python check_components.py
    if errorlevel 1 (
        echo.
        echo ❌ Обнаружены проблемы с компонентами!
        echo Проверьте вывод выше для диагностики
        pause
        exit /b 1
    )
) else (
    echo ⚠️  Файл проверки не найден, пропускаем...
)
echo.

REM Запуск приложения
echo [5/5] Запуск LogoMaster Pro...
echo.
if exist main.py (
    echo 🚀 Запускаем приложение...
    echo Если окно не появилось, проверьте консоль на наличие ошибок
    echo.
    python main.py
    if errorlevel 1 (
        echo.
        echo ❌ Приложение завершилось с ошибкой!
        echo Код ошибки: %errorlevel%
    ) else (
        echo.
        echo ✅ Приложение завершено успешно
    )
) else (
    echo ❌ main.py не найден!
    echo Убедитесь, что все файлы проекта находятся в текущей папке
)

echo.
echo Нажмите любую клавишу для выхода...
pause >nul