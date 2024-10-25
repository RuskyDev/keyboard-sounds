set version=1.0

pyinstaller --onefile src/main.py --windowed --hidden-import plyer.platforms.win.notification --name=KeyboardSounds-v%VERSION% --icon=src/icon.ico

@pause>nul