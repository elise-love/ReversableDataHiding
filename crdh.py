# crdh.py
import cv2
import numpy as np

def find_original_peak_from_embedded(Y_channel_embedded):
    """
    Try to find the original peak from the embedded image by analyzing the histogram
    This is a heuristic approach - look for the most likely original peak
    """
    hist = cv2.calcHist([Y_channel_embedded], [0], None, [256], [0, 256])
    
    # Find peaks in the histogram (local maxima)
    potential_peaks = []
    for i in range(1, 255):
        if hist[i] > hist[i-1] and hist[i] > hist[i+1] and hist[i] > 10:  # threshold to avoid noise
            potential_peaks.append((i, int(hist[i][0])))
    
    # Sort by frequency (highest first)
    potential_peaks.sort(key=lambda x: x[1], reverse=True)
    
    # Return the most frequent peak as the likely original peak
    if potential_peaks:
        return potential_peaks[0][0]
    else:
        # Fallback to global maximum
        return int(np.argmax(hist))

def extract_bits_from_Y_robust(Y_channel_embedded, original_peak, total_bits_to_extract):
    """
    Robust bit extraction that handles edge cases better
    """
    bits = ''
    img_flat = Y_channel_embedded.flatten()
    extracted_count = 0
    
    # Count available pixels for extraction
    available_peak = np.sum(img_flat == original_peak)
    available_peak_minus_1 = np.sum(img_flat == original_peak - 1)
    total_available = available_peak + available_peak_minus_1
    
    print(f"[DEBUG] Available pixels: peak({original_peak})={available_peak}, peak-1({original_peak-1})={available_peak_minus_1}, total={total_available}")
    
    if total_available < total_bits_to_extract:
        print(f"警告：可用像素數 ({total_available}) 少於需要提取的位元數 ({total_bits_to_extract})")
    
    # Extract bits
    for i in range(len(img_flat)):
        if extracted_count >= total_bits_to_extract:
            break
        
        pixel_value = img_flat[i]
        if pixel_value == original_peak:
            bits += '0'
            extracted_count += 1
        elif pixel_value == original_peak - 1:
            bits += '1'
            extracted_count += 1
    
    print(f"[DEBUG] Extracted {len(bits)} bits out of {total_bits_to_extract} requested")
    return bits

def bits_to_string(bits):
    """將位元串轉回原始文字"""
    if not bits:
        return ""
    
    chars = []
    # Ensure we have complete bytes
    if len(bits) % 8 != 0:
        print(f"警告：提取的訊息位元數 ({len(bits)}) 不是 8 的倍數，截斷到最近的位元組。")
        bits = bits[:len(bits) - (len(bits) % 8)]
    
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) == 8:  # Ensure we have a complete byte
            try:
                char_code = int(byte, 2)
                if 32 <= char_code <= 126:  # Printable ASCII range
                    chars.append(chr(char_code))
                else:
                    # Handle non-printable characters
                    chars.append('?')
            except ValueError:
                print(f"警告：無法將位元串 '{byte}' 轉換為字元。")
                chars.append('?')
    
    return ''.join(chars)

def restore_Y_channel(Y_channel_embedded, original_peak):
    """根據原始 peak 將被修改過的像素值還原"""
    img_flat = Y_channel_embedded.flatten()
    restored = img_flat.copy()
    
    for i in range(len(restored)):
        embedded_value = img_flat[i]
        if embedded_value == original_peak:
            # This pixel was originally peak and contained data bit '0'
            pass  # Keep as is
        elif embedded_value == original_peak - 1:
            # This pixel was originally peak and contained data bit '1'
            restored[i] = original_peak
        elif embedded_value < original_peak - 1:
            # This pixel was shifted down during embedding
            restored[i] = embedded_value + 1
    
    return restored.reshape(Y_channel_embedded.shape)

