# histogram_widget.py
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor, QFont
import numpy as np

class HistogramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.histogram_data = None
        self.title = ""
        self.color = QColor(100, 150, 255)  # Default blue
        self.peak_value = None
        self.setMinimumSize(400, 200)

        # Let the parent¡¦s dark background show through
        self.setAttribute(Qt.WA_TranslucentBackground)

    def set_histogram_data(self, hist_data, title="Histogram", color=None, peak=None):
        self.histogram_data = hist_data.flatten() if hist_data is not None else None
        self.title = title
        if color:
            self.color = color
        self.peak_value = peak
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        # === FIXED GUARD ===
        if self.histogram_data is None or len(self.histogram_data) == 0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        ml, mr, mt, mb = 40, 20, 40, 30
        plot_w, plot_h = w - ml - mr, h - mt - mb

        # Draw bars
        maxv = np.max(self.histogram_data)
        bar_w = plot_w / len(self.histogram_data)
        for i, v in enumerate(self.histogram_data):
            if v <= 0: continue
            ph = (v / maxv) * plot_h
            x = ml + i * bar_w
            y = mt + (plot_h - ph)

            col = (
                QColor(255, 100, 100, 180)
                if (self.peak_value == i)
                else QColor(self.color.red(), self.color.green(), self.color.blue(), 180)
            )
            painter.fillRect(int(x), int(y), int(bar_w), int(ph), col)

        # Draw grid
        pen = QPen(QColor(60, 60, 60), 1)
        painter.setPen(pen)
        for j in range(1, 5):
            yy = mt + plot_h * j // 5
            painter.drawLine(ml, yy, ml + plot_w, yy)
        for i in range(1, 8):
            xx = ml + plot_w * i // 8
            painter.drawLine(xx, mt, xx, mt + plot_h)

        # Axes labels
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.setFont(QFont("Arial", 9))
        step = max(1, len(self.histogram_data) // 8)
        for i in range(0, len(self.histogram_data), step):
            xx = ml + i * bar_w
            painter.drawText(int(xx), h - 5, str(i))
        # Y-label
        painter.save()
        painter.translate(15, mt + plot_h / 2)
        painter.rotate(-90)
        painter.drawText(0, 0, "Frequency")
        painter.restore()
        # X-label
        painter.drawText(ml + plot_w // 2 - 30, h - 5, "Pixel Value")

        # Title
        painter.setPen(QPen(QColor(235, 106, 181), 1))
        painter.setFont(QFont("Comic Sans MS", 12, QFont.Bold))
        painter.drawText(ml, mt - 12, self.title)

        # Pink dashed border to match your other frames
        dash_pen = QPen(QColor(235, 106, 181), 2, Qt.DashLine)
        painter.setPen(dash_pen)
        painter.drawRoundedRect(1, 1, w - 2, h - 2, 5, 5)
