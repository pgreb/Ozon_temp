import sys
from cx_Freeze import setup, Executable

# Путь к вашему скрипту
script = "qt_test/qt_test.py"

# Имя выходного файла
output_exe = "OceanApp.exe"

# Конфигурация для cx_Freeze
build_exe_options = {
    "packages": ["os", "sqlite3", "pandas", "PyQt5.QtWidgets", "PyQt5.QtGui", "PyQt5.QtCore"],
    "includes": ["atexit"]
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Установка cx_Freeze
setup(
    name="OceanApp",
    version="1.0",
    description="Your Ocean App Description",
    options={"build_exe": build_exe_options},
    executables=[Executable(script, base=base, targetName=output_exe)]
)




