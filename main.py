import pdfplumber
import tkinter as tk
import pyttsx3
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
    task_queue.put((total,time.time()-start_time))

def  vakta(text,output_filename,status_label):
    engine=pyttsx3.init()
    voices=engine.getProperty('voices')
    engine.setProperty('voice',voices[0].id)
    engine.setProperty('rate',150)
    def finished_call(status):
        if status:
            estimated_minutes=estimate_time(text)
            estimated_minutes_str=f"{estimated_minutes: .2f}"
            status_label.config(text=f"Conversion Successful (Estimated Time : {estimated_minutes_str} minutes)",fg='green',pady=5)
    engine.save_to_file(text,output_filename+'.mp3')
    engine.runAndWait()
    engine.stop()
    finished_call(True)

def converter(book_path,start_entry,end_entry,audio_path,status_label,task_queue):
    try:
        lowest=int(start_entry)
        highest=int(end_entry)
        
        if lowest>highest:
            raise ValueError("Start Page must be less than End Page")
        
        extraction_thread=threading.Thread(target=extraction,args=(book_path,lowest,highest,task_queue))
        extraction_thread.start()
        extraction_thread.join()
        
        extracted_text,_=task_queue.get()
        
        vakta_thread=threading.Thread(target=vakta, args=(extracted_text,audio_path,status_label))
        vakta_thread.start()
    
    except ValueError as e:
        status_label.config(text=f"Error: {str(e)}", fg="red")
        
    except Exception as e:
        status_label.config(text="Error: Page numbers must be integers", fg="red")
        
def gui():
    root=tk.Tk()
    root.title("Vakta")
    tk.Label(root, text="Book Path:").pack()
    book_entry= tk.Entry(root, width=50)
    book_entry.pack()
    
    tk.Label(root, text="Start Page:").pack()
    start_entry = tk.Entry(root, width=10)
    start_entry.pack()
    
    tk.Label(root, text="End Page:").pack()
    end_entry = tk.Entry(root, width=10)
    end_entry.pack()
    
    tk.Label(root,text="Audio File Name:").pack()
    audio_entry=tk.Entry(root,width=50)
    audio_entry.pack()
    
    status_label = tk.Label(root, text="")
    status_label.pack()
    
    task_queue=queue.Queue()
    
    convert_button=tk.Button(root,text="Create AudioBook",command=lambda: converter(book_entry.get(),start_entry.get(),end_entry.get(),audio_entry.get(),status_label,task_queue))
    convert_button.pack()
    
    root.mainloop()
    
gui()
