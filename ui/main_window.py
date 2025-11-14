from PyQt5.QtCore import Qt, QTimer, QPoint, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from ui.circular_indicator import CircularIndicator

# Fixed imports - use core. prefix since files are in core folder
from core.voice_response import speak, set_caption_callback, stop as stop_speaking, is_speaking
from core.voice_recognition import listen_command
from core.brain import process_command
import time


class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setStyleSheet("""
            background-color: #3E007A;
            color: white;
            font-weight: bold;
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
        """)
        self.title = QLabel("💜 Smriti — AI Desktop Assistant", self)
        self.title.setStyleSheet("background: transparent; color: white; font-size: 16px; font-weight: 700;")
        self.minBtn = QPushButton("–", self)
        self.closeBtn = QPushButton("✕", self)
        
        for btn in (self.minBtn, self.closeBtn):
            btn.setFixedSize(28, 28)
            btn.setStyleSheet("""
                QPushButton {
                    color: white;
                    background: rgba(255,255,255,0.15);
                    border: none;
                    border-radius: 14px;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.3);
                }
            """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.addWidget(self.title)
        layout.addStretch()
        layout.addWidget(self.minBtn)
        layout.addWidget(self.closeBtn)
        
        if parent:
            self.minBtn.clicked.connect(parent.showMinimized)
            self.closeBtn.clicked.connect(parent.close)
        self.oldPos = None

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.oldPos = e.globalPos()

    def mouseMoveEvent(self, e):
        if self.oldPos:
            delta = e.globalPos() - self.oldPos
            self.parent().move(self.parent().x() + delta.x(), self.parent().y() + delta.y())
            self.oldPos = e.globalPos()

    def mouseReleaseEvent(self, e):
        self.oldPos = None


class SmritiListener(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_running = True

    def run(self):
        while self._is_running:
            try:
                # If TTS is currently speaking, listen briefly for ANY user speech; if heard, stop and process it immediately
                command = None
                if is_speaking():
                    print("🔇 Smriti is speaking... listening for your voice to interrupt")
                    try:
                        interrupt = listen_command(timeout=1, phrase_time_limit=3)
                        if interrupt and interrupt.strip():
                            print(f"🛑 User spoke during TTS: {interrupt}")
                            stop_speaking()
                            command = interrupt
                        else:
                            time.sleep(0.2)
                            continue
                    except Exception:
                        time.sleep(0.2)
                        continue
                    
                if command is None:
                    print("🎤 Listening for command... (quick mode)")
                    command = listen_command(timeout=4, phrase_time_limit=4)
                
                if command and command.strip():
                    print(f"🎯 Command received: {command}")
                    
                    # Check if user wants to stop current speech
                    stop_keywords = ["stop", "ruko", "chup", "mute", "bas", "shut up", "wait", "wait stop"]
                    if any(k in command.lower() for k in stop_keywords):
                        print("🛑 User requested to stop speaking")
                        stop_speaking()
                        if hasattr(self.parent(), "captionSignal"):
                            self.parent().captionSignal.emit("Okay, I stopped speaking.")
                        # Don't continue, wait for next command
                        time.sleep(1)
                        continue

                    # Immediate SHUTDOWN handling
                    shutdown_keywords = [
                        "shutdown", "shut down", "exit", "close", "band hojao", 
                        "band ho jao", "band ho", "band karo", "goodbye", "bye"
                    ]
                    if any(k in command.lower() for k in shutdown_keywords):
                        print("🔌 User requested shutdown")
                        stop_speaking()
                        QTimer.singleShot(0, self.parent().close)
                        continue

                    # Process command and SPEAK the response
                    try:
                        print("🧠 Processing command with brain...")
                        
                        # Show "Thinking..." message
                        if hasattr(self.parent(), "captionSignal"):
                            self.parent().captionSignal.emit("💭 Thinking...")
                        
                        response = process_command(command, speak_out=False)
                        
                        if response and response.strip():
                            print(f"💬 Response from Gemini: {response}")
                            
                            # Update UI caption
                            if hasattr(self.parent(), "captionSignal"):
                                self.parent().captionSignal.emit(response)
                            
                            # SPEAK THE RESPONSE
                            print(f"🔊 Speaking response...")
                            speak(response)
                            
                        else:
                            fallback = "I'm here, Sumit. How can I help you?"
                            if hasattr(self.parent(), "captionSignal"):
                                self.parent().captionSignal.emit(fallback)
                            print("🔊 Speaking fallback response")
                            speak(fallback)
                            
                    except Exception as e:
                        print(f"❌ Error processing command: {e}")
                        error_msg = "Sorry, I encountered an error. Please try again."
                        if hasattr(self.parent(), "captionSignal"):
                            self.parent().captionSignal.emit(error_msg)
                        speak(error_msg)
                
                else:
                    # No command detected, continue listening
                    print("🔁 No command detected, continuing to listen...")
                    time.sleep(0.5)
                            
            except Exception as e:
                print(f"❌ Error in listener thread: {e}")
                time.sleep(2)

    def stop(self):
        """Properly stop the thread"""
        self._is_running = False
        self.wait(1000)


class SmritiWindow(QWidget):
    captionSignal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 16)
        layout.setSpacing(8)

        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)

        self.indicator = CircularIndicator(self)
        layout.addWidget(self.indicator, alignment=Qt.AlignCenter)

        self.caption_label = QLabel("", self)
        self.caption_label.setAlignment(Qt.AlignCenter)
        self.caption_label.setStyleSheet("""
            color: white;
            background: rgba(60, 0, 100, 130);
            border-radius: 10px;
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
            font-weight: bold;
            padding: 8px 20px;
            margin-top: 10px;
        """)
        self.caption_label.setWordWrap(True)
        layout.addWidget(self.caption_label, alignment=Qt.AlignCenter)

        self.setFixedSize(440, 460)

        # Live caption hookup
        self.captionSignal.connect(self.on_caption)
        set_caption_callback(lambda text: self.captionSignal.emit(text))

        greeting = "✨ Smriti System Activated — Hello Sumit 💜"
        self.start_typing_animation(greeting)
        
        # Test speech after a short delay to ensure everything is loaded
        QTimer.singleShot(2000, lambda: self.test_speech())

        self.listener = SmritiListener(self)
        self.listener.start()

    def test_speech(self):
        """Test if TTS is working"""
        try:
            print("🔊 Testing TTS system with welcome message...")
            welcome_text = "Hello Sumit! Smriti system is now activated!"
            speak(welcome_text)
            print("✅ Test speech triggered")
        except Exception as e:
            print(f"❌ TTS test failed: {e}")

    def start_typing_animation(self, text):
        self.full_text = text
        self.caption_label.setText("")
        self.current_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_text)
        self.typing_interval = 28
        self.timer.start(self.typing_interval)

    def update_text(self):
        if self.current_index < len(self.full_text):
            ch = self.full_text[self.current_index]
            self.caption_label.setText(self.caption_label.text() + ch)
            self.current_index += 1
            if ch in ".!?":
                self.timer.setInterval(120)
            elif ch in ",;":
                self.timer.setInterval(80)
            else:
                self.timer.setInterval(self.typing_interval)
        else:
            self.timer.stop()

    def on_caption(self, text: str):
        self.start_typing_animation(text)

    def resizeEvent(self, event):
        inner_width = max(200, self.width() - 32)
        self.caption_label.setMaximumWidth(inner_width)
        return super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(25, 0, 60, 180))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)

    def closeEvent(self, event):
        """Properly clean up threads when closing the window"""
        if hasattr(self, 'listener'):
            self.listener.stop()
        super().closeEvent(event)