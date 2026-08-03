import sqlite3

class Database:
    def __init__(self, db_path="tasks.db"):
        self.db_path = db_path

    def add_task(self, name, description, status, priority, deadline=None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tasks (name, description, status, priority, deadline) VALUES (?, ?, ?, ?, ?)",
                (name, description, status, priority, deadline)
            )
            task_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO task_logs (task_id, event_type) VALUES (?, ?)",
                (task_id, "created")
            )
            conn.commit()
            return task_id

    def get_tasks(self, status_filter=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if status_filter:
                cursor.execute("SELECT * FROM tasks WHERE status = ? ORDER BY created_at ASC", (status_filter,))
            else:
                cursor.execute("SELECT * FROM tasks WHERE status != 'closed' ORDER BY created_at ASC")
            return cursor.fetchall()

    def update_task(self, task_id, field, new_value):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()

            # find old value
            cursor.execute(f"SELECT {field} FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"task id={task_id} does not exist")
            old_value = row[0]

            # update task
            cursor.execute(
                f"UPDATE tasks SET {field} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_value, task_id)
            )

            # add to log
            cursor.execute(
                "INSERT INTO task_logs (task_id, event_type, old_value, new_value) VALUES (?, ?, ?, ?)",
                (task_id, f"{field}_change", str(old_value), str(new_value))
            )
            conn.commit()

    def delete_task(self, task_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
            if cursor.fetchone() is None:
                raise ValueError(f"Task s id={task_id} neexistuje.")
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()

    def get_task_logs(self, task_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, event_type, old_value, new_value, created_at
                FROM task_logs WHERE task_id = ?
                ORDER BY created_at
                """,
                (task_id,)
            )
            return cursor.fetchall()


###
### create tables
###

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL DEFAULT 'medium',
                    deadline DATETIME,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    message TEXT,
                    old_value TEXT,
                    new_value TEXT,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                )
            """)
            conn.commit()
