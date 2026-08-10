import sys
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
            outline="#4ADE80", width=2, fill=fill_color
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

        self.bg_main = "#121212"
        self.bg_bar = "#1E1E1E"
        self.bg_hover = "#2C2C2C"
        self.fg_accent = "#4ADE80"
        self.fg_text = "#E5E7EB"
        self.fg_danger = "#F87171"

        self._drag_x = 0
        self._drag_y = 0
        self._resize_x = 0
        self._resize_y = 0
        self._start_width = 0
        self._start_height = 0

        self._setup_window()
        self._setup_widgets()

        self.processor = processor_factory(self.update_text)
        self.update_text("Waiting for subs...")

    def _setup_window(self):
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.85)
        self.root.overrideredirect(True)
        self.root.geometry("650x180+100+50")
        self.root.configure(bg=self.bg_main)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

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

    def _start_resize(self, event):
        self._resize_x = event.x_root
        self._resize_y = event.y_root
        self._start_width = self.root.winfo_width()
        self._start_height = self.root.winfo_height()

    def _on_resize_motion(self, event):
        delta_x = event.x_root - self._resize_x
        delta_y = event.y_root - self._resize_y
        new_width = max(300, self._start_width + delta_x)
        new_height = max(100, self._start_height + delta_y)
        self.root.geometry(f"{new_width}x{new_height}")

    def _start_area_selection(self, event=None):
        self.processor.is_paused = True
        self.update_text("Select area on screen...")
        AreaSelector(self.root, self.config, self._on_area_selected)

    def _on_area_selected(self):
        self.processor.last_text = ""
        self.update_text("Waiting for subs...")
        self.processor.is_paused = False

    def _quit(self, event=None):
        self.processor.stop()
        self.root.destroy()
        sys.exit(0)

    def _create_hover_btn(self, parent, text, fg_color, command):
        lbl = tk.Label(
            parent, text=text, bg=self.bg_bar, fg=fg_color,
            font=("Arial", 16), padx=10, cursor="hand2"
        )
        lbl.bind("<Button-1>", command)
        lbl.bind("<Enter>", lambda e: lbl.config(bg=self.bg_hover))
        lbl.bind("<Leave>", lambda e: lbl.config(bg=self.bg_bar))
        return lbl

    def _setup_widgets(self):
        control_frame = tk.Frame(self.root, bg=self.bg_bar, cursor="fleur", height=40)
        control_frame.grid(row=0, column=0, sticky="ew")
        control_frame.pack_propagate(False)
        self._make_draggable(control_frame)

        select_btn = self._create_hover_btn(control_frame, "✂", self.fg_accent, self._start_area_selection)
        select_btn.pack(side="left")

        exit_btn = self._create_hover_btn(control_frame, "✖", self.fg_danger, self._quit)
        exit_btn.pack(side="right")

        menus_frame = tk.Frame(control_frame, bg=self.bg_bar)
        menus_frame.pack(side="left", fill="both", expand=True)
        self._make_draggable(menus_frame)

        menus_container = tk.Frame(menus_frame, bg=self.bg_bar)
        menus_container.pack(expand=True)

        self.source_var = tk.StringVar(value=self._get_lang_name_by_code(self.config.source_lang))
        self.target_var = tk.StringVar(value=self._get_lang_name_by_code(self.config.target_lang))

        self.source_var.trace_add("write", self._on_source_change)
        self.target_var.trace_add("write", self._on_target_change)

        menu_opts = {
            "bg": self.bg_bar, "fg": self.fg_text, "highlightthickness": 0, "bd": 0,
            "activebackground": self.bg_hover, "activeforeground": self.fg_text,
            "font": ("Arial", 12), "indicatoron": 0
        }

        source_menu = tk.OptionMenu(menus_container, self.source_var, *LANGUAGES.keys())
        target_menu = tk.OptionMenu(menus_container, self.target_var, *LANGUAGES.keys())

        for menu in (source_menu, target_menu):
            menu.config(**menu_opts)
            menu["menu"].config(bg=self.bg_main, fg=self.fg_text, font=("Arial", 12), bd=0,
                                activebackground=self.bg_hover)

        source_menu.pack(side="left", padx=5)

        arrow_label = tk.Label(menus_container, text="➔", bg=self.bg_bar, fg=self.fg_accent, font=("Arial", 14))
        arrow_label.pack(side="left", padx=10)
        self._make_draggable(arrow_label)

        target_menu.pack(side="left", padx=5)

        self.text_widget = tk.Text(
            self.root, fg=self.fg_text, bg=self.bg_main, font=("Arial", 18, "bold"),
            padx=15, pady=10, bd=0, highlightthickness=0, wrap="word", spacing1=5, spacing3=5
        )
        self.text_widget.grid(row=1, column=0, sticky="nsew")

        resize_cursor = "size_nw_se" if sys.platform == "win32" else "bottom_right_corner"
        self.grip = tk.Label(
            self.root,
            text="⇲",
            bg=self.bg_main,
            fg=self.fg_accent,
            font=("Arial", 14),
            cursor=resize_cursor,
        )
        self.grip.place(relx=1.0, rely=1.0, anchor="se")
        self.grip.bind("<ButtonPress-1>", self._start_resize)
        self.grip.bind("<B1-Motion>", self._on_resize_motion)

    def update_text(self, text: str):
        self.root.after(0, self._safe_update_text, text)

    def _safe_update_text(self, text: str):
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, text)
        self.text_widget.config(state="disabled")

    def run(self):
        thread = threading.Thread(target=self.processor.start, daemon=True)
        thread.start()
        self.root.mainloop()
        self.processor.stop()
