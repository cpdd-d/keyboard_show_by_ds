@echo off
setlocal
rem ============================================================
rem  Build inputshow with PyInstaller.
rem
rem    db.bat            onefile  : single inputshow.exe (extracts to %%TEMP%% on start)
rem    db.bat onedir     onedir   : dist\inputshow\inputshow.exe + DLLs, no extraction
rem    db.bat onefile    onefile  : same as no argument
rem    db.bat both       both     : build both
rem
rem  Why onedir: the onefile bootloader unpacks the whole archive into a
rem  temporary folder on every launch. That step can be blocked by security
rem  software (observed: "Could not create temporary directory"), and it makes
rem  startup slower. onedir runs straight from the folder, so it is the safer
rem  choice for distribution.
rem ============================================================

cd /d "%~dp0"

set MODE=%~1
if "%MODE%"=="" set MODE=onefile

set NAME=inputshow
set ICON=ips.ico
set UPXDIR=C:\upx

rem ---- locate python ----
set PY=
where py >nul 2>nul && set PY=py -3
if not defined PY (
  where python >nul 2>nul && set PY=python
)
if not defined PY (
  echo [ERROR] Python not found. Install Python 3 and retry.
  exit /b 1
)

rem ---- common PyInstaller options ----
set OPTS=--noconfirm --clean --name %NAME%
set OPTS=%OPTS% --hidden-import=pynput.keyboard._win32
set OPTS=%OPTS% --hidden-import=pynput.mouse._win32
set OPTS=%OPTS% --hidden-import=PyQt5.QtNetwork
set OPTS=%OPTS% --exclude-module PyQt5.QtWebEngineWidgets
set OPTS=%OPTS% --exclude-module PyQt5.QtWebEngineCore
set OPTS=%OPTS% --exclude-module PyQt5.QtQuick
set OPTS=%OPTS% --exclude-module PyQt5.QtQml
set OPTS=%OPTS% --exclude-module PyQt5.QtMultimedia
set OPTS=%OPTS% --exclude-module PyQt5.QtMultimediaWidgets
set OPTS=%OPTS% --exclude-module PyQt5.QtBluetooth
set OPTS=%OPTS% --exclude-module PyQt5.QtDesigner
set OPTS=%OPTS% --exclude-module PyQt5.QtHelp
set OPTS=%OPTS% --exclude-module PyQt5.QtLocation
set OPTS=%OPTS% --exclude-module PyQt5.QtNfc
set OPTS=%OPTS% --exclude-module PyQt5.QtPositioning
set OPTS=%OPTS% --exclude-module PyQt5.QtSerialPort
set OPTS=%OPTS% --exclude-module PyQt5.QtSql
set OPTS=%OPTS% --exclude-module PyQt5.QtTest
set OPTS=%OPTS% --exclude-module PyQt5.QtWebChannel
set OPTS=%OPTS% --exclude-module PyQt5.QtWebSockets
set OPTS=%OPTS% --exclude-module PyQt5.QtXml
set OPTS=%OPTS% --exclude-module PyQt5.QtXmlPatterns
set OPTS=%OPTS% --exclude-module matplotlib
set OPTS=%OPTS% --exclude-module numpy
set OPTS=%OPTS% --exclude-module scipy
set OPTS=%OPTS% --exclude-module PIL
set OPTS=%OPTS% --exclude-module tkinter
set OPTS=%OPTS% --exclude-module unittest
set OPTS=%OPTS% --exclude-module pydoc

if exist "%ICON%" set OPTS=%OPTS% -i "%ICON%"
if exist "%UPXDIR%" (
  set OPTS=%OPTS% --upx-dir "%UPXDIR%"
) else (
  set OPTS=%OPTS% --noupx
)

rem ---- run ----
if /i "%MODE%"=="onedir"  goto onedir
if /i "%MODE%"=="onefile" goto onefile
if /i "%MODE%"=="both"    goto both

echo [ERROR] Unknown mode "%MODE%". Use: onedir ^| onefile ^| both
exit /b 1

:onedir
echo.
echo === Building ONEDIR (dist\%NAME%\%NAME%.exe - no temp extraction) ===
%PY% -m PyInstaller %OPTS% --onedir --windowed main.py
if errorlevel 1 goto fail
echo Built: dist\%NAME%\%NAME%.exe
if /i "%MODE%"=="onedir" goto done

:onefile
echo.
echo === Building ONEFILE (dist\%NAME%.exe - extracts to %%TEMP%%) ===
%PY% -m PyInstaller %OPTS% --onefile --windowed main.py
if errorlevel 1 goto fail
echo Built: dist\%NAME%.exe
goto done

:both
echo.
echo === Building ONEDIR ===
%PY% -m PyInstaller %OPTS% --onedir --windowed main.py
if errorlevel 1 goto fail
echo Built: dist\%NAME%\%NAME%.exe
echo.
echo === Building ONEFILE ===
%PY% -m PyInstaller %OPTS% --onefile --windowed main.py
if errorlevel 1 goto fail
echo Built: dist\%NAME%.exe
goto done

:fail
echo.
echo [ERROR] PyInstaller failed. Is it installed?  %PY% -m pip install pyinstaller
exit /b 1

:done
echo.
echo All done.
exit /b 0
