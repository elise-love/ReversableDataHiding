# decodeWindow.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from histogram_widget import HistogramWidget

class DecodeWindow(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setGeometry(50, 300, 1300, 550)
        self.setStyleSheet("""
            background-color: rgba(40, 40, 40, 0.6);
            border-radius: 12px;
        """)
        self.build_ui()

    def build_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(35)

        # Input panel
        input_panel = QFrame()
        input_panel.setStyleSheet("background-color: transparent;")
        input_layout = QVBoxLayout()
        input_layout.setSpacing(20)
        input_layout.setAlignment(Qt.AlignTop)

        self.dec_image_preview = QLabel(".. or Drop images here")
        self.dec_image_preview.setFixedSize(280, 280)
        self.dec_image_preview.setStyleSheet("""
            border: 2px dashed rgba(230, 230, 230, 0.9);
            background-color: rgba(60, 40, 40, 0.7);
            font-size:16px;
            font-family:'Comic Sans MS';
            color: rgba(230, 230, 230, 0.9);
            border-radius: 10px;
        """)
        self.dec_image_preview.setAlignment(Qt.AlignCenter)
        input_layout.addWidget(self.dec_image_preview, alignment=Qt.AlignCenter)

        input_layout.addItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.dec_select_btn = QPushButton("Select Image")
        self.dec_select_btn.setFixedSize(200, 40)
        self.dec_select_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(128, 0, 0, 0.8);
                color: #fff;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-family: 'Comic Sans MS';
            }
            QPushButton:hover {
                background-color: rgba(200, 0, 0, 0.8);
            }
        """)
        self.dec_select_btn.clicked.connect(lambda: self.parent.select_image('decoding'))
        input_layout.addWidget(self.dec_select_btn, alignment=Qt.AlignCenter)

        input_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Input box for peak (moved to above Run button)
        self.dec_input_box = QLineEdit()
        self.dec_input_box.setPlaceholderText("Insert Key ?? :)))))")
        self.dec_input_box.setFixedSize(250, 35)
        self.dec_input_box.setStyleSheet("""
            background-color: rgba(60, 40, 40, 0.7);
            border: 1px solid rgba(230, 230, 230, 0.9);
            border-radius: 8px;
            font-size: 15px;
            font-family: 'Comic Sans MS';
            color: rgba(230, 230, 230, 0.9);
            padding-left: 10px;
        """)
        input_layout.addWidget(self.dec_input_box, alignment=Qt.AlignCenter)

        # Run button
        self.dec_run_btn = QPushButton("Run")
        self.dec_run_btn.setFixedSize(200, 40)
        self.dec_run_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(128, 0, 0, 0.8);
                color: #fff;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-family: 'Comic Sans MS';
            }
            QPushButton:hover {
                background-color: rgba(200, 0, 0, 0.8);
            }
        """)
        self.dec_run_btn.clicked.connect(self.parent.run_decoding)
        input_layout.addWidget(self.dec_run_btn, alignment=Qt.AlignCenter)

        input_panel.setLayout(input_layout)

        # Decoded image panel
        decoded_panel = QFrame()
        decoded_panel.setStyleSheet("background-color: transparent;")
        decoded_layout = QVBoxLayout()
        decoded_layout.setSpacing(10)
        decoded_layout.setAlignment(Qt.AlignCenter)

        # Title text
        decoded_title = QLabel("Decoded Image")
        decoded_title.setStyleSheet("""
            font-size:16px;
            font-family:'Comic Sans MS';
            color: rgba(230, 230, 230, 0.9);
        """)
        decoded_layout.addWidget(decoded_title, alignment=Qt.AlignCenter)
        
        # Decoded image preview
        self.dec_decoded_image = QLabel()
        self.dec_decoded_image.setFixedSize(350, 350)
        self.dec_decoded_image.setStyleSheet("""
            border: 1px solid rgba(230, 230, 230, 0.9);
            background-color: rgba(80, 0, 0, 0.6);
            border-radius: 10px;
        """)
        self.dec_decoded_image.setAlignment(Qt.AlignCenter)
        decoded_layout.addWidget(self.dec_decoded_image, alignment=Qt.AlignCenter)

        decoded_layout.addItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Decoded text output in scrollable area
        self.dec_decoded_text = QLabel("Decoded message will appear here")
        self.dec_decoded_text.setWordWrap(True)
        self.dec_decoded_text.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.dec_decoded_text.setStyleSheet("""
            font-size: 17px;
            font-family: 'Comic Sans MS';
            color: rgba(230, 230, 230, 0.8);
            background-color: rgba(60, 40, 40, 0.6);
            border: none;
            padding: 8px;
        """)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedSize(350, 70)
        scroll_area.setWidget(self.dec_decoded_text)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid rgba(230, 230, 230, 0.9);
                border-radius: 8px;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 8px;
                background: rgba(0, 0, 0, 0);
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.6);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        decoded_layout.addWidget(scroll_area, alignment=Qt.AlignCenter)

        decoded_panel.setLayout(decoded_layout)

        # Right panel (histograms)
        hist_panel = QFrame()
        hist_panel.setStyleSheet("background-color: transparent;")
        hist_layout = QVBoxLayout()
        hist_layout.setSpacing(10)
        hist_layout.setAlignment(Qt.AlignCenter)

        self.dec_histograms = []
        hist_titles = ["Original Histogram", "Shifted Histogram"]
        
        for i, title_text in enumerate(hist_titles):
            label = QLabel(title_text)
            label.setStyleSheet("""
                font-size:16px;
                font-family:'Comic Sans MS';
                color: white;
            """)
            hist_layout.addWidget(label, alignment=Qt.AlignCenter)

            hist = HistogramWidget(mode="decode")
            hist.setFixedSize(350, 180)
            hist.setStyleSheet("""
                border: 1px solid white;
                background-color: rgba(60, 40, 40, 0.8);
                border-radius: 10px;
            """)
            
            hist_layout.addWidget(hist, alignment=Qt.AlignCenter)
            self.dec_histograms.append(hist)

            if i < len(hist_titles) - 1:
                hist_layout.addItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))

        hist_panel.setLayout(hist_layout)

        main_layout.addWidget(input_panel, 1)
        main_layout.addWidget(decoded_panel, 1)
        main_layout.addWidget(hist_panel, 1)

        self.setLayout(main_layout)