def decode_image(img_color, manual_peak=None):
    """
    Improved decoding function with better error handling
    """
    logs = []

    try:
        img_ycrcb = cv2.cvtColor(img_color, cv2.COLOR_BGR2YCrCb)
        Y_channel_embedded = img_ycrcb[:, :, 0]

        # Try multiple approaches to find the original peak
        hist_embedded = cv2.calcHist([Y_channel_embedded], [0], None, [256], [0, 256])

        # NEW: Use manual_peak if provided
        if manual_peak is not None:
            estimated_peak = manual_peak
            log_msg = f"使用手動輸入的 peak: {estimated_peak}"
            print(log_msg)
            logs.append(log_msg)
        else:
            # Approach 1: Use histogram analysis to find likely original peak
            estimated_peak = find_original_peak_from_embedded(Y_channel_embedded)
            log_msg = f"估計的原始 peak: {estimated_peak}"
            print(log_msg)
            logs.append(log_msg)

        # Try to extract header with estimated peak
        total_header_bits = 24  # 8 bits peak + 16 bits length
        header_bits = extract_bits_from_Y_robust(
            Y_channel_embedded,
            original_peak=estimated_peak,
            total_bits_to_extract=total_header_bits
        )

        if len(header_bits) < 24:
            # Try with the global maximum as fallback
            fallback_peak = int(np.argmax(hist_embedded))
            log_msg = f"使用備用 peak: {fallback_peak}"
            print(log_msg)
            logs.append(log_msg)

            header_bits = extract_bits_from_Y_robust(
                Y_channel_embedded,
                original_peak=fallback_peak,
                total_bits_to_extract=total_header_bits
            )
            estimated_peak = fallback_peak

        if len(header_bits) < 24:
            return None, f"錯誤：無法提取完整的 Header。只提取到 {len(header_bits)} 位元，需要 24 位元。"

        # Parse header
        peak_bits = header_bits[:8]
        length_bits = header_bits[8:24]

        extracted_peak = int(peak_bits, 2)
        message_length = int(length_bits, 2)

        log_msg = f"從 Header 解析：Peak = {extracted_peak}, 訊息長度 = {message_length} bits"
        print(log_msg)
        logs.append(log_msg)

        # Validate extracted values
        if extracted_peak < 0 or extracted_peak > 255:
            return None, f"錯誤：提取到的 Peak 值 ({extracted_peak}) 超出有效範圍 [0-255]"

        if message_length <= 0 or message_length > 100000:  # Reasonable upper limit
            return None, f"錯誤：提取到的訊息長度 ({message_length}) 不合理"

        # Extract full data using the correct peak from header
        total_bits_to_extract = 24 + message_length
        full_bits = extract_bits_from_Y_robust(
            Y_channel_embedded,
            original_peak=extracted_peak,
            total_bits_to_extract=total_bits_to_extract
        )

        if len(full_bits) < total_bits_to_extract:
            # Try partial extraction
            if len(full_bits) >= 24:
                message_bits = full_bits[24:]
                log_msg = f"警告：只能提取部分資料 ({len(message_bits)} bits)，嘗試解碼..."
                print(log_msg)
                logs.append(log_msg)
            else:
                return None, f"錯誤：無法提取足夠的資料位元。需要 {total_bits_to_extract}，只得到 {len(full_bits)}"
        else:
            message_bits = full_bits[24:24+message_length]

        # Decode message
        message = bits_to_string(message_bits)
        log_msg = f"解碼訊息: '{message}'"
        print(log_msg)

        # Restore image
        restored_Y = restore_Y_channel(Y_channel_embedded, extracted_peak)
        restored_Y = np.clip(restored_Y, 0, 255).astype(np.uint8)

        Cr = img_ycrcb[:, :, 1]
        Cb = img_ycrcb[:, :, 2]
        restored_ycrcb = cv2.merge([restored_Y, Cr, Cb])
        restored_img = cv2.cvtColor(restored_ycrcb, cv2.COLOR_YCrCb2BGR)

        hist_restored = cv2.calcHist([restored_Y], [0], None, [256], [0, 256])

        return {
            'message': message,
            'restored_img': restored_img,
            'hist_embedded': hist_embedded,
            'hist_restored': hist_restored,
            'extracted_peak': extracted_peak,
            'logs': logs
        }, None

    except Exception as e:
        error_msg = f"解碼過程中發生錯誤: {str(e)}"
        print(error_msg)
        return None, error_msg
