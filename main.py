import pdfplumber
import os
import tkinter as tk
import pyttsx3
from queue import Queue  #for task queue
import threading
from tkinter import filedialog #for browse
import keras_ocr
from PIL import Image
import numpy as np

# Initialize the pipeline
pipeline=keras_ocr.pipeline.Pipeline()

def browse_file(entry):
    filepath=filedialog.askopenfilename(title="Select a file",filetypes=(("Pdf File","*.pdf"),("Text Files","*.txt,*"),
                                ("Image Files","*.jpg;*.jpeg;*.png;*.bmp;*.tiff"),
                                ("Doc File","*.docx"),
                                ("All Files","*.*")))
    if filepath:
        entry.delete(0,tk.END)
        entry.insert(0,filepath)
        
def convert_to_audio(text, output_filename):
    try:
        engine = pyttsx3.init() #initialize pyttsx engine(text to speech)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id if len(voices)>1 else voices[0].id)
        engine.setProperty('rate', 150)
        engine.save_to_file(text, output_filename + '.mp3')
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        raise Exception(f"Error occurred while Converting to Error: {str(e)}")
    finally:
        engine.stop()

def clean_ocr_words(words):
    cleaned=[]
    for w in words:
        if isinstance(w,str) and w.strip() and not w.replace('.',' ',1).isdigit():
            cleaned.append(w.strip())
    return cleaned

def extract_text_keras_ocr_from_image(pil_image):
    try:
        img_arr=np.array(pil_image.convert("RGB"))
        prediction_groups=pipeline.recognize([img_arr])
        print('prediction: ',prediction_groups)
        words=[word for word,box in prediction_groups[0]]
        print('prediction[0]: ',prediction_groups[0])
        print('words ',words)
        return " ".join(clean_ocr_words(words)).strip()
    except Exception as e:
        raise Exception(f"keras_ocr error:{e}")

def extract_text_keras_ocr_from_path(image_path):
    try:
        img=keras_ocr.tools.read(image_path)
        prediction_groups=pipeline.recognize([img])
        print('prediction: ',prediction_groups)
        words=[word for word,box in prediction_groups[0]]
        print('prediction[0]: ',prediction_groups[0])
        print('words ',words)
        return " ".join(clean_ocr_words(words)).strip()
    except Exception as e:
        raise Exception(f"Keras-OCR error {image_path}:{e}")

def extract_text_from_pdf_or_image(filepath,start_page=1,end_page=None,task_queue=None):
    ext = os.path.splitext(filepath)[1].lower()
    extracted=[]
    try:
        if ext==".pdf":
            task_queue and task_queue.put("Opening PDF...")
            with pdfplumber.open(filepath) as pdf:
                total_pages=len(pdf.pages)
                if end_page is None or end_page>total_pages:
                    end_page=total_pages
                for p in range(start_page,end_page+1):
                    task_queue and task_queue.put(f"Processing page {p}/{end_page}...")
                    page=pdf.pages[p-1]
                    text=page.extract_text()
                    if text and text.strip():
                        extracted.append(text)
                    else:
                        try:
                            page_image=page.to_image(resolution=2000).original
                        except Exception:
                           page_image=page.to_image().original 
                        ocr_text=extract_text_keras_ocr_from_image(page_image)
                        extracted.append(ocr_text)
        elif ext in ['.jpg','.jpeg','.png','.bmp','.tiff']:
            task_queue and task_queue.put("Extracting text from image via Keras OCR")
            ocr_text=extract_text_keras_ocr_from_path(filepath)
            extracted.append(ocr_text)
        elif ext==".txt":
            task_queue and task_queue.put("Reading text file...")
            with open(filepath,"r", encoding="utf-8",errors="ignore") as f:
                extracted.append(f.read())
        else:
            raise ValueError("Unsupported file type.Use PDF, image, or Txt")
        combined="\n\n".join([t for t in extracted if t and t.strip()])
        return combined
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except Exception as e:
        raise Exception(f"Error extracting text: {e}")
    
