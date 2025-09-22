import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import schedule
import time
import threading
from datetime import datetime

# Categories mapping
FILE_CATEGORIES = {
    "Images": [".jpg", ".png", ".gif"],
    "Videos": [".mp4", ".mkv", ".avi"],
    "Documents": [".pdf", ".docx", ".txt"],
    "Music": [".mp3", ".wav"]
}

log_file = "log.txt"
selected_folder = ""

# Function to organize files
def organize_files():
    global selected_folder
    if not selected_folder:
        messagebox.showerror("Error", "Please select a folder first")
        return

    moved_files = []
    for file_name in os.listdir(selected_folder):
        file_path = os.path.join(selected_folder, file_name)
        if os.path.isfile(file_path):
            ext = os.path.splitext(file_name)[1].lower()
            moved = False

            # Check category
            for category, extensions in FILE_CATEGORIES.items():
                if ext in extensions:
                    category_path = os.path.join(selected_folder, category)
                    os.makedirs(category_path, exist_ok=True)
                    new_path = os.path.join(category_path, file_name)
                    shutil.move(file_path, new_path)
                    moved_files.append((file_path, new_path))
                    moved = True
                    break

            # If no category found → Others
            if not moved:
                other_path = os.path.join(selected_folder, "Others")
                os.makedirs(other_path, exist_ok=True)
                new_path = os.path.join(other_path, file_name)
                shutil.move(file_path, new_path)
                moved_files.append((file_path, new_path))

    # Log the moves
    with open(log_file, "a") as f:
        for old, new in moved_files:
            f.write(f"{datetime.now()} | MOVED | {old} --> {new}\n")

    messagebox.showinfo("Success", "Files organized successfully!")

# Undo function
def undo_last_action():
    if not os.path.exists(log_file):
        messagebox.showerror("Error", "No log file found!")
        return

    undone = []
    with open(log_file, "r") as f:
        lines = f.readlines()

    with open(log_file, "w") as f:
        for line in lines:
            if "MOVED" in line:
                parts = line.strip().split(" | ")
                old_new = parts[-1].split(" --> ")
                old, new = old_new[0], old_new[1]
                if os.path.exists(new):
                    shutil.move(new, old)
                    undone.append((new, old))
                # Skip writing this line (removes from log)
            else:
                f.write(line)

    if undone:
        messagebox.showinfo("Undo", "Last action undone successfully!")
    else:
        messagebox.showinfo("Undo", "Nothing to undo!")

# Scheduler worker
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Select folder
def browse_folder():
    global selected_folder
    selected_folder = filedialog.askdirectory()
    if selected_folder:
        folder_label.config(text=f"Selected: {selected_folder}")

# Schedule every X minutes
def schedule_task():
    try:
        minutes = int(schedule_entry.get())
        schedule.clear()
        schedule.every(minutes).minutes.do(organize_files)
        messagebox.showinfo("Scheduled", f"Organizer will run every {minutes} minutes!")
    except ValueError:
        messagebox.showerror("Error", "Enter a valid number of minutes")

# GUI setup
root = tk.Tk()
root.title("File Organizer with Automation")
root.geometry("500x300")

tk.Label(root, text="File Organizer", font=("Arial", 16, "bold")).pack(pady=10)

folder_label = tk.Label(root, text="No folder selected", fg="blue")
folder_label.pack(pady=5)

tk.Button(root, text="Browse Folder", command=browse_folder).pack(pady=5)
tk.Button(root, text="Organize Now", command=organize_files).pack(pady=5)
tk.Button(root, text="Undo Last Action", command=undo_last_action).pack(pady=5)

# Scheduling part
tk.Label(root, text="Run automatically every (minutes):").pack(pady=5)
schedule_entry = tk.Entry(root)
schedule_entry.pack(pady=5)
tk.Button(root, text="Set Schedule", command=schedule_task).pack(pady=5)

# Start scheduler thread
threading.Thread(target=run_scheduler, daemon=True).start()

root.mainloop()
