# rdh.py
import cv2
import numpy as np
# ===== 灰階影像嵌入函式（直方圖位移） =====
def embed_data(img, data_bits, peak):
    """
    將資料位元嵌入灰階影像。
    步驟：
    1. 先將所有 < peak 的像素值 -1（位移避免衝突）
    2. 從 peak 開始，依序用 data_bits 替換（遇到1時 peak-1，遇到0時 peak 保持）
    3. 限制像素值在 0~255 並重塑為影像形狀
    傳回：
        - 嵌入後的影像
        - 實際嵌入的位元數
    """
    img_flat = img.flatten()
    embedded_img = img_flat.copy()

    # 位移左側像素避免衝突: 所有 < peak 的像素都減 1
    for i in range(len(embedded_img)):
        if embedded_img[i] < peak:
            embedded_img[i] -= 1 

    # 嵌入資料到原本位於 peak 的位置
    data_index = 0
    for i in range(len(embedded_img)):
        if embedded_img[i] == peak and data_index < len(data_bits):
            if data_bits[data_index] == '1':
                embedded_img[i] -= 1  # 資料=1 -> peak-1
            else:
                embedded_img[i] = peak  # 資料=0 -> peak 維持
            data_index += 1

    embedded_img = np.clip(embedded_img, 0, 255).reshape(img.shape)
    return embedded_img, data_index

# ===== 彩色影像嵌入（使用 Y 通道） =====
def embed_data_color(img_color, data_bits, peak):
    """
    將資料嵌入彩色影像（僅使用 Y 通道）：
    1. 轉換為 YCrCb 色彩空間，分離 Y、Cr、Cb
    2. 嵌入資料到 Y 通道
    3. 合併通道並轉回 BGR
    傳回：
        - 嵌入後的彩色影像
        - 實際嵌入的位元數
    """
    img_ycrcb = cv2.cvtColor(img_color, cv2.COLOR_BGR2YCrCb)
    Y, Cr, Cb = cv2.split(img_ycrcb)

    # 確保 Y 通道是 uint8
    if Y.dtype != np.uint8:
        Y = Y.astype(np.uint8)

    # 嵌入
    embedded_Y, used_bits = embed_data(Y, data_bits, peak)
    embedded_Y = np.clip(embedded_Y, 0, 255).astype(np.uint8)

    # 合併通道並轉回 BGR
    embedded_ycrcb = cv2.merge([embedded_Y, Cr, Cb])
    embedded_color = cv2.cvtColor(embedded_ycrcb, cv2.COLOR_YCrCb2BGR)

    return embedded_color, used_bits