def converter(book_path, start_page, end_page, audio_path, task_queue,status_label):
    try:
        #error handling
        if not all([book_path,audio_path]):
            raise ValueError("Please enter book_path and audio_path")
        ext=os.path.splitext(book_path)[1].lower()
        if ext=='.pdf':
            if not start_page and not end_page:
                raise ValueError("Please enter start and end page no")
            if not (start_page.isdigit() and end_page.isdigit()):
                raise ValueError("Page No should be Number")    
            lowest = int(start_page)
            highest = int(end_page)
            if lowest > highest:
                raise ValueError("Start Page must be less than End Page")
        else:
            lowest,highest=1,1
        task_queue.put("Starting Extraction")
        text=extract_text_from_pdf_or_image(book_path,lowest,highest,task_queue=task_queue)
        if not text or not text.strip():
            raise ValueError("No text found in the Selected file/pages.")
        task_queue.put("Extracted text Successfully,Converting to audio...")
        convert_to_audio(text,audio_path)
        task_queue.put(f"Conversion Finished... Saved as: {audio_path}")
    except Exception as e:
        status_label.config(fg="red")
        task_queue.put(f"Error: {str(e)}")
        

def create_gui():
    root = tk.Tk()
    root.title("Vakta 2.0")
    root.geometry("900x600")
    root.config(bg="#1E1E2E")
    title=tk.Label(root,text="Vakta 2.0",font=("Times New Roman",42,"bold"),fg="#ffd700",bg="#1E1E2E" )
    title.pack(pady=40)
    
    frame=tk.Frame(root,bg="#1E1E2E")
    frame.pack(pady=10)
    
    tk.Label(frame, text="File Path:",font=("Segoe UI", 12,"bold","italic"),fg="white",bg="#1E1E2E").grid(row=0,column=0,padx=10,pady=10)
    book_entry = tk.Entry(frame, width=45,font=("Segoe UI",12),relief="flat",fg="#333333",bg="#F4F4F4",highlightthickness=2,highlightcolor="#ffd700",highlightbackground="#ffd700")
    book_entry.grid(row=0,column=1,padx=10,pady=10)
    tk.Button(frame,text='Browse',command=lambda:browse_file(book_entry),font=("Segoe UI",12,"bold"),fg="white",bg="#ffd700",relief="flat").grid(row=0,column=2,padx=10,pady=10)
    
    tk.Label(frame, text="Start Page(PDF only):",font=("Segoe UI",12,"bold","italic"),fg="white",bg="#1e1e2e").grid(row=1,column=0,padx=10,pady=10)
    start_entry = tk.Entry(frame, width=45,font=("Segoe UI",12),fg="#333333",bg="#F4F4F4",highlightthickness=2,highlightcolor="#ffd700",highlightbackground="#ffd700")
    start_entry.grid(padx=10,row=1,column=1,pady=10)

    tk.Label(frame, text="End Page(PDF only):",font=("Segoe UI",12,"bold","italic"),fg="white",bg="#1e1e2e").grid(padx=10,row=2,column=0,pady=10)
    end_entry = tk.Entry(frame, width=45,font=("Segoe UI",12),fg="#333333",bg="#F4F4F4",highlightthickness=2,highlightcolor="#ffd700",highlightbackground="#ffd700")
    end_entry.grid(padx=10,row=2,column=1,pady=10)

    tk.Label(frame, text="Audio File Name (no extension):",font=("Segoe UI",12,"bold","italic"),fg="white",bg="#1e1e2e").grid(padx=10,row=3,column=0,pady=10)
    audio_entry = tk.Entry(frame, width=45,font=("Segoe UI",12),fg="#333333",bg="#F4F4F4",highlightthickness=2,highlightcolor="#ffd700",highlightbackground="#ffd700")
    audio_entry.grid(padx=10,row=3,column=1,pady=10)

    status_label = tk.Label(frame, text="",font=("Segoe UI",12,"bold","italic"),fg="white",bg="#1e1e2e")
    status_label.grid(padx=10,row=4,column=0,columnspan=3,pady=10)

    task_queue = Queue()

    def start_conversion():
        status_label.config(text="Starting Conversion...")
        threading.Thread(target=converter,args=(book_entry.get(), start_entry.get(), end_entry.get(), audio_entry.get(),task_queue,status_label),daemon=True).start()
        

    convert_button = tk.Button(frame, text="Create AudioBook", command=start_conversion,font=("Segoe UI",12,"bold"),fg="white",bg="#ffd700",relief="flat")
    convert_button.grid(row=5,column=0,columnspan=3,pady=10,padx=10)

    def poll_queue():
        while not task_queue.empty():
            status = task_queue.get_nowait()
            status_label.config(text=status)
        root.after(200,poll_queue)
    poll_queue()
    root.mainloop()

if __name__ == "__main__":
    create_gui()
