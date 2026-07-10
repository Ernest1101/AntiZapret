@echo off
title AntiZapret - General Strategy
echo ==========================================
echo  AntiZapret - General Strategy
echo ==========================================
echo.

REM Проверка прав администратора
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ОШИБКА] Запустите скрипт от имени администратора!
    pause
    exit /b 1
)

echo [INFO] Запуск стратегии обхода...
echo.

REM Переход в директорию скрипта
cd /d "%~dp0"

REM Проверка наличия бинарных файлов
if not exist "bin\winws.exe" (
    echo [ОШИБКА] Файл bin\winws.exe не найден!
    echo Скачайте бинарные файлы zapret и поместите в папку bin\
    pause
    exit /b 1
)

if not exist "bin\WinDivert64.sys" (
    echo [ОШИБКА] Файл bin\WinDivert64.sys не найден!
    pause
    exit /b 1
)

echo [INFO] Запуск winws.exe...
echo.

REM Запуск winws с базовой стратегией
start "" /B "bin\winws.exe" --filter-tcp --filter-udp --dpi-desync=split2 --dpi-desync-split-pos=1 --dpi-desync-fake-tls=bin\tls_clienthello.bin --dpi-desync-ttl=0 --hostlist=lists\list-general.txt --hostlist-auto=lists\list-general-user.txt --ipset=lists\ipset-all.txt --nfqws

echo.
echo [INFO] Стратегия запущена!
echo [INFO] Для остановки закройте это окно или используйте taskkill /F /IM winws.exe
echo.
echo Нажмите любую клавишу для остановки...
pause >nul

echo.
echo [INFO] Остановка стратегии...
taskkill /F /IM winws.exe >nul 2>&1
echo [INFO] Стратегия остановлена.
pause
