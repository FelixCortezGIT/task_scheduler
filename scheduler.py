import threading
import time
from datetime import datetime
from controller import TaskController

class Scheduler:
    def __init__(self, db_path, on_deadline_reached, check_interval=60, reminder_interval_minutes=30):
        self.controller = TaskController(db_path)
        self.on_deadline_reached = on_deadline_reached
        self.check_interval = check_interval
        self.reminder_interval = reminder_interval_minutes * 60
        self.last_notified = {}
        self._stop_event = threading.Event()

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self._stop_event.set()

    def _run(self):
        while not self._stop_event.is_set():
            self._check_deadlines()
            time.sleep(self.check_interval)

    def _check_deadlines(self):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        tasks = self.controller.list_tasks()

        for task in tasks:
            task_id, name, description, status, priority, deadline, *_ = task
            if not deadline or deadline > now_str:
                continue

            last = self.last_notified.get(task_id)
            now_epoch = time.time()
            if last is None or (now_epoch - last) >= self.reminder_interval:
                self.last_notified[task_id] = now_epoch
                self.on_deadline_reached(task)
