import sys
import traceback
from PySide6.QtWidgets import QApplication
from ui.main_window import SmritiWindow


if __name__ == "__main__":
    try:
        print("🚀 Launching Smriti System...")
        print("🔧 Initializing components...")
        
        # Create application
        app = QApplication(sys.argv)
        print("✅ PySide6 app created")
        
        # Create main window
        smriti = SmritiWindow()
        print("✅ Main window created")
        
        # Show window and ensure it's focused
        smriti.show()
        smriti.raise_()  # Bring window to front
        smriti.activateWindow()  # Activate and focus window
        smriti.setFocus()  # Set keyboard focus
        print("💜 Smriti Interface Launched Successfully.")
        print("🎯 Ready for voice commands...")
        
        # Run application
        exit_code = app.exec()
        print("👋 Smriti application closed")
        sys.exit(exit_code)
        
    except Exception as e:
        print("❌ Error while launching Smriti:")
        traceback.print_exc()