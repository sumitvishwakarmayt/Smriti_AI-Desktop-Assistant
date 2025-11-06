from PyQt5.QtWidgets import QApplication
from ui.main_window import SmritiWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    smriti = SmritiWindow()
    smriti.show()
    sys.exit(app.exec_())
