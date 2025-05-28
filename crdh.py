#crdh.py
import cv2
import numpy as np
import matplotlib.pyplot as plt

def extract_bits_from_Y(Y_channel_embedded, original_peak, total_bits_to_extract):
    bits = ''
    img_flat = Y_channel_embedded.flatten()
    extracted_count = 0
    # 這裡我們假設原始 peak 值是已知的，並且我們要從嵌入的影像中提取位元
    for i in range(len(img_flat)):
        if extracted_count >= total_bits_to_extract:
            break  # 提取到足夠的位元就停止

        if img_flat[i] == original_peak: # 這個像素原本是 peak，所以得知取出資料為 0
            bits += '0'
            extracted_count += 1
        elif img_flat[i] == original_peak - 1: # 這個像素原本是 peak-1，所以得知取出資料為 1
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

    for i in range(0, len(bits), 8): #按照8位元分組，每組轉為一字元
        byte = bits[i:i+8]
        try:
            chars.append(chr(int(byte, 2))) 
        except ValueError:
            print(f"警告：無法將位元串 '{byte}' 轉換為字元，可能資料已損壞。")
            chars.append('?')
    return ''.join(chars) # 將字元串連接起來

def restore_Y_channel(Y_channel_embedded, original_peak):
    """根據原始 peak 將被修改過的像素值還原"""
    img_flat = Y_channel_embedded.flatten()
    restored = img_flat.copy()

    for i in range(len(restored)):
        embedded_value = img_flat[i]   # 嵌入後的像素值
        if embedded_value == original_peak: # 嵌入後的像素值如果是peak，則不動
            pass 
        elif embedded_value == original_peak - 1: # 嵌入後的像素值如果是peak-1，則還原為原始peak
            restored[i] = original_peak
        elif embedded_value < original_peak - 1: # 嵌入後的像素值如果小於peak-1，則還原為原始peak+1
            restored[i] = embedded_value + 1

    return restored.reshape(Y_channel_embedded.shape) #將嵌入後的Ｙ通道復原


