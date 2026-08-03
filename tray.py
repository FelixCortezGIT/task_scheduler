import pystray
from PIL import Image, ImageDraw
import tkinter as tk
import keyboard
import threading
from view.dashboard import Dashboard
from controller import TaskController

class TrayApp:
    def __init__(self):
        self.window = None
        self.tray_icon = None
        self._setup_window()
        self._setup_tray()

    def _setup_window(self):
        self.window = tk.Tk()
        self.window.title("task scheduler")
        self.window.geometry("900x400")
        self.window.withdraw()  # window is hidden
        self.window.protocol("WM_DELETE_WINDOW", self.hide_window)  # X = hide, but not close app

        controller = TaskController("tasks.db")
        self.dashboard = Dashboard(self.window, controller)
        self.dashboard.pack(fill="both", expand=True)

    def _create_icon_image(self):
        # placeholder icon (blue square)
        image = Image.new("RGB", (64, 64), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill="blue")
        return image

    def _setup_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("Show/Hide", self.toggle_window),
            pystray.MenuItem("Exit", self.quit_app)
        )
        self.tray_icon = pystray.Icon("task_tracker", self._create_icon_image(), "task scheduler", menu)

    def show_window(self):
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()

    def hide_window(self):
        self.window.withdraw()

    def toggle_window(self, icon=None, item=None):
        if self.window.state() == "withdrawn":
            self.show_window()
        else:
            self.hide_window()

    def quit_app(self, icon=None, item=None):
        self.tray_icon.stop()
        self.window.quit()

    def _hotkey_listener(self):
        keyboard.add_hotkey("ctrl+shift", self.toggle_window)
        keyboard.wait()

    def run(self):
        threading.Thread(target=self._hotkey_listener, daemon=True).start()
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
        self.window.mainloop()

if __name__ == "__main__":
    app = TrayApp()
    app.run()
