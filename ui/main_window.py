from PySide6.QtCore import Qt, QTimer, QPoint, QThread, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit
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
        self.pinBtn = QPushButton("📌", self)
        self.minBtn = QPushButton("–", self)
        self.closeBtn = QPushButton("✕", self)
        
        # Pin button styling
        self.pinBtn.setFixedSize(28, 28)
        self.pinBtn.setStyleSheet("""
            QPushButton {
                color: white;
                background: rgba(255,255,255,0.15);
                border: none;
                border-radius: 14px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.3);
            }
            QPushButton:pressed {
                background: rgba(255,255,255,0.4);
            }
        """)
        
        # Minimize and close buttons styling
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
        layout.addWidget(self.pinBtn)
        layout.addWidget(self.minBtn)
        layout.addWidget(self.closeBtn)
        
        if parent:
            self.pinBtn.clicked.connect(self.toggle_pin)
            self.minBtn.clicked.connect(parent.showMinimized)
            self.closeBtn.clicked.connect(parent.close)
        self.oldPos = None
        self.is_pinned = True  # Start pinned since window starts with WindowStaysOnTopHint
        # Update button style to show pinned state
        self.pinBtn.setStyleSheet("""
            QPushButton {
                color: white;
                background: rgba(255, 200, 0, 0.4);
                border: 2px solid rgba(255, 200, 0, 0.8);
                border-radius: 14px;
            }
            QPushButton:hover {
                background: rgba(255, 200, 0, 0.5);
            }
        """)
    
    def toggle_pin(self):
        """Toggle window always-on-top state"""
        if self.parent():
            self.is_pinned = not self.is_pinned
            if self.is_pinned:
                self.parent().setWindowFlags(self.parent().windowFlags() | Qt.WindowStaysOnTopHint)
                self.pinBtn.setStyleSheet("""
                    QPushButton {
                        color: white;
                        background: rgba(255, 200, 0, 0.4);
                        border: 2px solid rgba(255, 200, 0, 0.8);
                        border-radius: 14px;
                    }
                    QPushButton:hover {
                        background: rgba(255, 200, 0, 0.5);
                    }
                """)
            else:
                self.parent().setWindowFlags(self.parent().windowFlags() & ~Qt.WindowStaysOnTopHint)
                self.pinBtn.setStyleSheet("""
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
            self.parent().show()  # Re-show window to apply flags
            self.parent().raise_()  # Bring to front
            self.parent().activateWindow()  # Focus window

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
        self._mic_active = False  # Mic is off by default

    def run(self):
        while self._is_running:
            try:
                # Only listen if mic is active
                if not self._mic_active:
                    time.sleep(0.5)
                    continue
                
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

    def set_mic_active(self, active: bool):
        """Enable or disable microphone listening"""
        self._mic_active = active
        print(f"🎤 Microphone {'activated' if active else 'deactivated'}")
    
    def stop(self):
        """Properly stop the thread"""
        self._is_running = False
        self.wait(1000)


class SmritiWindow(QWidget):
    captionSignal = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
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

        # Text input field with glassmorphism
        input_container = QWidget(self)
        input_container.setStyleSheet("background: transparent;")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(16, 8, 16, 8)
        input_layout.setSpacing(8)
        
        # Text input field
        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("Type your message here...")
        self.text_input.setStyleSheet("""
            QLineEdit {
                background: rgba(100, 40, 180, 0.3);
                border: 2px solid rgba(160, 90, 250, 0.5);
                border-radius: 20px;
                color: white;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                padding: 10px 16px;
                backdrop-filter: blur(10px);
            }
            QLineEdit:focus {
                border: 2px solid rgba(210, 150, 255, 0.8);
                background: rgba(120, 60, 200, 0.4);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.6);
            }
        """)
        self.text_input.returnPressed.connect(self.send_text_command)
        input_layout.addWidget(self.text_input)
        
        # Send button
        self.send_btn = QPushButton("➤", self)
        self.send_btn.setFixedSize(40, 40)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: rgba(160, 90, 250, 0.5);
                border: 2px solid rgba(210, 150, 255, 0.6);
                border-radius: 20px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(180, 110, 270, 0.6);
                border: 2px solid rgba(230, 170, 255, 0.8);
            }
            QPushButton:pressed {
                background: rgba(140, 70, 230, 0.7);
            }
        """)
        self.send_btn.clicked.connect(self.send_text_command)
        input_layout.addWidget(self.send_btn)
        
        # Mic toggle button
        self.mic_btn = QPushButton("🎤", self)
        self.mic_btn.setFixedSize(40, 40)
        self.mic_btn.setCheckable(True)
        self.mic_btn.setChecked(False)  # Mic off by default
        self.mic_btn.clicked.connect(self.toggle_mic)
        self.update_mic_button_style()
        input_layout.addWidget(self.mic_btn)
        
        layout.addWidget(input_container)

        self.setFixedSize(440, 540)  # Increased height for new elements

        # Live caption hookup
        self.captionSignal.connect(self.on_caption)
        set_caption_callback(lambda text: self.captionSignal.emit(text))

        # Show loading message immediately
        self.caption_label.setText("Please Wait Smriti System Booting...")
        
        # Defer heavy initialization until after window is shown
        self.listener = None
        self.mic_active = False
        QTimer.singleShot(100, self.initialize_background_services)

    def initialize_background_services(self):
        """Initialize heavy services after window is shown for faster launch"""
        try:
            print("🔧 Initializing background services...")
            # Start listener thread
            self.listener = SmritiListener(self)
            self.listener.start()
            print("✅ Listener thread started")
            
            # Start welcome message - typing and speech simultaneously
            QTimer.singleShot(500, self.start_welcome_message)
        except Exception as e:
            print(f"❌ Error initializing background services: {e}")
    
    def start_welcome_message(self):
        """Start welcome message with simultaneous typing and speech"""
        try:
            print("🔊 Starting welcome message...")
            welcome_text = "Hello Sumit! Smriti system is now activated!"
            
            # Start speaking - this will trigger caption callback which starts typing automatically
            # Both will happen simultaneously
            speak(welcome_text)
            print("✅ Welcome message started (typing + speech simultaneously)")
        except Exception as e:
            print(f"❌ Welcome message error: {e}")

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
        if hasattr(self, 'listener') and self.listener:
            self.listener.stop()
        super().closeEvent(event)
    
    def toggle_mic(self):
        """Toggle microphone listening on/off"""
        self.mic_active = self.mic_btn.isChecked()
        if self.listener:
            self.listener.set_mic_active(self.mic_active)
        self.update_mic_button_style()
        if self.mic_active:
            self.captionSignal.emit("🎤 Microphone activated - Listening...")
        else:
            self.captionSignal.emit("🔇 Microphone deactivated")
    
    def update_mic_button_style(self):
        """Update mic button style based on state"""
        if self.mic_btn.isChecked():
            self.mic_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 80, 80, 0.6);
                    border: 2px solid rgba(255, 120, 120, 0.8);
                    border-radius: 20px;
                    color: white;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background: rgba(255, 100, 100, 0.7);
                    border: 2px solid rgba(255, 140, 140, 1.0);
                }
                QPushButton:pressed {
                    background: rgba(255, 60, 60, 0.8);
                }
            """)
        else:
            self.mic_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(100, 40, 180, 0.4);
                    border: 2px solid rgba(160, 90, 250, 0.6);
                    border-radius: 20px;
                    color: white;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background: rgba(120, 60, 200, 0.5);
                    border: 2px solid rgba(180, 110, 270, 0.8);
                }
                QPushButton:pressed {
                    background: rgba(80, 20, 160, 0.6);
                }
            """)
    
    def send_text_command(self):
        """Process text input command"""
        text = self.text_input.text().strip()
        if not text:
            return
        
        # Clear input field
        self.text_input.clear()
        
        # Show user's command instantly (no typing animation)
        self.caption_label.setText(f"You: {text}")
        
        # Process command in a separate thread to avoid blocking UI
        def process_in_thread():
            try:
                print(f"📝 Processing text command: {text}")
                
                # Show thinking message with typing animation
                self.captionSignal.emit("💭 Thinking...")
                
                # Process command
                response = process_command(text, speak_out=False)
                
                if response and response.strip():
                    print(f"💬 Response: {response}")
                    # Update UI with response
                    self.captionSignal.emit(response)
                    # Speak the response
                    speak(response)
                else:
                    fallback = "I'm here, Sumit. How can I help you?"
                    self.captionSignal.emit(fallback)
                    speak(fallback)
            except Exception as e:
                print(f"❌ Error processing text command: {e}")
                error_msg = "Sorry, I encountered an error. Please try again."
                self.captionSignal.emit(error_msg)
                speak(error_msg)
        
        # Run in thread to avoid blocking
        import threading
        thread = threading.Thread(target=process_in_thread, daemon=True)
        thread.start()
    
    def showEvent(self, event):
        """Ensure window is focused when shown"""
        super().showEvent(event)
        self.raise_()
        self.activateWindow()
        self.setFocus()