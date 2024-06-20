from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QFontDatabase, QFont
import os
import glob

for ttf_file in glob.glob("*.ttf"):
    print(f"File: {ttf_file}")
    try:
        fontId = QFontDatabase.addApplicationFont(os.path.abspath(ttf_file))
        fontName = QFontDatabase.applicationFontFamilies(fontId)[0] if fontId != -1 else None

        if fontName:
            print(fontName)
        print("---")
    except Exception as e:
        print(f"Error {ttf_file}")
        continue