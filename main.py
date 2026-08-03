import os
from database import Database
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.db")

def print_tasks(tasks):
    if not tasks:
        print("no task")
        return
    print(f"\n{'ID':<5} {'name':<25} {'description':<25} {'status':<12} {'priority':<10} {'deadline':<20}")
    print("-" * 98)
    for task in tasks:
        # task = (id, name, description, status, priority, deadline, created_at, updated_at)
        task_id, name, desc, status, priority, deadline, *_ = task
        deadline_str = deadline if deadline else "-"
        print(f"{task_id:<5} {name[:24]:<25} {desc[:24]:<25} {status:<12} {priority:<10} {deadline_str:<20}")

def main():
    db = Database(DB_PATH)

    if not os.path.exists(DB_PATH):
        db.init_db()

# add task
#     name = input("task name: ").strip()
#     description = input("notes: ").strip()
#     status = input("status: ").strip()
#     priority = input("priority (default: medium): ").strip() or "medium"
#     deadline = input("deadline (YYYY-MM-DD HH:MM press Enter for none): ").strip() or None
#     task_id = db.add_task(name, description, status, priority, deadline)
#     print(f"task added. ID: {task_id}")

# edit task
#     task_id = 2
#     field = "status"          # name / description / status / priority / deadline
#     new_value = "on hold"
#     db.update_task(task_id, field, new_value)
#     print(f"task {task_id} updated: {field} → {new_value}")

# delete task
#     task_id = 2
#     db.delete_task(task_id)
#     print(f"task {task_id} deleted")

# show all tasks
    tasks = db.get_tasks()
    print_tasks(tasks)

# show logs for task
#     task_id = 2
#     with sqlite3.connect(DB_PATH) as conn:
#         cursor = conn.cursor()
#         cursor.execute(
#             "SELECT id, event_type, old_value, new_value, created_at FROM task_logs WHERE task_id = ? ORDER BY created_at",
#             (task_id,)
#         )
#         logs = cursor.fetchall()
#         if not logs:
#             print("no logs for this task")
#         else:
#             for log in logs:
#                 print(log)

if __name__ == "__main__":
    main()
