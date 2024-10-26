@echo off
set /p VERSION="Version to Build: "
pyinstaller --onefile src/main.py --windowed --hidden-import plyer.platforms.win.notification --distpath build --workpath build --specpath build --name=KeyboardSounds-v%VERSION% --icon=../src/icon.ico
echo.
pause
