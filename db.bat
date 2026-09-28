@echo off
setlocal
rem ============================================================
rem  Build inputshow with PyInstaller.
rem
rem    db.bat            onedir : dist\inputshow_portable\   (recommended)
rem    db.bat onefile    onefile: dist\inputshow.exe
rem    db.bat both       both
rem
rem  WHY ONEDIR IS THE DEFAULT
rem    A onefile exe is a self-extracting archive: every launch unpacks the
rem    whole thing into a temporary folder first. If that step fails you get
rem    "Could not create temporary directory!" and the program never starts -
rem    typically because security software blocks it, the temp folder is in a
rem    bad state, or the system drive is full.
rem    The onedir build has no such step: it runs straight from its folder.
rem
rem  HOW TO SHIP IT
rem    Zip dist\inputshow_portable\ and send the zip. The user extracts it and
rem    runs inputshow_portable.exe inside. Keep the _internal folder next to
rem    the exe - it is part of the program.
rem ============================================================

cd /d "%~dp0"

set MODE=%~1
if "%MODE%"=="" set MODE=onedir

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
set OPTS=--noconfirm --windowed
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

rem UPX shrinks the Qt DLLs a lot. It cannot pack python3*.dll and prints a
rem "NotCompressibleException" warning, but PyInstaller skips that file and the
rem build stays valid (verified). Set UPX_NO=1 to disable compression.
if "%UPX_NO%"=="1" (
  set OPTS=%OPTS% --noupx
) else (
  if exist "%UPXDIR%" set OPTS=%OPTS% --upx-dir "%UPXDIR%"
)

rem ---- mode dispatch ----
if /i "%MODE%"=="onedir"  goto onedir
if /i "%MODE%"=="onefile" goto onefile
if /i "%MODE%"=="both"    goto both

echo [ERROR] Unknown mode "%MODE%". Use: onedir ^| onefile ^| both
exit /b 1

:onedir
echo.
echo === ONEDIR -^> dist\inputshow_portable\  (recommended, no temp extraction) ===
if exist build\inputshow_portable rmdir /s /q build\inputshow_portable
%PY% -m PyInstaller %OPTS% --clean --onedir --name inputshow_portable main.py
if errorlevel 1 goto fail
echo Built: dist\inputshow_portable\inputshow_portable.exe
if /i "%MODE%"=="onedir" goto done

:onefile
echo.
echo === ONEFILE -^> dist\inputshow.exe  (unpacks to a temp folder on every run) ===
if exist build\inputshow rmdir /s /q build\inputshow
%PY% -m PyInstaller %OPTS% --clean --onefile --name inputshow main.py
if errorlevel 1 goto fail
echo Built: dist\inputshow.exe
goto done

:both
echo.
echo === ONEDIR ===
if exist build\inputshow_portable rmdir /s /q build\inputshow_portable
%PY% -m PyInstaller %OPTS% --clean --onedir --name inputshow_portable main.py
if errorlevel 1 goto fail
echo.
echo === ONEFILE ===
if exist build\inputshow rmdir /s /q build\inputshow
%PY% -m PyInstaller %OPTS% --clean --onefile --name inputshow main.py
if errorlevel 1 goto fail
goto done

:fail
echo.
echo [ERROR] PyInstaller failed. Is it installed?  %PY% -m pip install pyinstaller
exit /b 1

:done
echo.
echo All done. Output in dist\
if exist dist\inputshow_portable\inputshow_portable.exe echo   ONEDIR : dist\inputshow_portable\inputshow_portable.exe   ^<- zip this folder to share
if exist dist\inputshow.exe echo   ONEFILE: dist\inputshow.exe
exit /b 0
