# 🎧 Vakta 2.0 — Text to Audio Converter

### Overview  
**Vakta 2.0** is a lightweight and powerful **Text-to-Audio Converter** built with Python.  
It can take any **PDF, image, or text file** and turn it into an **audio file** — so you can listen to books, notes, or documents hands-free.  

The app features a clean graphical interface, automatic text extraction (even from scanned pages), and smooth background processing.

---

### ✨ What’s New in Version 2.0
- Resolving the problem for scanned books pdf by using OCR.
- 🧠 **OCR Support:** Reads text from scanned PDFs and images using `keras_ocr`  
- 🎨 **Modern GUI:** Built with `tkinter` in a dark theme  
- ⚡ **Threaded Processing:** Uses Python’s `threading` and `queue` to keep the GUI responsive while converting files  
- 🔊 **Improved Audio Engine:** Uses `pyttsx3` for clear and natural text-to-speech output  

---

### 🧰 Tech Stack

| Library | Purpose |
|----------|----------|
| **pdfplumber** | Extracts text from text-based PDFs |
| **keras_ocr** | Detects and reads text from scanned PDFs or images |
| **pyttsx3** | Converts text into an audio file |
| **tkinter** | Creates the graphical interface |
| **threading & queue** | Handles background tasks without freezing the GUI |

---

### ⚙️ Installation
You can set up Vakta 2.0 easily:

```bash
git clone https://github.com/yourusername/Vakta-2.0.git
cd Vakta-2.0
pip install pdfplumber pyttsx3 keras-ocr Pillow numpy
```

> 🧩 Note: The first time you run Vakta, `keras_ocr` may take a few minutes to download its models.

---

### 🚀 How It Works

#### 🧵 **Threading and Background Tasks**
Vakta 2.0 uses the **`threading`** module to handle conversions in a separate thread.  
This ensures that the GUI never freezes while reading large PDFs or converting audio.

When you click **“Create AudioBook”**, a new thread is started:
```python
threading.Thread(
    target=converter,
    args=(book_entry.get(), start_entry.get(), end_entry.get(), audio_entry.get(), task_queue),
    daemon=True
).start()
```

The **`Queue`** object (`task_queue`) is used to safely send status updates back to the main thread, which then updates the GUI labels using:
```python
root.after(200, poll_queue)
```
This pattern keeps GUI feel active like every thing is happening at frontend.

---

### 🚀 How to Use
1. Run the app:
   ```bash
   python vakta2.py
   ```
2. Choose a file (PDF, image, or text).  
3. For PDFs, enter start and end page numbers.  
4. Type a name for your audio file.  
5. Click **Create AudioBook**.  
   - The conversion runs in a background thread.  
   - You’ll see live status messages (e.g., *Processing page 3/10...*).  

Your audio (`.mp3`) file will be saved in the same folder.

---

### 🖼️ Example Interface
<img width="907" height="643" alt="Screenshot (167)" src="https://github.com/user-attachments/assets/6816ac36-5eb4-42fb-bf5f-4048fd5dac2a" />


---

### 📦 Output Example
```
Opening PDF...
Processing page 1/4...
Extracted text successfully, converting to audio...
✅ Conversion Finished: saved as output.mp3
```

---

### 💡 Future Ideas
- 🗣️ Selectable voices (male/female)
- 🎛️ Adjustable speech speed and pitch
- 📁 Output folder selection
- 📚 Batch file conversion

---

### 👨‍💻 About
**Vakta 2.0** was developed by *Karlex* to make reading easier and more accessible.  
It’s free, open-source, and designed to turn your reading material into an audiobook effortlessly.

**Version:** 2.0  
**License:** MIT  
