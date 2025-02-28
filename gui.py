import tkinter as tk
from tkinter import messagebox
import threading
import backend.mydblp as mydblp  # importing the existing crawler module

def run_crawl(confs_str, keywords_str):
    # Convert comma-separated strings into lists
    confs = [c.strip() for c in confs_str.split(",") if c.strip()]
    keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]
    # Override global parameters in mydblp
    mydblp.CONFS = confs
    mydblp.keywords = keywords

    paper_list = []
    for conf in mydblp.CONFS:
        paper_list += mydblp.searchConference(conf, mydblp.keywords)
    if paper_list:
        mydblp.savePaper2csv(paper_list, mydblp.FILE_NAME)
    messagebox.showinfo("Done", f"Found {len(paper_list)} papers.\nData saved to {mydblp.FILE_NAME}")

def start_crawl():
    # Start crawl in a new thread to avoid blocking GUI
    thread = threading.Thread(target=run_crawl, args=(confs_entry.get(), keywords_entry.get()))
    thread.start()

# GUI setup
root = tk.Tk()
root.title("DBLP Crawler GUI")

# Conference Input
tk.Label(root, text="Conferences (comma-separated):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
confs_entry = tk.Entry(root, width=50)
confs_entry.grid(row=0, column=1, padx=5, pady=5)
confs_entry.insert(0, ", ".join(mydblp.CONFS))  # default value

# Keywords Input
tk.Label(root, text="Keywords (comma-separated):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
keywords_entry = tk.Entry(root, width=50)
keywords_entry.grid(row=1, column=1, padx=5, pady=5)
keywords_entry.insert(0, ", ".join(mydblp.keywords))  # default value

# Start Button
start_button = tk.Button(root, text="Start Crawl", command=start_crawl)
start_button.grid(row=2, column=0, columnspan=2, pady=10)

# ...existing code (optional GUI enhancements)...

root.mainloop()
