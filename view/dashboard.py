import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class Dashboard(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        button_frame = ttk.Frame(self)
        button_frame.pack(side="top", fill="x", padx=10, pady=10)

        refresh_btn = ttk.Button(button_frame, text="refresh", command=self.refresh)
        refresh_btn.pack(side="left", padx=(0, 5))

        add_btn = ttk.Button(button_frame, text="add Task", command=self.open_add_form)
        add_btn.pack(side="left", padx=5)

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
        self.tree.bind("<Double-1>", self.open_edit_form)
        self.tree.bind("<Delete>", self.delete_selected)

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

    def open_add_form(self):
        form = tk.Toplevel(self)
        form.title("Add Task")
        form.geometry("350x380")
        form.grab_set()  # will block interaction with main window until form is open

        ttk.Label(form, text="Name*").pack(anchor="w", padx=10, pady=(10, 0))
        name_entry = ttk.Entry(form, width=40)
        name_entry.pack(padx=10)

        ttk.Label(form, text="Description").pack(anchor="w", padx=10, pady=(10, 0))
        desc_entry = tk.Text(form, width=40, height=4)
        desc_entry.pack(padx=10)

        ttk.Label(form, text="Status*").pack(anchor="w", padx=10, pady=(10, 0))
        status_var = tk.StringVar(value="active")
        status_dropdown = ttk.Combobox(form, textvariable=status_var, values=["active", "on_hold", "closed"], state="readonly")
        status_dropdown.pack(padx=10)

        ttk.Label(form, text="Priority").pack(anchor="w", padx=10, pady=(10, 0))
        priority_var = tk.StringVar(value="medium")
        priority_dropdown = ttk.Combobox(form, textvariable=priority_var, values=["medium", "high"], state="readonly")
        priority_dropdown.pack(padx=10)

        ttk.Label(form, text="Deadline (YYYY-MM-DD HH:MM)").pack(anchor="w", padx=10, pady=(10, 0))
        deadline_entry = ttk.Entry(form, width=40)
        deadline_entry.pack(padx=10)

        error_label = ttk.Label(form, text="", foreground="red")
        error_label.pack(padx=10, pady=(5, 0))

        def submit():
            name = name_entry.get()
            description = desc_entry.get("1.0", "end").strip()
            status = status_var.get()
            priority = priority_var.get()
            deadline = deadline_entry.get().strip() or None

            try:
                self.controller.create_task(name, description, status, priority, deadline)
                form.destroy()
                self.refresh()
            except ValueError as e:
                error_label.config(text=str(e))

        submit_btn = ttk.Button(form, text="Confirm", command=submit)
        submit_btn.pack(pady=15)

    def open_edit_form(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        task_id, name, description, status, priority, deadline = values

        form = tk.Toplevel(self)
        form.title(f"Edit Task #{task_id}")
        form.geometry("350x380")
        form.grab_set()

        ttk.Label(form, text="Name*").pack(anchor="w", padx=10, pady=(10, 0))
        name_entry = ttk.Entry(form, width=40)
        name_entry.insert(0, name)
        name_entry.pack(padx=10)

        ttk.Label(form, text="Description").pack(anchor="w", padx=10, pady=(10, 0))
        desc_entry = tk.Text(form, width=40, height=4)
        desc_entry.insert("1.0", "" if description == "-" else description)
        desc_entry.pack(padx=10)

        ttk.Label(form, text="Status*").pack(anchor="w", padx=10, pady=(10, 0))
        status_var = tk.StringVar(value=status)
        status_dropdown = ttk.Combobox(form, textvariable=status_var, values=["active", "on_hold", "closed"], state="readonly")
        status_dropdown.pack(padx=10)

        ttk.Label(form, text="Priority").pack(anchor="w", padx=10, pady=(10, 0))
        priority_var = tk.StringVar(value=priority)
        priority_dropdown = ttk.Combobox(form, textvariable=priority_var, values=["medium", "high"], state="readonly")
        priority_dropdown.pack(padx=10)

        ttk.Label(form, text="Deadline (YYYY-MM-DD HH:MM)").pack(anchor="w", padx=10, pady=(10, 0))
        deadline_entry = ttk.Entry(form, width=40)
        deadline_entry.insert(0, "" if deadline == "-" else deadline)
        deadline_entry.pack(padx=10)

        error_label = ttk.Label(form, text="", foreground="red")
        error_label.pack(padx=10, pady=(5, 0))

        def submit():
            new_name = name_entry.get().strip()
            new_description = desc_entry.get("1.0", "end").strip()
            new_status = status_var.get()
            new_priority = priority_var.get()
            new_deadline = deadline_entry.get().strip() or None

            try:
                if new_name != name:
                    self.controller.edit_task(task_id, "name", new_name)
                if new_description != description:
                    self.controller.edit_task(task_id, "description", new_description)
                if new_status != status:
                    self.controller.edit_task(task_id, "status", new_status)
                if new_priority != priority:
                    self.controller.edit_task(task_id, "priority", new_priority)
                if new_deadline != (None if deadline == "-" else deadline):
                    self.controller.edit_task(task_id, "deadline", new_deadline)

                form.destroy()
                self.refresh()
            except ValueError as e:
                error_label.config(text=str(e))

        submit_btn = ttk.Button(form, text="confirm", command=submit)
        submit_btn.pack(pady=15)

    def delete_selected(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        task_id = values[0]

        confirm = messagebox.askyesno("confirm", f"delete task #{task_id}?")
        if confirm:
            self.controller.remove_task(task_id)
            self.refresh()
