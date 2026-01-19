@echo off
echo ========================================
echo   Pokemon Todo List - Build EXE
echo ========================================
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install PyInstaller if not already installed
echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building executable...
echo.

REM Build the executable with all resources
pyinstaller --onefile ^
    --windowed ^
    --name="PokemonTodo" ^
    --icon=sprites/pokeball.png ^
    --add-data="PressStart2P-Regular.ttf;." ^
    --add-data="sprites;sprites" ^
    --noconsole ^
    main.py

echo.
echo ========================================
echo   Build Complete!
echo ========================================
echo.
echo Your .exe file is in the 'dist' folder
echo You can move PokemonTodo.exe anywhere!
echo.
echo IMPORTANT: MongoDB must be running
echo            on your computer to use the app
echo.
pause
