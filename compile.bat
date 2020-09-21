
pyinstaller --onefile --distpath ./bin dmr-kr-monitor-by-vk2cyo.py

rmdir build /S /Q
rmdir __pycache__ /S /Q
del /F /Q dmr-kr-monitor-by-vk2cyo.spec
