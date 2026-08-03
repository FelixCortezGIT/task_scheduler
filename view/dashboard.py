import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class Dashboard(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        style = ttk.Style()
        style.theme_use("clam")

        button_frame = ttk.Frame(self)
        button_frame.pack(side="top", fill="x", padx=5, pady=5)

        self.current_view = "work"

        add_btn = ttk.Button(button_frame, text="add new", command=self.open_add_form)
        add_btn.pack(side="left", padx=(0, 2))

        work_btn = ttk.Button(button_frame, text="work mode", command=self.show_work_mode)
        work_btn.pack(side="left", padx=2)

        show_all_btn = ttk.Button(button_frame, text="show all", command=self.show_all_tasks)
        show_all_btn.pack(side="left", padx=2)

        self.tree = ttk.Treeview(
            self,
            columns=("id", "name", "description", "created_at", "updated_at", "status", "priority", "deadline"),
            show="headings"
        )

        self.tree.tag_configure("active", background="#FFEB3B")    # žltá
        self.tree.tag_configure("on_hold", background="#99D8D8")   # svetlomodrá
        self.tree.tag_configure("closed", background="#D9D9D9")    # sivá

        self.column_config = {
            "id":          {"width": 40,  "anchor": "center"},
            "name":        {"width": 130, "anchor": "w"},
            "description": {"width": 200, "anchor": "w"},
            "created_at":  {"width": 130, "anchor": "center"},
            "updated_at":  {"width": 130, "anchor": "center"},
            "status":      {"width": 80,  "anchor": "center"},
            "priority":    {"width": 80,  "anchor": "center"},
            "deadline":    {"width": 130, "anchor": "center"},
        }

        self.sort_column = None
        self.sort_reverse = False

        for col, cfg in self.column_config.items():
            self.tree.heading(col, text=col.capitalize(), command=lambda c=col: self.sort_by(c))
            self.tree.column(col, width=cfg["width"], anchor=cfg["anchor"])

        self.tree.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        self.tree.bind("<Double-1>", self.open_edit_form)
        self.tree.bind("<Delete>", self.delete_selected)

        self.refresh()

    def show_work_mode(self):
        self.current_view = "work"
        self.refresh()

    def show_all_tasks(self):
        self.current_view = "all"
        self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if self.current_view == "all":
            tasks = self.controller.list_tasks(show_all=True)
        else:
            tasks = self.controller.list_tasks()

        for task in tasks:
            task_id, name, description, status, priority, deadline, created_at, updated_at = task
            self.tree.insert("", "end", values=(
                task_id, name, description or "-", created_at, updated_at, status, priority, deadline or "-"
            ), tags=(status,))

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
        task_id, name, description, created_at, updated_at, status, priority, deadline = values

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

    def sort_by(self, col):
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False

        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]

        def sort_key(item):
            value = item[0]
            return (value is None or value in ("", "-"), value)

        items.sort(key=sort_key, reverse=self.sort_reverse)

        for index, (_, k) in enumerate(items):
            self.tree.move(k, "", index)

        for c in self.column_config:
            arrow = ""
            if c == self.sort_column:
                arrow = " ▲" if not self.sort_reverse else " ▼"
            self.tree.heading(c, text=c.capitalize() + arrow)

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
