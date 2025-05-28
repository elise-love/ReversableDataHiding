# __init__.py
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QFileDialog, QGraphicsOpacityEffect,QTextEdit
from PyQt5.QtCore import Qt, QPoint, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPixmap, QFont, QLinearGradient, QBrush, QPainter, QPen, QColor
import sys, os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import rdh
import crdh
import datetime

from encodeWindow import EncodeWindow
from decodeWindow import DecodeWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        #window properties
        self.setFixedSize(1400, 900)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setCentralWidget(QWidget())

        self.is_encoding = True
        self.current_encoding_image_path = None
        self.current_decoding_image_path = None

        #background color settings
        self.color_block = QWidget(self)
        self.color_block.setGeometry(0, 0, 1400, 900)
        self.color_block.setStyleSheet("background-color: rgba(30, 30, 30, 0.9); border-radius: 5px;")

        #icon label settings
        self.icon_label = QLabel(self)
        self.icon_label.setGeometry(70, 20, 250, 250)
        self.icon1_path = os.path.join(os.path.dirname(__file__),"icons", "icon1.jpg")
        self.icon2_path = os.path.join(os.path.dirname(__file__),"icons",  "icon2.jpg")
        self.set_icon(self.icon1_path)

        #mode text settings
        self.modeText = QLabel("Current Mode: Encoding...", self)
        self.modeText.setGeometry(50, 235, 250, 30)
        self.modeText.setAlignment(Qt.AlignCenter)
        self.modeText.setStyleSheet("font-size: 20px; color: rgba(255, 105, 180, 0.9); font-family:'Comic Sans MS';")
        
        # Setup fade-in / fade-out animation
        self.mode_opacity_effect = QGraphicsOpacityEffect()
        self.modeText.setGraphicsEffect(self.mode_opacity_effect)

        self.mode_animation = QPropertyAnimation(self.mode_opacity_effect, b"opacity")
        self.mode_animation.setDuration(1500)  # 1 second fade
        self.mode_animation.setStartValue(1.0)
        self.mode_animation.setEndValue(0.2)
        self.mode_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.mode_animation.setLoopCount(-1)  # Infinite loop
        self.mode_animation.start()


        #elements container settings
        self.encoding_container = EncodeWindow(self)
        self.decoding_container = DecodeWindow(self)
        self.decoding_container.hide()

        #dashboard settings
        self.dashboard  = QTextEdit(self)
        self.dashboard.setGeometry(450,40,410,240)
        self.dashboard.setReadOnly(True)
        self.dashboard.setStyleSheet("""
            background-color: rgba(0, 0, 0, 130);
            color: #00FF00;
            font-size: 14px;
            font-family: 'Courier New';
            border-radius: 3px;
            padding: 10px;
        """
        )

        #toggle object
        self.icon_label.mouseDoubleClickEvent = self.toggle_mode

        #dragging boolean
        self.mouse_is_dragging = False

        #encode image transmission
        self.encoded_pixmap_transmission = None


    def set_icon(self, path):
        pixmap = QPixmap(path).scaled(160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(pixmap)

    def toggle_mode(self, e):
        if self.is_encoding:
            self.color_block.setStyleSheet("background-color: rgba(60, 40, 40, 0.8); border-radius: 5px;")
            self.set_icon(self.icon2_path)
            self.modeText.setText("Current Mode: Decoding...")
            self.modeText.setStyleSheet("font-size: 20px; color: rgba(230, 230, 230, 0.9); font-family:'Comic Sans MS';")
            self.encoding_container.hide()
            self.decoding_container.show()
            self.is_encoding = False
            self.dashboard_message_display("Changed mode to decoding","red")
        else:
            self.color_block.setStyleSheet("background-color: rgba(30, 30, 30, 0.9); border-radius: 5px;")
            self.set_icon(self.icon1_path)
            self.modeText.setText("Current Mode: Encoding...")
            self.modeText.setStyleSheet("font-size: 20px; color: rgba(255, 105, 180, 0.9); font-family:'Comic Sans MS';")
            self.decoding_container.hide()
            self.encoding_container.show()
            self.is_encoding = True
            self.dashboard_message_display("Changed mode to encoding","lightpink")
            
  

    def select_image(self, mode):
        path, _ = QFileDialog.getOpenFileName(       #path: return user's chosen path(if canceled than return empty string), _:ignore檔案篩選器回傳值
            self,                                    #視窗父物件，確保對話框為主視窗子視窗
            "Select Image",                          #window title
            "",                                      #預設路徑(空字串 = 使用系統預設)
            "Images (*.png *.jpg *.jpeg *.bmp)"      #檔案類型過濾器
        )
        
        #if user selected an img
        if path:
            if mode == 'encoding':

                #save teh selected img path
                self.current_encoding_image_path = path

                #create QPixmap obj and scale it to diaplay in the preview area
                pixmap = QPixmap(path).scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.encoding_container.enc_image_preview.setPixmap(pixmap)
                self.encoding_container.enc_image_preview.setText("")#clear text

            else:
                self.current_decoding_image_path = path
                pixmap = QPixmap(path).scaled(280, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.decoding_container.dec_image_preview.setPixmap(pixmap)
                self.decoding_container.dec_image_preview.setText("")

    def run_encoding(self):
        try:
            #step1: check of the image path is there
            if not self.current_encoding_image_path:            
                self.dashboard_message_display("Please select an image first!", "lightpink")
                return

            #step2: check if the encoded text is there 
            message = self.encoding_container.enc_textbox.text().strip()
            if not message:
                self.dashboard_message_display("Please enter text to encode!", "lightpink")
                return
            
            #step3: turn the message to 二進位(每個字8 bits)
            #ord(c): 把單一字元 c 轉成對應的 ASCII / Unicode 數值（int）
            #format(..., '08b'): int 轉成 8 bits 的二進位string
            #for c in message: 對 message 中每個字元執行轉換
            #''.join(...): 把所有二進位字串接在一起，形成完整的隱藏資料 bit stream
            message_bits = ''.join(format(ord(c), '08b') for c in message)
            
            #step4: read color image (BGR 格式)
            img_color = cv2.imread(self.current_encoding_image_path)
            if img_color is None:
                self.dashboard_message_display("Failed to load image!","lightpink")
                return

            img_ycrcb = cv2.cvtColor(img_color, cv2.COLOR_BGR2YCrCb)
            img_y = img_ycrcb[:, :, 0]
            hist = cv2.calcHist([img_y], [0], None, [256], [0, 256])
            peak = int(np.argmax(hist))

            peak_bits = format(peak, '08b')
            length_prefix = format(len(message_bits), '016b')
            full_data_bits = peak_bits + length_prefix + message_bits

            capacity = int(hist[peak][0])
            if len(full_data_bits) > capacity:
                self.dashboard_message_display("Error", f"Data too large to embed.\nRequired: {len(full_data_bits)} bits, Available: {capacity} bit","blue")
                return

            embedded_color, used_bits = rdh.embed_data_color(img_color, full_data_bits, peak)
            embedded_path = os.path.join(os.path.dirname(__file__), "tempFile", "temp_embedded.png")
            cv2.imwrite(embedded_path, embedded_color)

            embedded_pixmap = QPixmap(embedded_path).scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.encoding_container.enc_encoded_image.setPixmap(embedded_pixmap)
            self.dashboard_message_display("Embedding image completed!","grey")

            # Calculate the embedded image histogram
            embedded_ycrcb = cv2.cvtColor(embedded_color, cv2.COLOR_BGR2YCrCb)
            embedded_y = embedded_ycrcb[:, :, 0]
            hist_embedded = cv2.calcHist([embedded_y], [0], None, [256], [0, 256])

            # Display the histograms directly in the HistogramWidgets
            self.encoding_container.enc_histograms[0].set_histogram_data(hist, title="Original Y Histogram", color=QColor(100, 150, 255), peak=peak)
            self.dashboard_message_display("Original histogram successfully painted!", "grey")
            
            self.encoding_container.enc_histograms[1].set_histogram_data(hist_embedded, title="Embedded Y Histogram", color=QColor(255, 100, 100), peak=peak)
            self.dashboard_message_display("Shifted histogram successfully painted!", "grey")


            #encoded image transmission
            self.encoded_pixmap_transmission = embedded_pixmap
            self.decoding_container.dec_image_preview.setPixmap(self.encoded_pixmap_transmission)
            self.dashboard_message_display("Encoded image transmitted to decoding mode","grey")


        except Exception as e:
            self.dashboard_message_display("An error occurred during encoding","lightpink")

    def run_decoding(self):
        try:
            if not self.current_decoding_image_path:
                self.dashboard_message_display("Please select an image first!","red")
                return

            img_color = cv2.imread(self.current_decoding_image_path)
            self.dashboard_message_display("Image selection successufl!","grey")

            if img_color is None:
                self.dashboard_message_display("Failed to load image!","red")
                return

            decoded_pixmap = QPixmap(self.current_decoding_image_path).scaled(350, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.decoding_container.dec_decoded_image.setPixmap(decoded_pixmap)
            self.dashboard_message_display("Load image successful!","grey")

            self.decoding_container.dec_decoded_text.setText("Decoding functionality not implemented yet.")

            img_ycrcb = cv2.cvtColor(img_color, cv2.COLOR_BGR2YCrCb)
            img_y = img_ycrcb[:, :, 0]
            hist = cv2.calcHist([img_y], [0], None, [256], [0, 256])

            # Display the histogram in the decoding histogram widget
            self.decoding_container.dec_histogram.set_histogram_data(hist, title="Decoded Y Histogram", color=QColor(100, 150, 255))

        except Exception as e:
            self.dashboard_message_display("An error occurred during encoding","red")


    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.mouse_is_dragging = True
            self.mouse_drag_position = e.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self.mouse_is_dragging and (e.buttons() & Qt.LeftButton):
            self.move(e.globalPos() - self.mouse_drag_position)

    def mouseReleaseEvent(self, e):
        self.mouse_is_dragging = False

    #display words on dashboard
    def dashboard_message_display(self, message, color="grey"):
        # Get current timestamp
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")

        # Apply color tag for HTML if needed
        formatted_message = f"<span style='color:{color}'>{timestamp} {message}</span>"

        # Append to existing text
        self.dashboard.append(formatted_message)

        # Optional: Auto-scroll to bottom
        self.dashboard.verticalScrollBar().setValue(self.dashboard.verticalScrollBar().maximum())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 