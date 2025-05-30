# histogram_widget.py
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor, QFont
import numpy as np

class HistogramWidget(QWidget):
    def __init__(self, parent=None, mode="encode"):#default mode:encode
        super().__init__(parent)
        self.histogram_data = None
        self.title = ""
        self.color = QColor(100, 150, 255)
        self.peak_value = None
        self.mode = mode  #mode (encode/decode)
        self.setMinimumSize(400, 200)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def set_histogram_data(self, hist_data, title="Histogram", color=None, peak=None):
        self.histogram_data = hist_data.flatten() if hist_data is not None else None
        self.title = title
        if color:
            self.color = color
        self.peak_value = peak
        self.update()  #trigger repaint

    def paintEvent(self, event):
        pink = (255, 105, 150)
        red = (80, 0, 0, 153)
        gold = (255, 215, 0) 

        # === FIXED GUARD ===
        if self.histogram_data is None or len(self.histogram_data) == 0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        ml, mr, mt, mb = 40, 20, 40, 30
        plot_w, plot_h = w - ml - mr, h - mt - mb

        # Determine bar color based on mode
        if self.mode == "decode":
            base_color = red
            border_color = QColor(255, 255, 255)  # White border
            title_color = QColor(255, 255, 255)   # White title
        else:
            base_color = pink
            border_color = QColor(235, 106, 181)  # Pink border
            title_color = QColor(235, 106, 181)   # Pink title

        # Draw bars
        maxv = np.max(self.histogram_data)
        bar_w = plot_w / len(self.histogram_data)

        for i, v in enumerate(self.histogram_data):
            if v <= 0:
                continue
            ph = (v / maxv) * plot_h
            x = ml + i * bar_w
            y = mt + (plot_h - ph)
            if i == self.peak_value:
                col = QColor(*gold, 220)
            elif hasattr(self, 'shifted_indices') and i in self.shifted_indices:
                col = QColor(*base_color, 180) if len(base_color) == 3 else QColor(*base_color)
            else:
                col = QColor(*base_color, 180) if len(base_color) == 3 else QColor(*base_color)
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
        painter.setPen(QPen(title_color, 1))
        painter.setFont(QFont("Comic Sans MS", 12, QFont.Bold))
        painter.drawText(ml, mt - 12, self.title)

        # Border (white in decode mode)
        dash_pen = QPen(border_color, 2, Qt.DashLine)
        painter.setPen(dash_pen)
        painter.drawRoundedRect(1, 1, w - 2, h - 2, 5, 5)