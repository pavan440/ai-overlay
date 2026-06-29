import ctypes
import tkinter as tk
from tkinter import ttk

from config import load_config
from rag import DocumentStore
from theme import ACCENT, BG, BG_DARK, BG_MID, FG, FG_DIM, GREEN, RED
from ui.chat_tab import ChatTab
from ui.settings_tab import SettingsTab
from win32_utils import apply_overlay


class OverlayApp:
    def __init__(self) -> None:
        self.cfg = load_config()
        self.history: list = []
        self.doc_store = DocumentStore()
        self._drag_x = 0
        self._drag_y = 0
        self.hidden = False

        self.root = tk.Tk()
        self.root.title("AI Overlay")
        self.root.geometry("640x500+80+80")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", self.cfg["opacity"])
        self.root.overrideredirect(True)
        self.root.configure(bg=BG_DARK)

        self._build_titlebar()
        self._build_notebook()
        self.root.update_idletasks()
        self._apply_win32()
        self._bind_keys()

    def _apply_win32(self) -> None:
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        apply_overlay(hwnd)

    def _build_titlebar(self) -> None:
        bar = tk.Frame(self.root, bg=BG_DARK, height=30)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)
        bar.bind("<ButtonPress-1>", self._drag_start)
        bar.bind("<B1-Motion>", self._drag_move)

        title_lbl = tk.Label(bar, text="AI Overlay", bg=BG_DARK, fg=ACCENT,
                              font=("Segoe UI Semibold", 9))
        title_lbl.pack(side=tk.LEFT, padx=8)

        tk.Button(bar, text="✕", bg=BG_DARK, fg=RED, relief=tk.FLAT,
                  font=("Segoe UI", 10), padx=6,
                  activebackground=BG_MID, activeforeground=RED,
                  command=self.root.destroy).pack(side=tk.RIGHT)
        tk.Button(bar, text="—", bg=BG_DARK, fg=GREEN, relief=tk.FLAT,
                  font=("Segoe UI", 10), padx=6,
                  activebackground=BG_MID, activeforeground=GREEN,
                  command=self._toggle_hide).pack(side=tk.RIGHT)

    def _build_notebook(self) -> None:
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_MID, foreground=FG_DIM,
                        padding=[12, 4], font=("Segoe UI", 8))
        style.map("TNotebook.Tab",
                  background=[("selected", BG)],
                  foreground=[("selected", FG)])

        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill=tk.BOTH, expand=True)

        self.chat_tab = ChatTab(
            self.nb, self.cfg, self.history, self.doc_store, self.root,
            on_no_key=lambda: self.nb.select(1),
        )
        self.nb.add(self.chat_tab, text=" Chat ")

        self.settings_tab = SettingsTab(
            self.nb, self.cfg, self.doc_store, self.root,
            on_save=self._on_settings_saved,
        )
        self.nb.add(self.settings_tab, text=" Settings ")

    def _on_settings_saved(self, _cfg: dict) -> None:
        self.chat_tab.refresh_model_label()
        self.chat_tab.refresh_rag_status()

    def _drag_start(self, event: tk.Event) -> None:
        self._drag_x = event.x_root - self.root.winfo_x()
        self._drag_y = event.y_root - self.root.winfo_y()

    def _drag_move(self, event: tk.Event) -> None:
        self.root.geometry(f"+{event.x_root - self._drag_x}+{event.y_root - self._drag_y}")

    def _toggle_hide(self) -> None:
        if self.hidden:
            self.root.deiconify()
            self.hidden = False
        else:
            self.root.withdraw()
            self.hidden = True

    def _bind_keys(self) -> None:
        self.root.bind_all("<Control-h>", lambda e: self._toggle_hide())
        self.root.bind_all("<Control-r>", lambda e: self.chat_tab.toggle_mic())
        self.root.bind_all("<Control-g>", lambda e: self.chat_tab._take_screenshot())
        self.root.bind_all("<Control-q>", lambda e: self.root.destroy())

    def run(self) -> None:
        self.root.mainloop()
