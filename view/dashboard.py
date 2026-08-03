import tkinter as tk
from tkinter import ttk

class Dashboard(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.tree = ttk.Treeview(
            self,
            columns=("id", "name", "description", "status", "priority", "deadline"),
            show="headings"
        )

        column_config = {
            "id":          {"width": 40,  "anchor": "center"},
            "name":        {"width": 180, "anchor": "w"},
            "description": {"width": 320, "anchor": "w"},
            "status":      {"width": 80,  "anchor": "center"},
            "priority":    {"width": 80,  "anchor": "center"},
            "deadline":    {"width": 140, "anchor": "center"},
        }

        for col, cfg in column_config.items():
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=cfg["width"], anchor=cfg["anchor"])

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        refresh_btn = ttk.Button(self, text="Refresh", command=self.refresh)
        refresh_btn.pack(pady=(0, 10))

        self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        tasks = self.controller.list_tasks()
        for task in tasks:
            task_id, name, description, status, priority, deadline, *_ = task
            self.tree.insert("", "end", values=(
                task_id, name, description or "-", status, priority, deadline or "-"
            ))
