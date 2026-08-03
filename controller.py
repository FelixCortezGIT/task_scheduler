from database import Database

class TaskController:
    def __init__(self, db_path):
        self.db = Database(db_path)

    def create_task(self, name, description, status, priority, deadline=None):
        name = name.strip()
        if not name:
            raise ValueError("task's name is mandatory value")
        return self.db.add_task(name, description, status, priority, deadline)

    def edit_task(self, task_id, field, new_value):
        return self.db.update_task(task_id, field, new_value)

    def remove_task(self, task_id):
        return self.db.delete_task(task_id)

    def list_tasks(self, status_filter=None, show_all=False):
        return self.db.get_tasks(status_filter, show_all)

    def get_task_logs(self, task_id):
        return self.db.get_task_logs(task_id)
