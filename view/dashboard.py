import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

class Dashboard(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        style = ttk.Style()
        style.theme_use("sandstone")  # light themes: "flatly", "cosmo", "morph", "litera", "journal", "lumen"
        # light themes: "minty", "pulse", "sandstone", "united", "yeti", "simplex", "cerculean"
        # dark themes: "darkly", "cyborg", "superhero", "solar", "vapor"

        button_frame = ttk.Frame(self)
        button_frame.pack(side="top", fill="x", padx=5, pady=5)

        self.current_view = "work"

        add_btn = ttk.Button(button_frame, text="add new", command=self.open_add_form, bootstyle="success")
        add_btn.pack(side="left", padx=(0, 2))

        work_btn = ttk.Button(button_frame, text="work mode", command=self.show_work_mode, bootstyle="primary")
        work_btn.pack(side="left", padx=2)

        show_all_btn = ttk.Button(button_frame, text="show all", command=self.show_all_tasks, bootstyle="secondary")
        show_all_btn.pack(side="left", padx=2)

        self.tree = ttk.Treeview(
            self,
            columns=("id", "name", "description", "created_at", "updated_at", "status", "priority", "deadline"),
            show="headings",
            bootstyle="primary"
        )

        # ttkbootstrap themes have dark backgrounds, so pair each highlight
        # with a dark foreground to keep the text readable.
        self.tree.tag_configure("active", background="#FFEB3B", foreground="#1a1a1a")
        self.tree.tag_configure("on_hold", background="#99D8D8", foreground="#1a1a1a")
        self.tree.tag_configure("closed", background="#D9D9D9", foreground="#1a1a1a")

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

    def _themed_text_widget(self, parent, **kwargs):
        """tk.Text isn't a ttk widget, so ttkbootstrap can't theme it directly.
        Pull the current theme's colors so it doesn't look like a plain white
        box sitting inside a dark-themed form."""
        colors = ttk.Style().colors
        return tk.Text(
            parent,
            bg=colors.inputbg,
            fg=colors.inputfg,
            insertbackground=colors.inputfg,
            relief="flat",
            highlightthickness=1,
            highlightbackground=colors.border,
            **kwargs
        )

    def open_add_form(self):
        form = ttk.Toplevel(self)
        form.title("Add Task")
        form.geometry("560x250")
        form.grab_set()  # will block interaction with main window until form is open

        name_frame = ttk.Frame(form)
        name_frame.pack(fill="x", padx=10, pady=(10, 0))
        ttk.Label(name_frame, text="Name*", width=12).pack(side="left")
        name_entry = ttk.Entry(name_frame)
        name_entry.pack(side="left", fill="x", expand=True)

        desc_frame = ttk.Frame(form)
        desc_frame.pack(fill="x", padx=10, pady=(10, 0))
        ttk.Label(desc_frame, text="Description", width=12).pack(side="left", anchor="n")
        desc_entry = self._themed_text_widget(desc_frame, height=4)
        desc_entry.pack(side="left", fill="x", expand=True)

        row_frame = ttk.Frame(form)
        row_frame.pack(fill="x", padx=10, pady=(10, 0))

        ttk.Label(row_frame, text="Status*").grid(row=0, column=0, sticky="w")
        status_var = tk.StringVar(value="active")
        status_dropdown = ttk.Combobox(row_frame, textvariable=status_var, values=["active", "on_hold", "closed"], state="readonly", width=10)
        status_dropdown.grid(row=0, column=1, sticky="w", padx=(4, 16))

        ttk.Label(row_frame, text="Priority").grid(row=0, column=2, sticky="w")
        priority_var = tk.StringVar(value="medium")
        priority_dropdown = ttk.Combobox(row_frame, textvariable=priority_var, values=["medium", "high"], state="readonly", width=10)
        priority_dropdown.grid(row=0, column=3, sticky="w", padx=(4, 16))

        ttk.Label(row_frame, text="Deadline").grid(row=0, column=4, sticky="w")
        deadline_entry = ttk.Entry(row_frame, width=24)
        deadline_entry.grid(row=0, column=5, sticky="w", padx=(4, 0))
        ttk.Label(row_frame, text="YYYY-MM-DD HH:MM", bootstyle="secondary").grid(row=1, column=5, sticky="w", padx=(4, 0))

        error_label = ttk.Label(form, text="", bootstyle="danger")
        error_label.pack(padx=10, pady=(2, 0))

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

        submit_btn = ttk.Button(form, text="Confirm", command=submit, bootstyle="success")
        submit_btn.pack(pady=(15, 10))

    def open_edit_form(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        task_id, name, description, created_at, updated_at, status, priority, deadline = values

        form = ttk.Toplevel(self)
        form.title(f"Edit Task #{task_id}")
        form.geometry("560x250")
        form.grab_set()

        name_frame = ttk.Frame(form)
        name_frame.pack(fill="x", padx=10, pady=(10, 0))
        ttk.Label(name_frame, text="Name*", width=12).pack(side="left")
        name_entry = ttk.Entry(name_frame)
        name_entry.insert(0, name)
        name_entry.pack(side="left", fill="x", expand=True)

        desc_frame = ttk.Frame(form)
        desc_frame.pack(fill="x", padx=10, pady=(10, 0))
        ttk.Label(desc_frame, text="Description", width=12).pack(side="left", anchor="n")
        desc_entry = self._themed_text_widget(desc_frame, height=4)
        desc_entry.insert("1.0", "" if description == "-" else description)
        desc_entry.pack(side="left", fill="x", expand=True)

        row_frame = ttk.Frame(form)
        row_frame.pack(fill="x", padx=10, pady=(10, 0))

        ttk.Label(row_frame, text="Status*").grid(row=0, column=0, sticky="w")
        status_var = tk.StringVar(value=status)
        status_dropdown = ttk.Combobox(row_frame, textvariable=status_var, values=["active", "on_hold", "closed"], state="readonly", width=10)
        status_dropdown.grid(row=0, column=1, sticky="w", padx=(4, 16))

        ttk.Label(row_frame, text="Priority").grid(row=0, column=2, sticky="w")
        priority_var = tk.StringVar(value=priority)
        priority_dropdown = ttk.Combobox(row_frame, textvariable=priority_var, values=["medium", "high"], state="readonly", width=10)
        priority_dropdown.grid(row=0, column=3, sticky="w", padx=(4, 16))

        ttk.Label(row_frame, text="Deadline").grid(row=0, column=4, sticky="w")
        deadline_entry = ttk.Entry(row_frame, width=24)
        deadline_entry.insert(0, "" if deadline == "-" else deadline)
        deadline_entry.grid(row=0, column=5, sticky="w", padx=(4, 0))
        ttk.Label(row_frame, text="YYYY-MM-DD HH:MM", bootstyle="secondary").grid(row=1, column=5, sticky="w", padx=(4, 0))

        error_label = ttk.Label(form, text="", bootstyle="danger")
        error_label.pack(padx=10, pady=(2, 0))

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

        submit_btn = ttk.Button(form, text="confirm", command=submit, bootstyle="success")
        submit_btn.pack(pady=(15, 10))

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
