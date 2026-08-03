import tkinter as tk
from tkinter import ttk

def show_deadline_popup(parent, task):
    task_id, name, description, status, priority, deadline, *_ = task

    popup = tk.Toplevel(parent)
    popup.title("Deadline Reached")
    popup.attributes("-topmost", True)

    ttk.Label(popup, text="⚠ Deadline Reached", font=("", 12, "bold")).pack(padx=20, pady=(15, 5))
    ttk.Label(popup, text=name, font=("", 10, "bold")).pack(padx=20)
    ttk.Label(popup, text=f"Deadline: {deadline}").pack(padx=20, pady=(0, 10))
    ttk.Button(popup, text="OK", command=popup.destroy).pack(pady=(0, 15))
