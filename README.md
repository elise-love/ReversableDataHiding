# 🌸 Steganography: Tool to Hide Messages in Images 🌸

Welcome to this **Steganography Tool** (Spiderman themed): a PyQt5 application that lets you hide messages in images and reveal them later, all with a dash of style! 🌷✨

## 💖 Features

- **✨ Dual Modes**: Switch between modes by double-clicking the spiderman pic!
- **🌺 Encoding Mode**: Hide your secret text in an image, like tucking a love note in a secret desk.
- **🌸 Decoding Mode**: Reveal the hidden message and restore the image's purity.
- **✨ Dashboard Messages**: Every step you take is celebrated with a line-by-line animated log terminal.
- **✨ Seamless Mode Switching**: Double-click the icon to toggle between Encoding and Decoding modes — it's as fun as switching outfits!
- **✨ Histograms**: View the original and modified histograms of the Y channel, with charming color themes. The peak bar is golden colored.

## 🌷 How to Use

### Step 1️⃣ Start the App
Launch the app by running:
```bash
__init__.py
```

### Step 2️⃣ Encoding Mode
1. Select an image you love.
2. Enter the secret text you want to hide. *(Please use English for now!)*
3. Click **Run**, and watch the RDH magic unfold!
4. The embedded image is previewed, and the encoding stats (like peak, used bits) are shown in the dashboard.

### Step 3️⃣ Decoding Mode
1. Switch to decoding by double-clicking the Spiderman icon.
2. Select the image with the hidden message. *(Your previous encoded image will be there by default)*
3. Click **Run**, and see your message declassify!
4. The restored image and histograms are updated.

## 📁 Project Structure

```
Solution 'ReversableDataHiding'
├── Project 'ReversableDataHiding'
│   ├── icons/
│   │   ├── icon1.jpg
│   │   └── icon2.jpg
│   ├── tempFile/
│   ├── .gitignore
│   ├── crdh.py
│   ├── decodeWindow.py
│   ├── encodeWindow.py
│   ├── histogram_widget.py
│   ├── rdh.py
│   ├── README.md
│   └── __init__.py
```

## 🍬 Notes

- This project uses **OpenCV** for the behind-the-scenes wizardry 🎭
- Animations are done with `QTimer` and `QPropertyAnimation` for extra sparkle! ✨
- The generated images are stored in `tempFile/`
- No secrets are too small — try it out! 🔍

## 💌 A Gentle Thank You

Thank you for checking out this **Steganography Tool**. I hope you find it intriguing and useful! 🍃🌸

---

🕷️