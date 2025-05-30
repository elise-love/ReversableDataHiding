# rdh.py - Improved Version
import cv2
import numpy as np

def embed_data(grayscaleImg, data_bits, peak):
    """
    將資料位元嵌入灰階影像（改進版）
    """
    print(f"[DEBUG] Embedding {len(data_bits)} bits using peak {peak}")
    
    # Flatten and copy
    img_flat = grayscaleImg.flatten()
    embedded_img = img_flat.copy()
    
    # Count available pixels at peak for capacity check
    peak_pixels = np.sum(img_flat == peak)
    print(f"[DEBUG] Available peak pixels: {peak_pixels}")
    
    if peak_pixels < len(data_bits):
        print(f"警告：Peak 像素數 ({peak_pixels}) 少於要嵌入的位元數 ({len(data_bits)})")
        return embedded_img.reshape(grayscaleImg.shape), 0
    
    # Step 1: Shift pixels < peak down by 1 to make room
    shift_count = 0
    for i in range(len(embedded_img)):
        if embedded_img[i] < peak and embedded_img[i] > 0:  # Avoid going below 0
            embedded_img[i] -= 1
            shift_count += 1
    
    print(f"[DEBUG] Shifted {shift_count} pixels down")
    
    # Step 2: Embed data bits into peak pixels
    embedding_bit = 0
    embedded_count = 0
    
    for i in range(len(embedded_img)):
        if embedding_bit >= len(data_bits):
            break
            
        # Only embed in pixels that are still at peak value after shifting
        if img_flat[i] == peak:  # Use original image to identify peak pixels
            if data_bits[embedding_bit] == '1':
                embedded_img[i] = peak - 1  # Represent '1' as peak-1
            else:
                embedded_img[i] = peak      # Represent '0' as peak
            
            embedding_bit += 1
            embedded_count += 1
    
    print(f"[DEBUG] Successfully embedded {embedded_count} bits")
    
    # Ensure valid pixel values and reshape
    embedded_img = np.clip(embedded_img, 0, 255).reshape(grayscaleImg.shape)
    
    return embedded_img, embedding_bit

def embed_data_color(img_color, data_bits, peak):
    """
    將資料嵌入彩色影像（改進版）
    """
    print(f"[DEBUG] Color embedding: {len(data_bits)} bits, peak = {peak}")
    
    # Convert to YCrCb
    img_ycrcb = cv2.cvtColor(img_color, cv2.COLOR_BGR2YCrCb)
    Y, Cr, Cb = cv2.split(img_ycrcb)
    
    # Ensure correct data type
    if Y.dtype != np.uint8:
        Y = Y.astype(np.uint8)
    
    # Check histogram and capacity
    hist = cv2.calcHist([Y], [0], None, [256], [0, 256])
    capacity = int(hist[peak][0])
    print(f"[DEBUG] Peak {peak} has {capacity} pixels available")
    
    if len(data_bits) > capacity:
        print(f"錯誤：資料太大無法嵌入。需要 {len(data_bits)} bits，可用 {capacity} bits")
        return img_color, 0
    
    # Embed data
    embedded_Y, used_bits = embed_data(Y, data_bits, peak)
    embedded_Y = np.clip(embedded_Y, 0, 255).astype(np.uint8)
    
    # Merge channels and convert back
    embedded_ycrcb = cv2.merge([embedded_Y, Cr, Cb])
    embedded_color = cv2.cvtColor(embedded_ycrcb, cv2.COLOR_YCrCb2BGR)
    
    print(f"[DEBUG] Embedding completed: {used_bits} bits used")
    return embedded_color, used_bits

def analyze_image_for_embedding(img_path):
    """
    分析影像的嵌入能力
    """
    img = cv2.imread(img_path)
    if img is None:
        return None
    
    img_ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    Y = img_ycrcb[:, :, 0]
    
    hist = cv2.calcHist([Y], [0], None, [256], [0, 256])
    peak = int(np.argmax(hist))
    capacity = int(hist[peak][0])
    
    print(f"影像分析結果:")
    print(f"- Peak 值: {peak}")
    print(f"- Peak 像素數: {capacity}")
    print(f"- 最大可嵌入字元數: {capacity // 8}")
    
    return {
        'peak': peak,
        'capacity': capacity,
        'max_chars': capacity // 8
    }