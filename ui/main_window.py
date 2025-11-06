from PyQt5.QtCore import Qt, QTimer, QPoint, QThread
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from ui.circular_indicator import CircularIndicator
from core.voice_response import speak
from core.voice_recognition import listen_command
from core.brain import process_command
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
    def run(self):
        while True:
            command = listen_command()
            if command:
                process_command(command)


class SmritiWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

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
            font-family: 'Orbitron';
            font-size: 14px;
            font-weight: bold;
            padding: 8px 20px;
            margin-top: 10px;
        """)
        layout.addWidget(self.caption_label, alignment=Qt.AlignCenter)

        self.setFixedSize(440, 460)

        greeting = "✨ Smriti System Activated — Hello Sumit 💜"
        self.start_typing_animation(greeting)
        speak("Smriti system activated. Hello Sumit.")

        self.listener = SmritiListener()
        self.listener.start()

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
