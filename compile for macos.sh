rm -rf build
rm -rf dist
pyinstaller --onefile --windowed --icon=icon.png -n "Reverse Engineer Spritesheets" "Reverse Engineer Spritesheets.py"