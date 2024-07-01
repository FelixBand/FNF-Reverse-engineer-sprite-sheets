rd /s /q build
rd /s /q dist
pyinstaller --windowed --onefile --icon=icon.ico -n "Reverse Engineer Spritesheets" "Reverse Engineer Spritesheets.py"
pause