if __name__ == '__main__':
    # 1. 讀取嵌入影像
    embedded_img = cv2.imread('France_embedded.png') # 這是嵌入後的影像
    if embedded_img is None:
        print("錯誤：找不到嵌入影像 'France_embedded.png'，請確認路徑。")
        exit()

    # 確保影像為 3 通道 (彩色)
    if len(embedded_img.shape) != 3:
         print("錯誤：讀取的嵌入影像不是彩色影像。")
         exit()

    # 2. 擷取 Y 通道
    img_ycrcb = cv2.cvtColor(embedded_img, cv2.COLOR_BGR2YCrCb)
    Y_channel_embedded = img_ycrcb[:, :, 0]

    # 確保 Y 通道是 uint8
    if Y_channel_embedded.dtype != np.uint8:
         Y_channel_embedded = Y_channel_embedded.astype(np.uint8)
         print("Warning: Converting embedded Y channel to uint8.")

    # 3. 取得嵌入時使用的原始 Peak 值 (需要使用者提供)
    # 這是這個方法的限制，需要知道原始 Peak 值才能開始提取
    try:
        original_peak_input = int(input("請輸入嵌入時使用的原始 Peak 值 (整數): "))
        if not (0 <= original_peak_input <= 255):
             raise ValueError("Peak 值必須在 0 到 255 之間。")
        original_peak = original_peak_input
        print(f"使用提供的原始 Peak 值 = {original_peak}")
    except ValueError as e:
        print(f"無效的輸入：{e}")
        exit()


    # 4. 提取前 8 位元 (Peak 值)
    print("嘗試提取前 8 位元 (Peak 值)...")
    # 這裡我們需要呼叫 extract_bits_from_Y，指定要提取 8 個位元
    # 這個函數會掃描整個影像，直到找到 8 個符合 Peak/Peak-1 條件的像素
    peak_bits = extract_bits_from_Y(Y_channel_embedded, original_peak, 8) # 提取 8 位元，為了獲得 Peak 值

    if len(peak_bits) < 8:
        print(f"錯誤：未能提取完整的 8 位元 Peak 值。只提取到 {len(peak_bits)} 位元。提供的 Peak 值可能不正確或影像已損壞。")
        exit()

    try:
        extracted_peak = int(peak_bits, 2)
        print(f"從影像中提取的 Peak 值 = {extracted_peak}")
    except ValueError:
        print(f"錯誤：無法將提取的 Peak 位元 '{peak_bits}' 轉換為整數。資料可能已損壞。")
        exit()

    # 驗證提取的 Peak 值與提供的 Peak 值是否一致
    if extracted_peak != original_peak:
        print(f"警告：提取的 Peak 值 ({extracted_peak}) 與您提供的原始 Peak 值 ({original_peak}) 不符！提取結果可能不正確。")
        # 你可以選擇在這裡退出，或者繼續使用提供的 original_peak (如果信任它) 或提取的 extracted_peak (如果信任影像資料)。
        # 為了安全性，如果它們不匹配，通常應該停止。這裡我們繼續，但發出警告。


    # 5. 提取接下來的 16 位元 (訊息長度前綴)，為了獲得訊息長度（16）
    print("嘗試提取接下來的 16 位元 (訊息長度)...")
    # 現在我們要提取總共 8 (Peak) + 16 (Length) = 24 個位元
    # extract_bits_from_Y 會再次從頭掃描，但這次會提取前 24 個符合條件的位元
    peak_and_length_bits = extract_bits_from_Y(Y_channel_embedded, original_peak, 8 + 16)

    if len(peak_and_length_bits) < 24:
         print(f"錯誤：未能提取完整的 24 位元 (Peak+Length)。只提取到 {len(peak_and_length_bits)} 位元。提供的 Peak 值可能不正確或影像已損壞。")
         exit()

    length_prefix_bits = peak_and_length_bits[8:24] # 取第 8 到 23 位元 (共 16 個)

    try:
        message_length = int(length_prefix_bits, 2)
        print(f"從長度前綴讀取的訊息長度（bits）= {message_length}")
    except ValueError:
         print(f"錯誤：無法將提取的長度位元 '{length_prefix_bits}' 轉換為整數。資料可能已損壞。")
         exit()


    # 6. 提取完整的資料 (Peak + 長度前綴 + 訊息位元)
    total_bits_to_extract = 8 + 16 + message_length
    print(f"嘗試提取完整的 {total_bits_to_extract} 位元資料 (Peak + Length + Message)...")
    # 提取所有需要的位元（訊息）
    full_bits = extract_bits_from_Y(Y_channel_embedded, original_peak, total_bits_to_extract)

    if len(full_bits) < total_bits_to_extract:
        print(f"錯誤：未能提取完整的 {total_bits_to_extract} 位元資料。只提取到 {len(full_bits)} 位元。提供的 Peak 值可能不正確或影像已損壞。訊息可能不完整。")
        # 嘗試還原部分影像並根據提取到的位元解碼部分訊息 (如果夠長)
        message_bits = full_bits[24:] # 即使不完整也嘗試取訊息部分
        if len(message_bits) > 0:
             message = bits_to_string(message_bits)
             print(f"嘗試還原的部分訊息：{message}")
        else:
             print("未能提取到任何訊息位元。")

        restored_Y = restore_Y_channel(Y_channel_embedded, original_peak) # 使用提供的 original_peak 來還原
        restored_Y = np.clip(restored_Y, 0, 255).astype(np.uint8)
        Cr = img_ycrcb[:, :, 1]
        Cb = img_ycrcb[:, :, 2]
        if restored_Y.shape == Cr.shape and restored_Y.shape == Cb.shape:
             restored_ycrcb = cv2.merge([restored_Y, Cr, Cb])
             restored_img = cv2.cvtColor(restored_ycrcb, cv2.COLOR_YCrCb2BGR)
             cv2.imwrite('restored_image_partial.png', restored_img)
             print("已儲存部分還原影像為 restored_image_partial.png")
        else:
             print("通道形狀不一致，無法儲存部分還原影像。")

        exit() # 提取失敗，終止程式


    # 提取訊息位元 (跳過 Peak 和長度前綴)
    message_bits = full_bits[24:]
    message = bits_to_string(message_bits)
    print(f"還原出的訊息：{message}")

    # 7. 還原影像（將 Y 通道的嵌入值還原回原始值）
    # 使用提供的 original_peak 來還原影像
    restored_Y = restore_Y_channel(Y_channel_embedded, original_peak)
    restored_Y = np.clip(restored_Y, 0, 255).astype(np.uint8)  # clip + 轉型以確保範圍和型別

    # 檢查 Cr, Cb 通道形狀是否一致
    Cr = img_ycrcb[:, :, 1]
    Cb = img_ycrcb[:, :, 2]

    if restored_Y.shape != Cr.shape or restored_Y.shape != Cb.shape:
        print("錯誤：還原後的 Y 通道與 Cr/Cb 通道形狀不一致！無法合併。")
        print(f"Y: {restored_Y.shape}, Cr: {Cr.shape}, Cb: {Cb.shape}")
        exit()

    # 合併回 YCrCb 並轉回 BGR
    restored_ycrcb = cv2.merge([restored_Y, Cr, Cb])
    restored_img = cv2.cvtColor(restored_ycrcb, cv2.COLOR_YCrCb2BGR)

    # 儲存還原影像
    cv2.imwrite('image.png', restored_img)
    print("已儲存還原影像為 image.png")

    # 8. 顯示直方圖（嵌入後、還原後）
    hist_embedded = cv2.calcHist([Y_channel_embedded], [0], None, [256], [0, 256])
    hist_restored = cv2.calcHist([restored_Y], [0], None, [256], [0, 256])

    plt.figure(figsize=(14, 6))

    plt.subplot(1, 2, 1)
    plt.plot(hist_embedded, label='Embedded Y Histogram', color='red')
    plt.title('Embedded Y Channel Histogram (for Extraction)')
    plt.xlabel('Pixel Value')
    plt.ylabel('Count')
    plt.legend()
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(hist_restored, label='Restored Y Histogram', color='blue')
    plt.title('Restored Y Channel Histogram')
    plt.xlabel('Pixel Value')
    plt.ylabel('Count')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()