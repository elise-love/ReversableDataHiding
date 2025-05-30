# rdh.py
import cv2
import numpy as np
# ===== 灰階影像嵌入函式（直方圖位移） =====
def embed_data(grayscaleImg, data_bits, peak):
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

    #flattens the 2D img matrix into a 1D array(easier to iterate over every pixel)
    img_flat = grayscaleImg.flatten()

    #copy of flattened message(not to mess with the original)
    embedded_img = img_flat.copy()

    #所有 < peak 的像素都減 1
    for i in range(len(embedded_img)):
        if embedded_img[i] < peak:
            embedded_img[i] -= 1 

    # 嵌入資料到原本位於 peak 的位置
    embedding_bit = 0 

    for i in range(len(embedded_img)):
        if embedded_img[i] == peak and embedding_bit < len(data_bits):
            #if the current data bit is [1], set the pixel to peak-1 to represent 1
            if data_bits[embedding_bit] == '1':
                embedded_img[i] -= 1  
            else:
                embedded_img[i] = peak
            embedding_bit += 1

    #after embedding, enure pixel values are valid (0-255) and reshape back to the original img shape
    embedded_img = np.clip(embedded_img, 0, 255).reshape(grayscaleImg.shape)
    
    #return 1.modified image 2.how many bits able to embed(useful for debugging)
    return embedded_img, embedding_bit

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
    #convert BGR(nomal OpenCV color order) to YCrCb
    img_ycrcb = cv2.cvtColor(img_color, cv2.COLOR_BGR2YCrCb)

    #Y:brightness
    #Cr, Cb: color
    #split to 3 channels
    Y, Cr, Cb = cv2.split(img_ycrcb)

    #make sure Y channel's data type is 8-bit integers(required by OpenCV)
    if Y.dtype != np.uint8:
        Y = Y.astype(np.uint8)

    # 嵌入
    embedded_Y, used_bits = embed_data(Y, data_bits, peak)

    #keep pixel values valid and ensure data type is correct
    embedded_Y = np.clip(embedded_Y, 0, 255).astype(np.uint8)

    # 合併通道並轉回 BGR
    embedded_ycrcb = cv2.merge([embedded_Y, Cr, Cb])
    embedded_color = cv2.cvtColor(embedded_ycrcb, cv2.COLOR_YCrCb2BGR)

    return embedded_color, used_bits

"""
cv2.cvtColor :做色彩空間轉換

cv2.split / cv2.merge :取通道

np.clip 讓數值在範圍內
"""