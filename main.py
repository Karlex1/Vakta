import pdfplumber
import tkinter as tk
import pyttsx3
import concurrent.futures
import time
from queue import Queue
import threading

def estimate_time(text_length, speech_rate=150):
    words_per_minute = speech_rate / 60
    estimated_minutes = (len(text_length) / words_per_minute) + 0.5
    return round(estimated_minutes, 2)

def extract_text(filepath, lowest, highest):
    total = ''
    try:
        with pdfplumber.open(filepath) as pdf:
            for page_num in range(lowest, highest + 1):
                page = pdf.pages[page_num - 1]
                text = page.extract_text()
                total += text
        return total
    except FileNotFoundError:
        raise FileNotFoundError(f"File Not Found-{filepath}")
    except Exception as e:
        raise Exception(f"Error occurred while extracting text: {str(e)}")

def convert_to_audio(text, output_filename):
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 150)
        engine.save_to_file(text, output_filename + '.mp3')
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        raise Exception(f"Error occurred while Converting to Error: {str(e)}")

def converter(book_path, start_page, end_page, audio_path, status_label, task_queue):
    try:
        #error handling
        if not all([book_path,start_page,end_page,audio_path]):
            raise ValueError("Please enter all fields")
        if not (start_page.isdigit() and end_page.isdigit()):
            raise ValueError("Page No should be Number")    
        lowest = int(start_page)
        highest = int(end_page)
        if lowest > highest:
            raise ValueError("Start Page must be less than End Page")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            extracted_text = executor.submit(extract_text, book_path, lowest, highest)
            extracted_text = extracted_text.result()

            task_queue.put("Converting to audio...")
            convert_to_audio(extracted_text, audio_path)
            task_queue.put("Conversion successful.")

    except ValueError as e:
        task_queue.put(f"Error: {str(e)}")
    except FileNotFoundError as e:
        task_queue.put(f"Error: {str(e)}")
    except InvalidInputError as e:
        task_queue.put(f"Error: {str(e)}")
    except Exception as e:
        task_queue.put("Error: Conversion failed.")
        

def create_gui():
    root = tk.Tk()
    root.title("Vakta")

    tk.Label(root, text="Book Path:").pack()
    book_entry = tk.Entry(root, width=50)
    book_entry.pack()

    tk.Label(root, text="Start Page:").pack()
    start_entry = tk.Entry(root, width=10)
    start_entry.pack()

    tk.Label(root, text="End Page:").pack()
    end_entry = tk.Entry(root, width=10)
    end_entry.pack()

    tk.Label(root, text="Audio File Name:").pack()
    audio_entry = tk.Entry(root, width=50)
    audio_entry.pack()

    status_label = tk.Label(root, text="")
    status_label.pack()

    task_queue = Queue()

    def start_conversion():
        task_queue.put("Starting conversion...")
        executor = concurrent.futures.ThreadPoolExecutor()
        executor.submit(converter, book_entry.get(), start_entry.get(), end_entry.get(), audio_entry.get(), status_label, task_queue)

    convert_button = tk.Button(root, text="Create AudioBook", command=start_conversion)
    convert_button.pack()

    def update_status():
        while True:
            status = task_queue.get()
            status_label.config(text=status)
            root.update_idletasks()

    update_thread = threading.Thread(target=update_status, daemon=True)
    update_thread.start()

    root.mainloop()

if __name__ == "__main__":
    create_gui()
