import sys
import traceback
from PyQt5.QtWidgets import QApplication
from ui.main_window import SmritiWindow


if __name__ == "__main__":
    try:
        print("🚀 Launching Smriti System...")
        app = QApplication(sys.argv)
        smriti = SmritiWindow()
        smriti.show()
        print("💜 Smriti Interface Launched Successfully.")
        sys.exit(app.exec_())
    except Exception as e:
        print("❌ Error while launching Smriti:")
        traceback.print_exc()
