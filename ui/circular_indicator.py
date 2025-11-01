from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush, QRadialGradient
from PyQt5.QtCore import Qt, QTimer


class CircularIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(260, 260)
        self.alpha = 160
        self.direction = 1
        self.speed = 3
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Timer for breathing glow
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animateGlow)
        self.timer.start(30)

    def animateGlow(self):
        self.alpha += self.direction * self.speed
        if self.alpha >= 255:
            self.alpha = 255
            self.direction = -1
        elif self.alpha <= 100:
            self.alpha = 100
            self.direction = 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Holographic glow gradient
        gradient = QRadialGradient(self.rect().center(), min(self.width(), self.height()) / 2)
        gradient.setColorAt(0.0, QColor(255, 255, 255, 180))
        gradient.setColorAt(0.3, QColor(180, 0, 255, self.alpha))
        gradient.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)

        diameter = min(self.width(), self.height()) - 40
        x = int((self.width() - diameter) / 2)
        y = int((self.height() - diameter) / 2)
        painter.drawEllipse(x, y, diameter, diameter)
