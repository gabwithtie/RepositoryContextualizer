@echo off
title Building Code-RAG Executable
cls

:: ======================================================
:: CONFIGURATION (Adjust these if your folder names differ)
:: ======================================================
:: Relative path to your virtual environment folder inside the project
set "VENV_DIR=repocontextualizer"

:: Entry point python file
set "ENTRY_POINT=RepositoryContextualizer.py"

:: Splash screen image
set "SPLASH_IMG=splash.png"

:: Desired executable name (will output as CodeRAG_Packer.exe in /dist)
set "EXE_NAME=RepositoryContextualizer"


echo ======================================================
echo Step 1: Activating Virtual Environment
echo ======================================================

:: Check if the virtual environment exists in the subfolder
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at: "%VENV_DIR%\Scripts\activate.bat"
    echo Please update the VENV_DIR variable in this batch script to match your subfolder name.
    echo.
    pause
    exit /b 1
)

:: Activate the environment
call "%VENV_DIR%\Scripts\activate.bat"
echo [SUCCESS] Environment activated successfully!
echo.


echo ======================================================
echo Step 2: Checking Assets & Prerequisites
echo ======================================================

:: Check for PyInstaller inside the activated environment
where pyinstaller >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PyInstaller is not installed in this virtual environment!
    echo Installing PyInstaller now...
    pip install pyinstaller
)

:: Check if the main python script exists
if not exist "%ENTRY_POINT%" (
    echo [ERROR] Entry point file "%ENTRY_POINT%" was not found in the root directory!
    pause
    exit /b 1
)

:: Check for splash image (Optional flag setup)
set "SPLASH_FLAG="
if exist "%SPLASH_IMG%" (
    echo [INFO] Found splash image: %SPLASH_IMG%
    set "SPLASH_FLAG=--splash %SPLASH_IMG%"
) else (
    echo [WARNING] Splash image "%SPLASH_IMG%" not found. Building without splash screen...
)
echo.


echo ======================================================
echo Step 3: Running PyInstaller Build
echo ======================================================
echo Packaging heavy ML dependencies (ChromaDB ^& Sentence Transformers)...
echo This process can take 1-3 minutes. Please wait.
echo.

pyinstaller --noconsole ^
    --onefile ^
    --name "%EXE_NAME%" ^
    %SPLASH_FLAG% ^
    --collect-all chromadb ^
    --collect-all sentence_transformers ^
    "%ENTRY_POINT%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] PyInstaller build failed with exit code %ERRORLEVEL%.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ======================================================
echo [SUCCESS] Executable built successfully!
echo Output Location: %CD%\dist\%EXE_NAME%.exe
echo ======================================================
echo.

pause