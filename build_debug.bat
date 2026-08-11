@echo off
title Building Debug Executable
call repocontextualizer\Scripts\activate.bat

:: Build WITHOUT --noconsole and WITHOUT --splash so the terminal stays visible
pyinstaller --onefile ^
    --name "CodeRAG_DEBUG" ^
    --collect-all chromadb ^
    --collect-all sentence_transformers ^
    RepositoryContextualizer.py

echo.
echo ======================================================
echo DEBUG BUILD COMPLETE. 
echo Do NOT double click the EXE. Run it from CMD below!
echo ======================================================
pause