import threading
import tkinter as tk
from typing import Callable
from processor import SubtitleProcessor
from config import AppConfig, LANGUAGES


class AreaSelector:
    def __init__(self, parent: tk.Tk, config: AppConfig, on_complete: Callable[[], None]):
        self.config = config
        self.on_complete = on_complete

        self.top = tk.Toplevel(parent)

        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        self.top.geometry(f"{screen_width}x{screen_height}+0+0")
        self.top.overrideredirect(True)

        self.top.attributes("-alpha", 0.4)
        self.top.attributes("-topmost", True)
        self.top.config(cursor="cross")

        self.transparent_color = "magenta"
        try:
            self.top.attributes("-transparentcolor", self.transparent_color)
            self.has_transparent_color = True
        except tk.TclError:
            self.has_transparent_color = False

        self.canvas = tk.Canvas(self.top, bg="gray10", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.rect = None
        self.start_x = 0
        self.start_y = 0

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        self.top.bind("<Escape>", lambda e: self._close())
        self.top.focus_force()

    def _on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

        fill_color = self.transparent_color if self.has_transparent_color else "gray40"

        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="#00FF00", width=2, fill=fill_color
        )

    def _on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def _on_release(self, event):
        end_x, end_y = event.x, event.y

        left = min(self.start_x, end_x)
        top = min(self.start_y, end_y)
        width = abs(end_x - self.start_x)
        height = abs(end_y - self.start_y)

        if width > 10 and height > 10:
            self.config.monitor_left = left
            self.config.monitor_top = top
            self.config.monitor_width = width
            self.config.monitor_height = height

        self._close()

    def _close(self):
        self.on_complete()
        self.top.destroy()


class UIOverlay:
    def __init__(
            self,
            processor_factory: Callable[[Callable[[str], None]], SubtitleProcessor],
            config: AppConfig
    ):
        self.config = config
        self.root = tk.Tk()

        self._drag_x = 0
        self._drag_y = 0

        self._setup_window()

        self.text_var = tk.StringVar(value="Waiting for subs...")
        self._setup_widgets()

        self.processor = processor_factory(self.update_text)

    def _setup_window(self):
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.8)
        self.root.overrideredirect(True)
        self.root.geometry("+100+50")
        self._force_top()

    def _get_lang_name_by_code(self, code: str) -> str:
        for name, data in LANGUAGES.items():
            if data["source"] == code or data["target"] == code:
                return name
        return list(LANGUAGES.keys())[0]

    def _on_source_change(self, *args):
        lang_data = LANGUAGES[self.source_var.get()]
        self.config.source_lang = lang_data["source"]
        self.config.tesseract_lang = lang_data["tess"]
        self.processor.last_text = ""

    def _on_target_change(self, *args):
        lang_data = LANGUAGES[self.target_var.get()]
        self.config.target_lang = lang_data["target"]
        self.processor.last_text = ""

    def _start_move(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_motion(self, event):
        x = self.root.winfo_x() + (event.x - self._drag_x)
        y = self.root.winfo_y() + (event.y - self._drag_y)
        self.root.geometry(f"+{x}+{y}")

    def _make_draggable(self, widget):
        widget.bind("<ButtonPress-1>", self._start_move)
        widget.bind("<B1-Motion>", self._on_motion)

    def _start_area_selection(self):
        self.processor.is_paused = True
        self.text_var.set("Select area on screen...")
        AreaSelector(self.root, self.config, self._on_area_selected)

    def _on_area_selected(self):
        self.processor.last_text = ""
        self.text_var.set("Waiting for subs...")
        self.processor.is_paused = False

    def _setup_widgets(self):
        control_frame = tk.Frame(self.root, bg="black", cursor="fleur")
        control_frame.pack(fill="x", padx=15, pady=5)
        self._make_draggable(control_frame)

        self.source_var = tk.StringVar(value=self._get_lang_name_by_code(self.config.source_lang))
        self.target_var = tk.StringVar(value=self._get_lang_name_by_code(self.config.target_lang))

        self.source_var.trace_add("write", self._on_source_change)
        self.target_var.trace_add("write", self._on_target_change)

        source_menu = tk.OptionMenu(control_frame, self.source_var, *LANGUAGES.keys())
        target_menu = tk.OptionMenu(control_frame, self.target_var, *LANGUAGES.keys())

        for menu in (source_menu, target_menu):
            menu.config(
                bg="black", fg="#00FF00", highlightthickness=0, bd=0,
                activebackground="#333333", activeforeground="#00FF00", font=("Arial", 12)
            )
            menu["menu"].config(bg="black", fg="#00FF00", font=("Arial", 12))

        select_btn = tk.Button(
            control_frame, text="✂", bg="black", fg="#00FF00", bd=0,
            font=("Arial", 14), command=self._start_area_selection,
            cursor="hand2", activebackground="#333333", activeforeground="#00FF00"
        )
        select_btn.pack(side="left", padx=(0, 10))

        source_menu.pack(side="left")

        arrow_label = tk.Label(control_frame, text=" ➔ ", bg="black", fg="#00FF00", font=("Arial", 12, "bold"))
        arrow_label.pack(side="left")
        self._make_draggable(arrow_label)

        target_menu.pack(side="left")

        text_label = tk.Label(
            self.root, textvariable=self.text_var, fg="#00FF00", bg="black",
            font=("Arial", 20, "bold"), justify="left", padx=15, pady=10, cursor="fleur"
        )
        text_label.pack(anchor="w")
        self._make_draggable(text_label)

    def _force_top(self):
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(250, self._force_top)

    def update_text(self, text: str):
        self.text_var.set(text)

    def run(self):
        thread = threading.Thread(target=self.processor.start, daemon=True)
        thread.start()
        self.root.mainloop()
        self.processor.stop()
