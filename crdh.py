#crdh.py
import cv2
import numpy as np

def extract_bits_from_Y(Y_channel_embedded, original_peak, total_bits_to_extract):
    bits = ''
    img_flat = Y_channel_embedded.flatten()
    extracted_count = 0
    # 這裡我們假設原始 peak 值是已知的，並且我們要從嵌入的影像中提取位元
    for i in range(len(img_flat)):
        if extracted_count >= total_bits_to_extract:
            break  # 提取到足夠的位元就停止
        if img_flat[i] == original_peak:  # 這個像素原本是 peak，所以得知取出資料為 0
            bits += '0'
            extracted_count += 1
        elif img_flat[i] == original_peak - 1:  # 這個像素原本是 peak-1，所以得知取出資料為 1
            bits += '1'
            extracted_count += 1

    # 如果提取的位元數少於預期，發出警告
    if len(bits) < total_bits_to_extract:
        print(f"警告：未能提取到期望的 {total_bits_to_extract} 位元，只提取到 {len(bits)} 位元。影像可能已損壞或提供的 Peak 值不正確。")
    return bits

def bits_to_string(bits):
    """將位元串轉回原始文字"""
    chars = []
    # 每 8 位元組成一個字元，如果位元數不是 8 的倍數，則截斷到最近的位元組
    if len(bits) % 8 != 0:
        print(f"警告：提取的訊息位元數 ({len(bits)}) 不是 8 的倍數，可能訊息不完整或資料已損壞。截斷到最近的位元組。")
        bits = bits[:len(bits) - (len(bits) % 8)]  # 截斷到最近的位元組
    for i in range(0, len(bits), 8):  # 按照 8 位元分組，每組轉為一字元
        byte = bits[i:i+8]
        try:
            chars.append(chr(int(byte, 2)))
        except ValueError:
            print(f"警告：無法將位元串 '{byte}' 轉換為字元，可能資料已損壞。")
            chars.append('?')
    return ''.join(chars)  # 將字元串連接起來

def restore_Y_channel(Y_channel_embedded, original_peak):
    """根據原始 peak 將被修改過的像素值還原"""
    img_flat = Y_channel_embedded.flatten()
    restored = img_flat.copy()
    for i in range(len(restored)):
        embedded_value = img_flat[i]   # 嵌入後的像素值
        if embedded_value == original_peak:  # 嵌入後的像素值如果是 peak，則不動
            pass
        elif embedded_value == original_peak - 1:  # 嵌入後的像素值如果是 peak-1，則還原為原始 peak
            restored[i] = original_peak
        elif embedded_value < original_peak - 1:  # 嵌入後的像素值如果小於 peak-1，則還原為原始 peak+1
            restored[i] = embedded_value + 1
    return restored.reshape(Y_channel_embedded.shape)  # 將嵌入後的Ｙ通道復原

def decode_image(img_color):
    logs = []  # collect infos for dashboard

    img_ycrcb = cv2.cvtColor(img_color, cv2.COLOR_BGR2YCrCb)
    Y_channel_embedded = img_ycrcb[:, :, 0]

    # 第一步：直接用 Peak-based 方法提取前 24 個位元（8 bits peak + 16 bits length）
    total_header_bits = 8 + 16
    log_msg = f"直接使用 Peak-based 提取前 {total_header_bits} 位元（8+16）..."
    print(log_msg)
    logs.append(log_msg)

    header_bits = extract_bits_from_Y(
        Y_channel_embedded,
        original_peak=np.argmax(cv2.calcHist([Y_channel_embedded], [0], None, [256], [0, 256])),
        total_bits_to_extract=total_header_bits
    )

    peak_bits = header_bits[:8]
    length_bits = header_bits[8:24]

    if len(peak_bits) < 8 or len(length_bits) < 16:
        return None, "錯誤：未能提取完整的 Header（24 位元）。"

    extracted_peak = int(peak_bits, 2)
    message_length = int(length_bits, 2)
    log_msg = f"從影像中提取 Peak = {extracted_peak}，訊息長度（bits）= {message_length}"
    print(log_msg)
    logs.append(log_msg)

    # 第二步：使用正確的 Peak，提取完整資料（8 + 16 + message_length）
    total_bits_to_extract = 8 + 16 + message_length
    log_msg = f"使用提取到的 Peak，提取完整 {total_bits_to_extract} 位元..."
    print(log_msg)
    logs.append(log_msg)

    full_bits = extract_bits_from_Y(Y_channel_embedded, extracted_peak, total_bits_to_extract)
    if len(full_bits) < total_bits_to_extract:
        return None, "錯誤：未能提取完整的資料。可能資料已損壞。"

    # 第三步：還原文字
    message_bits = full_bits[24:]
    message = bits_to_string(message_bits)
    log_msg = f"還原出的訊息：{message}"
    print(log_msg)
    logs.append(log_msg)

    # 還原影像
    restored_Y = restore_Y_channel(Y_channel_embedded, extracted_peak)
    restored_Y = np.clip(restored_Y, 0, 255).astype(np.uint8)
    Cr = img_ycrcb[:, :, 1]
    Cb = img_ycrcb[:, :, 2]
    restored_ycrcb = cv2.merge([restored_Y, Cr, Cb])
    restored_img = cv2.cvtColor(restored_ycrcb, cv2.COLOR_YCrCb2BGR)

    hist_embedded = cv2.calcHist([Y_channel_embedded], [0], None, [256], [0, 256])
    hist_restored = cv2.calcHist([restored_Y], [0], None, [256], [0, 256])

    # Return structured data
    return {
        'message': message,
        'restored_img': restored_img,
        'hist_embedded': hist_embedded,
        'hist_restored': hist_restored,
        'extracted_peak': extracted_peak,
        'logs': logs
    }, None


"""
1. 從 Y 通道中提取 Peak bits
2. 提取訊息長度前綴
3. 提取完整訊息位元
4. 還原文字訊息
5. 還原 Y 通道與合併回彩色影像
6. 計算直方圖 the shifted histogram didn't show on the gui 
"""