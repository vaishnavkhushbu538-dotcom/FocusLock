import tkinter as tk
from tkinter import messagebox
import psutil
import threading
import time

running = False
time_limit = 0
used_time = 0
selected_apps = []

# ❌ Ignore system apps
IGNORE_APPS = [
    "System Idle Process", "System", "explorer.exe",
    "svchost.exe", "SearchApp.exe", "RuntimeBroker.exe"
]

# 🔍 Load apps
def load_apps():
    apps = []
    for proc in psutil.process_iter(['name']):
        try:
            name = proc.info['name']
            if name and name not in apps and name not in IGNORE_APPS:
                apps.append(name)
        except:
            pass
    
    listbox.delete(0, tk.END)
    for app in sorted(apps):
        listbox.insert(tk.END, app)

# ▶️ Start
def start_timer():
    global running, time_limit, used_time, selected_apps

    try:
        time_limit = int(entry.get()) * 60
    except:
        messagebox.showerror("Error", "Enter valid number")
        return

    selected_apps = [listbox.get(i) for i in listbox.curselection()]

    if not selected_apps:
        messagebox.showwarning("Warning", "Select at least one app")
        return

    used_time = 0
    running = True

    threading.Thread(target=track_usage, daemon=True).start()
    status_label.config(text="Status: Running 🔥")

# ⏱️ Track usage
def track_usage():
    global used_time, running

    while running:
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] in selected_apps:
                    used_time += 1

                    time_left = max(0, (time_limit - used_time) // 60)

                    status_label.config(
                        text=f"Used: {used_time//60} min | Left: {time_left} min"
                    )

                    if used_time >= time_limit:
                        try:
                            proc.kill()
                        except:
                            pass

                        messagebox.showwarning("Time Over", "Apps are now locked!")
                        running = False
                        return
            except:
                pass

        time.sleep(1)

# 🎨 GUI
root = tk.Tk()
root.title("FocusLock Pro")
root.geometry("400x520")
root.configure(bg="#1e1e2f")

title = tk.Label(root, text="🔒 FocusLock", fg="white", bg="#1e1e2f",
                 font=("Arial", 18, "bold"))
title.pack(pady=10)

tk.Label(root, text="Enter Time (minutes):",
         fg="white", bg="#1e1e2f").pack()

entry = tk.Entry(root, justify="center")
entry.pack(pady=5)

tk.Button(root, text="Load Running Apps",
          command=load_apps,
          bg="#4CAF50", fg="white").pack(pady=5)

listbox = tk.Listbox(root, selectmode=tk.MULTIPLE,
                     height=12, bg="#2b2b3c", fg="white")
listbox.pack(pady=10, fill="both", expand=True)

tk.Button(root, text="Start Focus",
          command=start_timer,
          bg="#2196F3", fg="white").pack(pady=10)

status_label = tk.Label(root, text="Status: Idle",
                        fg="white", bg="#1e1e2f")
status_label.pack(pady=10)

root.mainloop()
