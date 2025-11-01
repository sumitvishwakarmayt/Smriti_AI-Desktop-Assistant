from PyQt5.QtCore import Qt, QTimer, QPoint, QThread
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from ui.circular_indicator import CircularIndicator
from core.voice_response import speak
import time


class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setStyleSheet("""
            background-color: rgba(90, 0, 160, 200);
            color: white;
            font-weight: bold;
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
        """)

        self.title = QLabel("💜 Smriti — AI Desktop Assistant", self)
        self.title.setStyleSheet("padding-left: 15px; font-family: 'Orbitron'; font-size: 14px;")

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
        layout.addWidget(self.title)
        layout.addStretch()
        layout.addWidget(self.minBtn)
        layout.addWidget(self.closeBtn)
        layout.setContentsMargins(10, 0, 10, 0)

        self.minBtn.clicked.connect(parent.showMinimized)
        self.closeBtn.clicked.connect(parent.close)
        self.oldPos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.oldPos:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.parent().move(self.parent().x() + delta.x(), self.parent().y() + delta.y())
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.oldPos = None


class VoiceThread(QThread):
    def run(self):
        time.sleep(1)  # lil pause before she talks
        speak("Smriti System Activated - Hello Sumit")


class SmritiWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Add TitleBar
        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)

        # Add glowing indicator
        self.indicator = CircularIndicator(self)
        layout.addWidget(self.indicator, alignment=Qt.AlignCenter)

        # Caption label (typing effect)
        self.caption_label = QLabel("", self)
        self.caption_label.setAlignment(Qt.AlignCenter)
        self.caption_label.setStyleSheet("""
            color: white;
            background: rgba(60, 0, 100, 130);
            border-radius: 10px;
            font-family: 'Orbitron';
            font-size: 14px;
            font-weight: bold;
            padding: 8px 20px;
            margin-top: 10px;
        """)
        layout.addWidget(self.caption_label, alignment=Qt.AlignCenter)

        # Window appearance
        self.setFixedSize(440, 460)

        # Start typing effect AND voice
        self.start_typing_animation("✨ Smriti System Activated — Hello Sumit 💜")

        self.voice_thread = VoiceThread()
        self.voice_thread.start()

    def start_typing_animation(self, text):
        self.full_text = text
        self.caption_label.setText("")
        self.current_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_text)
        self.timer.start(35)

    def update_text(self):
        if self.current_index < len(self.full_text):
            self.caption_label.setText(self.caption_label.text() + self.full_text[self.current_index])
            self.current_index += 1
        else:
            self.timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(25, 0, 60, 180))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)
