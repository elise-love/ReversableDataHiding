# encodeWindow.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import rdh
from histogram_widget import HistogramWidget

class EncodeWindow(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setGeometry(50, 300, 1300, 550)
        self.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.6);
            border-radius: 12px;
        """)
        self.build_ui()

    def build_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(30)

        # Left panel
        input_panel = QFrame()
        input_panel.setStyleSheet("background-color: transparent;")
        input_layout = QVBoxLayout()
        input_layout.setSpacing(15)
        input_layout.setAlignment(Qt.AlignTop)

        self.enc_image_preview = QLabel(".. or Drop images here")
        self.enc_image_preview.setFixedSize(300, 300)
        self.enc_image_preview.setAlignment(Qt.AlignCenter)
        self.enc_image_preview.setStyleSheet("""
            border: 2px dashed rgba(255, 105, 180, 0.9);
            background-color: rgba(50, 0, 0, 0.7);
            font-size:16px;
            font-family:'Comic Sans MS';
            color: rgba(255, 105, 180, 0.9);
            border-radius: 10px;
        """)
        input_layout.addWidget(self.enc_image_preview, alignment=Qt.AlignCenter)

        self.enc_select_btn = QPushButton("Select Image")
        self.enc_select_btn.setFixedSize(200, 40)
        self.enc_select_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 105, 180, 0.8);
                color: #000;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-family: 'Comic Sans MS';
            }
            QPushButton:hover {
                background-color: rgba(255, 20, 147, 0.8);
            }
        """)
        self.enc_select_btn.clicked.connect(lambda: self.parent.select_image('encoding'))
        input_layout.addWidget(self.enc_select_btn, alignment=Qt.AlignCenter)

        self.enc_textbox = QLineEdit()
        self.enc_textbox.setPlaceholderText("Enter text to encode")
        self.enc_textbox.setFixedSize(300, 40)
        self.enc_textbox.setStyleSheet("""
            font-size:16px;
            font-family:'Comic Sans MS';
            border: 1px solid rgba(255, 105, 180, 0.9);
            border-radius: 8px;
            padding: 5px 10px;
            background-color: rgba(50, 0, 0, 0.85);
            color: #fff;
        """)
        input_layout.addWidget(self.enc_textbox, alignment=Qt.AlignCenter)

        self.enc_run_btn = QPushButton("Run")
        self.enc_run_btn.setFixedSize(200, 40)
        self.enc_run_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 105, 180, 0.8);
                color: #000;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-family: 'Comic Sans MS';
            }
            QPushButton:hover {
                background-color: rgba(255, 20, 147, 0.8);
            }
        """)
        self.enc_run_btn.clicked.connect(self.run_encoding)
        input_layout.addWidget(self.enc_run_btn, alignment=Qt.AlignCenter)

        input_panel.setLayout(input_layout)

        # Center panel
        encoded_panel = QFrame()
        encoded_panel.setStyleSheet("background-color: transparent;")
        encoded_layout = QVBoxLayout()
        encoded_layout.setAlignment(Qt.AlignCenter)

        encoded_title = QLabel("Encoded Image")
        encoded_title.setStyleSheet("font-size:16px; color: rgba(255, 105, 180, 0.9); font-family:'Comic Sans MS';")
        encoded_layout.addWidget(encoded_title, alignment=Qt.AlignCenter)

        self.enc_encoded_image = QLabel()
        self.enc_encoded_image.setFixedSize(400, 400)
        self.enc_encoded_image.setStyleSheet("""
            border: 1px solid rgba(255, 105, 180, 0.9);
            background-color: rgba(50, 0, 0, 0.6);
            border-radius: 10px;
        """)
        self.enc_encoded_image.setAlignment(Qt.AlignCenter)
        encoded_layout.addWidget(self.enc_encoded_image, alignment=Qt.AlignCenter)

        encoded_panel.setLayout(encoded_layout)

        # Right panel (histograms)
        hist_panel = QFrame()
        hist_panel.setStyleSheet("background-color: transparent;")
        hist_layout = QVBoxLayout()
        hist_layout.setAlignment(Qt.AlignCenter)

        self.enc_histograms = []
        for title in ["Original Histogram", "Shifted Histogram"]:
            label = QLabel(title)
            label.setStyleSheet("""
                font-size:16px;
                font-family:'Comic Sans MS';
                color: rgba(255, 105, 180, 0.9);
            """)
            hist_layout.addWidget(label, alignment=Qt.AlignCenter)

            hist_widget = HistogramWidget()  # 改成 HistogramWidget
            hist_widget.setFixedSize(400, 200)
            hist_layout.addWidget(hist_widget, alignment=Qt.AlignCenter)
            self.enc_histograms.append(hist_widget)

        hist_panel.setLayout(hist_layout)

        layout.addWidget(input_panel, 1)
        layout.addWidget(encoded_panel, 1)
        layout.addWidget(hist_panel, 1)

        self.setLayout(layout)

    def run_encoding(self):
        self.parent.enc_textbox = self.enc_textbox
        self.parent.enc_image_preview = self.enc_image_preview
        self.parent.enc_encoded_image = self.enc_encoded_image
        self.parent.enc_histograms = self.enc_histograms
        self.parent.run_encoding()
