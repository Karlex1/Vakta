from gtts import gTTS  
import pdfplumber
import tkinter as tk
import pyttsx3
import wave

def extraction(filepath,lowest,highest):
    with pdfplumber.open(filepath) as pdf:
        total=''
        for page_num in range(lowest,highest+1):
            page = pdf.pages[page_num - 1]
            text = page.extract_text()
            total+=text
        return total

def  vakta(text,output_filename):
    engine=pyttsx3.init()
    voices=engine.getProperty('voices')
    engine.setProperty('voice',voices[0].id)
    rate=engine.getProperty('rate')
    engine.setProperty('rate',150)
    engine.save_to_file(text,output_filename+'.wav')
    engine.runAndWait()

def converter(book_entry,start_entry,end_entry,audio_entry,status_label):
    book_path=book_entry
    try:
        lowest=int(start_entry)
        highest=int(end_entry)
        if lowest>highest:
            raise ValueError("Start Page must be less than End Page")
    except ValueError as e:
        status_label.config(text=f"Error: {str(e)}", fg="red")
    except Exception as e:
        status_label.config(text="Error: Page numbers must be integers", fg="red")
    audio_path = audio_entry
    try:
        book_text=extraction(book_path, lowest, highest)
        vakta(book_text,audio_path)
        status_label.config(text="Conversion successful!", fg="green")
    except FileNotFoundError:
        status_label.config(text=f"Error: File not found - {book_path}", fg="red")
    except pdfplumber.PDFSyntaxError:
        status_label.config(text=f"Error: Invalid PDF format - {book_path}", fg="red")
    except Exception as e:
        status_label.config(text=f"Error: {str(e)}", fg="red")
        
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
    convert_button=tk.Button(root,text="Create AudioBook",command=lambda: converter(book_entry.get(),start_entry.get(),end_entry.get(),audio_entry.get(),status_label))
    convert_button.pack()
    status_label = tk.Label(root, text="")
    status_label.pack()
    root.mainloop()
    
gui()
