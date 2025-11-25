from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QColor, QPainter, QRadialGradient, QPainterPath
from PySide6.QtWidgets import QWidget
import math


class CircularIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.phase = 0.0
        self.active = True

        # Make the orb smaller and translucent background
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(220, 220)  # reduced from 260

        # 60 FPS animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_indicator)
        self.timer.start(16)

    def update_indicator(self):
        if self.active:
            self.phase = (self.phase + 2.5) % 360.0
            self.update()

    def set_active(self, active: bool):
        self.active = active
        if active:
            self.timer.start(16)
        else:
            self.timer.stop()
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rectf = QRectF(self.rect())

        # Smooth circle clipping (no hard square edges)
        clip_path = QPainterPath()
        clip_path.addEllipse(rectf)
        painter.setClipPath(clip_path)

        # Breathing animation phase (0..1)
        pulse = (math.sin(math.radians(self.phase)) + 1.0) / 2.0

        # Radius and pulse scaling
        base_radius = min(rectf.width(), rectf.height()) * 0.38
        radius = base_radius + (pulse * base_radius * 0.15)

        center = QPointF(rectf.center())

        # 💎 Enhanced gradient with subtle opacity + deeper hue variation
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0.0, QColor(255, 240, 255, 200))  # soft white heart
        gradient.setColorAt(0.2, QColor(210, 150, 255, 180))
        gradient.setColorAt(0.45, QColor(160, 90, 250, 160))
        gradient.setColorAt(0.75, QColor(100, 40, 180, 130))
        gradient.setColorAt(1.0, QColor(40, 0, 100, 70))  # smooth fade-out edge

        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)

        # Draw inner glow circle
        inner_rect = QRectF(center.x() - radius, center.y() - radius, radius * 2.0, radius * 2.0)
        painter.drawEllipse(inner_rect)

        # ✨ Outer aura — faint translucent mist
        halo_radius = radius * (1.4 + 0.1 * pulse)
        halo_alpha = int(35 + pulse * 70)
        outer_gradient = QRadialGradient(center, halo_radius)
        outer_gradient.setColorAt(0.0, QColor(230, 190, 255, halo_alpha))
        outer_gradient.setColorAt(1.0, QColor(50, 0, 90, 0))

        painter.setBrush(outer_gradient)
        halo_rect = QRectF(center.x() - halo_radius, center.y() - halo_radius, halo_radius * 2.0, halo_radius * 2.0)
        painter.drawEllipse(halo_rect)

        # 🌙 Soft inner moving sheen for realism
        sheen_radius = radius * 0.8
        sheen_angle = math.radians(self.phase * 0.8)
        sx = center.x() + math.cos(sheen_angle) * (radius * 0.1)
        sy = center.y() + math.sin(sheen_angle) * (radius * 0.1)
        sheen_grad = QRadialGradient(QPointF(sx, sy), sheen_radius)
        sheen_grad.setColorAt(0.0, QColor(255, 255, 255, int(60 * (0.6 + pulse * 0.4))))
        sheen_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(sheen_grad)
        painter.drawEllipse(QRectF(sx - sheen_radius, sy - sheen_radius, sheen_radius * 2, sheen_radius * 2))
