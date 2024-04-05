import pdfplumber
import tkinter as tk
import pyttsx3
import wave
import threading
import queue
import time

def estimate_time(text_length,speech_rate=150):
    words_per_minute=speech_rate/60
    estimated_minutes=(len(text_length)/words_per_minute)+0.5
    return round(estimated_minutes, 2)

def extraction(filepath,lowest,highest,task_queue):
    start_time=time.time()
    total=''
    with pdfplumber.open(filepath) as pdf:
        for page_num in range(lowest,highest+1):
            page = pdf.pages[page_num - 1]
            text = page.extract_text()
            total+=text
    elapsed_time=time.time()-start_time
    estimated_minutes=estimate_time(total)
    task_queue.put((total,elapsed_time,estimated_minutes))

def  vakta(text,output_filename):
    engine=pyttsx3.init()
    voices=engine.getProperty('voices')
    engine.setProperty('voice',voices[0].id)
    rate=engine.getProperty('rate')
    engine.setProperty('rate',150)
    engine.save_to_file(text,output_filename+'.mp3')
    engine.runAndWait()

def converter(book_entry,start_entry,end_entry,audio_entry,status_label,task_queue):
    book_path=book_entry
    try:
        lowest=int(start_entry)
        highest=int(end_entry)
        
        if lowest>highest:
            raise ValueError("Start Page must be less than End Page")
        
        audio_path = audio_entry
        extraction_thread=threading.Thread(target=extraction,args=(book_path,lowest,highest,task_queue))
        extraction_thread.start()
        
        extracted_text,extraction_time,estimated_minutes=task_queue.get()
        
        vakta_thread=threading.Thread(target=vakta, args=(None,audio_path))
        # extraction_thread.join()
        vakta_thread.start()
        vakta_thread.join()
        
        total_time=extraction_time
        estimated_minutes_str = f"{estimated_minutes:.2f}"
        total_time_str = f"{total_time:.2f}"
        label_text=f"Conversion Successful!(Estimated time:{estimated_minutes_str} minutes, Total Time: {total_time_str}seconds)"
        status_label.config(text=label_text ,fg='green',pady=5)
    
    except ValueError as e:
        status_label.config(text=f"Error: {str(e)}", fg="red")
        
    except Exception as e:
        status_label.config(text="Error: Page numbers must be integers", fg="red")
        
def gui():
    root=tk.Tk()
    root.title("Vakta")
    book_label = tk.Label(root, text="Book Path:")
    book_label.pack()
    
    book_entry= tk.Entry(root, width=50)
    book_entry.pack()
    
    start_label = tk.Label(root, text="Start Page:")
    start_label.pack()
    
    start_entry = tk.Entry(root, width=10)
    start_entry.pack()
    
    end_label = tk.Label(root, text="End Page:")
    end_label.pack()
    
    end_entry = tk.Entry(root, width=10)
    end_entry.pack()
    
    audio_label=tk.Label(root,text="Audio File Name:")
    audio_label.pack()
    
    audio_entry=tk.Entry(root,width=50)
    audio_entry.pack()
    
    task_queue=queue.Queue()
    
    convert_button=tk.Button(root,text="Create AudioBook",command=lambda: converter(book_entry.get(),start_entry.get(),end_entry.get(),audio_entry.get(),status_label,task_queue))
    convert_button.pack()
    status_label = tk.Label(root, text="")
    status_label.pack()
    root.mainloop()
    
gui()
