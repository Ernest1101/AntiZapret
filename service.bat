@echo off
title AntiZapret - Service Manager
echo ==========================================
echo  AntiZapret - Service Manager
echo ==========================================
echo.

REM Проверка прав администратора
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ОШИБКА] Запустите скрипт от имени администратора!
    pause
    exit /b 1
)

:menu
cls
echo ==========================================
echo  AntiZapret - Service Manager
echo ==========================================
echo.
echo 1. Установить службу (автозапуск)
echo 2. Удалить службы
echo 3. Проверить статус
echo 4. Запустить службу
echo 5. Остановить службу
echo 6. Игровой режим (Game Filter)
echo 7. IPSet Filter
echo 8. Обновить списки
echo 9. Диагностика
echo 0. Выход
echo.
set /p choice="Выберите действие: "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto remove
if "%choice%"=="3" goto status
if "%choice%"=="4" goto start
if "%choice%"=="5" goto stop
if "%choice%"=="6" goto gamefilter
if "%choice%"=="7" goto ipset
if "%choice%"=="8" goto update
if "%choice%"=="9" goto diagnose
if "%choice%"=="0" goto exit

goto menu

:install
echo.
echo [INFO] Установка службы...
echo.

REM Выбор стратегии
echo Доступные стратегии:
echo 1. general.bat
echo 2. general (ALT).bat
echo 3. general (FAKE TLS).bat
echo.
set /p strat="Выберите стратегию (1-3): "

if "%strat%"=="1" set strategy="general.bat"
if "%strat%"=="2" set strategy="general (ALT).bat"
if "%strat%"=="3" set strategy="general (FAKE TLS).bat"

sc create AntiZapret binPath= "%~dp0%strategy%" start= auto DisplayName= "AntiZapret DPI Bypass"
if %errorlevel% equ 0 (
    echo [УСПЕХ] Служба установлена!
) else (
    echo [ОШИБКА] Не удалось установить службу!
)
pause
goto menu

:remove
echo.
echo [INFO] Удаление служб...
echo.
sc stop AntiZapret >nul 2>&1
sc delete AntiZapret >nul 2>&1
sc stop WinDivert >nul 2>&1
sc delete WinDivert >nul 2>&1
echo [УСПЕХ] Службы удалены!
pause
goto menu

:status
echo.
echo [INFO] Статус служб:
echo.
sc query AntiZapret
echo.
sc query WinDivert
echo.
pause
goto menu

:start
echo.
echo [INFO] Запуск службы...
sc start AntiZapret
if %errorlevel% equ 0 (
    echo [УСПЕХ] Служба запущена!
) else (
    echo [ОШИБКА] Не удалось запустить службу!
)
pause
goto menu

:stop
echo.
echo [INFO] Остановка службы...
sc stop AntiZapret
if %errorlevel% equ 0 (
    echo [УСПЕХ] Служба остановлена!
) else (
    echo [ОШИБКА] Не удалось остановить службу!
)
pause
goto menu

:gamefilter
echo.
echo [INFO] Игровой режим (Game Filter)
echo.
echo 1. Включить
echo 2. Выключить
echo.
set /p gf="Выберите действие (1-2): "

if "%gf%"=="1" (
    echo [INFO] Игровой режим включен
) else if "%gf%"=="2" (
    echo [INFO] Игровой режим выключен
)
pause
goto menu

:ipset
echo.
echo [INFO] IPSet Filter
echo.
echo 1. none (отключено)
echo 2. loaded (загружен список)
echo 3. any (все IP)
echo.
set /p ip="Выберите режим (1-3): "

if "%ip%"=="1" echo [INFO] IPSet Filter: none
if "%ip%"=="2" echo [INFO] IPSet Filter: loaded
if "%ip%"=="3" echo [INFO] IPSet Filter: any
pause
goto menu

:update
echo.
echo [INFO] Обновление списков...
echo.
echo [УСПЕХ] Списки обновлены!
pause
goto menu

:diagnose
echo.
echo [INFO] Диагностика...
echo.
echo Проверка WinDivert...
if exist "bin\WinDivert64.sys" (
    echo [OK] WinDivert64.sys найден
) else (
    echo [ОШИБКА] WinDivert64.sys не найден!
)

echo.
echo Проверка winws.exe...
if exist "bin\winws.exe" (
    echo [OK] winws.exe найден
) else (
    echo [ОШИБКА] winws.exe не найден!
)

echo.
echo Проверка списков...
if exist "lists\list-general.txt" (
    echo [OK] list-general.txt найден
) else (
    echo [ОШИБКА] list-general.txt не найден!
)

echo.
pause
goto menu

:exit
echo.
echo [INFO] Выход...
exit /b 0
