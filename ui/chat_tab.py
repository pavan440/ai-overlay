import threading
import tkinter as tk
from tkinter import ttk
from typing import Callable

from PIL import ImageTk

from ai import call_anthropic, call_openai
from config import ANTHROPIC_MODELS, OPENAI_MODELS
from rag import DocumentStore
from theme import ACCENT, BG, BG_DARK, BG_MID, FG, FG_DIM, FG_MUTED, GREEN, RED, YELLOW
from voice import VoiceRecorder, transcribe
from vision import capture_screen

LEFT_W = 150   # fixed left-panel width


class ChatTab(tk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        cfg: dict,
        history: list,
        doc_store: DocumentStore,
        root: tk.Tk,
        on_no_key: Callable[[], None],
    ) -> None:
        super().__init__(parent, bg=BG)
        self._cfg = cfg
        self._history = history
        self._doc_store = doc_store
        self._root = root
        self._on_no_key = on_no_key

        self._recorder = VoiceRecorder()
        self._pending_image: str | None = None
        self._pending_thumb: ImageTk.PhotoImage | None = None

        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        # Left panel (fixed width)
        left = tk.Frame(self, bg=BG_DARK, width=LEFT_W)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)
        self._build_left(left)

        # Thin divider
        tk.Frame(self, bg=BG_MID, width=1).pack(side=tk.LEFT, fill=tk.Y)

        # Right panel (chat)
        right = tk.Frame(self, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._build_right(right)

    # ── Left panel ────────────────────────────────────────────────────────────

    def _build_left(self, parent: tk.Frame) -> None:
        def sep() -> None:
            tk.Frame(parent, bg=BG_MID, height=1).pack(fill=tk.X, padx=8, pady=6)

        # Voice button
        self._mic_btn = tk.Button(
            parent, text="🎤", bg=BG_MID, fg=FG,
            relief=tk.FLAT, font=("Segoe UI", 22), pady=10,
            activebackground=BG, command=self.toggle_mic,
        )
        self._mic_btn.pack(fill=tk.X, padx=8, pady=(12, 0))
        tk.Label(parent, text="Voice  Ctrl+R", bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 7)).pack()

        # Screenshot button
        self._ss_btn = tk.Button(
            parent, text="📷", bg=BG_MID, fg=FG,
            relief=tk.FLAT, font=("Segoe UI", 22), pady=10,
            activebackground=BG, command=self._take_screenshot,
        )
        self._ss_btn.pack(fill=tk.X, padx=8, pady=(8, 0))
        tk.Label(parent, text="Screenshot  Ctrl+G", bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 7)).pack()

        sep()

        # Model selector
        tk.Label(parent, text="Model", bg=BG_DARK, fg=FG_DIM,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=10)
        self._model_var = tk.StringVar(value=self._cfg.get("model", ""))
        self._model_combo = ttk.Combobox(
            parent, textvariable=self._model_var,
            font=("Segoe UI", 7), state="readonly",
        )
        self._model_combo.pack(fill=tk.X, padx=8, pady=(2, 4))
        self._model_combo.bind("<<ComboboxSelected>>", self._on_model_select)
        self.refresh_model_label()

        sep()

        # Shortcuts reference
        shortcuts = [
            ("Ctrl+R", "Voice"),
            ("Ctrl+G", "Screenshot"),
            ("Ctrl+H", "Hide"),
            ("Ctrl+Q", "Quit"),
        ]
        tk.Label(parent, text="Shortcuts", bg=BG_DARK, fg=FG_DIM,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=10, pady=(0, 4))
        for key, action in shortcuts:
            row = tk.Frame(parent, bg=BG_DARK)
            row.pack(fill=tk.X, padx=10, pady=1)
            tk.Label(row, text=key, bg=BG_DARK, fg=ACCENT,
                     font=("Consolas", 7), width=8, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=action, bg=BG_DARK, fg=FG_MUTED,
                     font=("Segoe UI", 7), anchor="w").pack(side=tk.LEFT)

        sep()

        # RAG status (bottom)
        self._rag_lbl = tk.Label(parent, text="", bg=BG_DARK, fg=YELLOW,
                                  font=("Segoe UI", 7), wraplength=130, justify="left")
        self._rag_lbl.pack(padx=8, anchor="w")
        self._refresh_rag_status()

        # Clear button (very bottom)
        tk.Button(parent, text="Clear Chat", bg=BG_MID, fg=FG_DIM,
                  relief=tk.FLAT, font=("Segoe UI", 8), pady=4,
                  activebackground=BG, command=self.clear).pack(
                      fill=tk.X, padx=8, side=tk.BOTTOM, pady=6)

    # ── Right panel ───────────────────────────────────────────────────────────

    def _build_right(self, parent: tk.Frame) -> None:
        # Chat history
        self._chat_box = tk.Text(
            parent, bg=BG, fg=FG, font=("Consolas", 10),
            relief=tk.FLAT, padx=10, pady=6, wrap=tk.WORD,
            state=tk.DISABLED, cursor="arrow", selectbackground=BG_MID,
        )
        self._chat_box.pack(fill=tk.BOTH, expand=True)

        sb = tk.Scrollbar(self._chat_box, command=self._chat_box.yview, bg=BG_MID)
        self._chat_box.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._chat_box.tag_config("you",  foreground=ACCENT, font=("Consolas", 10, "bold"))
        self._chat_box.tag_config("ai",   foreground=GREEN,  font=("Consolas", 10, "bold"))
        self._chat_box.tag_config("err",  foreground=RED)
        self._chat_box.tag_config("body", foreground=FG)
        self._chat_box.tag_config("dim",  foreground=FG_MUTED)
        self._chat_box.tag_config("img",  foreground=YELLOW)

        self.append("dim", "─── AI Overlay ready. Type below or press Ctrl+R to speak. ───\n\n")

        # Image preview strip (hidden by default)
        self._preview_frame = tk.Frame(parent, bg=BG_DARK, pady=3)
        tk.Label(self._preview_frame, text="📷 Screenshot attached",
                 bg=BG_DARK, fg=YELLOW, font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=6)
        self._thumb_label = tk.Label(self._preview_frame, bg=BG_DARK)
        self._thumb_label.pack(side=tk.LEFT, padx=2)
        tk.Button(self._preview_frame, text="✕", bg=BG_DARK, fg=RED,
                  relief=tk.FLAT, font=("Segoe UI", 8),
                  command=self._clear_image).pack(side=tk.LEFT, padx=4)

        # Input row
        input_row = tk.Frame(parent, bg=BG_DARK, pady=4)
        input_row.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Button(input_row, text="Send ↵", bg=ACCENT, fg=BG_DARK,
                  relief=tk.FLAT, font=("Segoe UI Semibold", 9), padx=10,
                  activebackground="#74c7ec", command=self.send).pack(side=tk.RIGHT, padx=6)

        self._input_box = tk.Text(
            input_row, bg=BG_MID, fg=FG, insertbackground=FG,
            font=("Consolas", 10), relief=tk.FLAT,
            height=3, padx=6, pady=4, wrap=tk.WORD,
        )
        self._input_box.pack(fill=tk.X, expand=True, padx=(6, 2))
        self._input_box.bind("<Return>", self._on_enter)
        self._input_box.bind("<Shift-Return>", lambda e: None)
        self._input_box.focus_set()

    # ── Model ─────────────────────────────────────────────────────────────────

    def refresh_model_label(self) -> None:
        models = OPENAI_MODELS if self._cfg.get("provider") == "openai" else ANTHROPIC_MODELS
        self._model_combo["values"] = models
        current = self._cfg.get("model", "")
        self._model_var.set(current if current in models else models[0])

    def _on_model_select(self, _event: tk.Event) -> None:
        self._cfg["model"] = self._model_var.get()

    # ── RAG status ────────────────────────────────────────────────────────────

    def _refresh_rag_status(self) -> None:
        names = self._doc_store.names()
        if names:
            self._rag_lbl.config(
                text=f"📄 {len(names)} file(s) loaded\n{self._doc_store.chunk_count} chunks"
            )
        else:
            self._rag_lbl.config(text="No context files")

    def refresh_rag_status(self) -> None:
        self._refresh_rag_status()

    # ── Chat helpers ──────────────────────────────────────────────────────────

    def append(self, tag: str, text: str) -> None:
        self._chat_box.configure(state=tk.NORMAL)
        self._chat_box.insert(tk.END, text, tag)
        self._chat_box.configure(state=tk.DISABLED)
        self._chat_box.see(tk.END)

    def clear(self) -> None:
        self._history.clear()
        self._chat_box.configure(state=tk.NORMAL)
        self._chat_box.delete("1.0", tk.END)
        self._chat_box.configure(state=tk.DISABLED)
        self.append("dim", "─── Conversation cleared. ───\n\n")

    # ── Send ──────────────────────────────────────────────────────────────────

    def _on_enter(self, event: tk.Event) -> str | None:
        if not event.state & 0x1:
            self.send()
            return "break"
        return None

    def send(self) -> None:
        text = self._input_box.get("1.0", tk.END).strip()
        if not text and not self._pending_image:
            return
        if not self._cfg.get("api_key"):
            self.append("err", "⚠ No API key — go to Settings › Model.\n\n")
            self._on_no_key()
            return

        self._input_box.delete("1.0", tk.END)

        if self._pending_image:
            content: object = [
                {"type": "text", "text": text or "What do you see in this screenshot?"},
                {"type": "image_url", "image_url": {"url": self._pending_image}},
            ]
            self.append("you", "You: ")
            self.append("body", (text or "(screenshot)") + "\n")
            self.append("img", "  [screenshot attached]\n")
            self._clear_image()
        else:
            content = text
            self.append("you", "You: ")
            self.append("body", text + "\n")

        self.append("ai", "AI:  ")
        self._history.append({"role": "user", "content": content})

        # Inject RAG context into system prompt if docs are loaded
        system = self._cfg["system_prompt"]
        if self._doc_store.has_docs and isinstance(content, str):
            ctx = self._doc_store.get_context(text)
            if ctx:
                system = f"{system}\n\n{ctx}"

        messages = [{"role": "system", "content": system}] + self._history
        threading.Thread(target=self._stream, args=(messages,), daemon=True).start()

    def _stream(self, messages: list) -> None:
        try:
            fn = call_openai if self._cfg["provider"] == "openai" else call_anthropic
            full = ""
            for chunk in fn(self._cfg, messages):
                full += chunk
                self._root.after(0, self.append, "body", chunk)
            self._root.after(0, self.append, "body", "\n\n")
            self._history.append({"role": "assistant", "content": full})
        except Exception as e:
            self._root.after(0, self.append, "err", f"\n⚠ Error: {e}\n\n")

    # ── Voice ─────────────────────────────────────────────────────────────────

    def toggle_mic(self) -> None:
        if self._recorder.is_recording:
            self._mic_btn.config(bg=BG_MID, fg=FG)
            self.append("dim", "⏹ Transcribing…\n")
            wav = self._recorder.stop()
            if wav:
                threading.Thread(target=self._do_transcribe, args=(wav,), daemon=True).start()
        else:
            self._mic_btn.config(bg=RED, fg=BG_DARK)
            self.append("dim", "🎤 Recording… (Ctrl+R to stop)\n")
            self._recorder.start()

    def _do_transcribe(self, wav: bytes) -> None:
        try:
            text = transcribe(wav, self._cfg["api_key"], self._cfg["base_url"])
            self._root.after(0, self._insert_transcription, text)
        except Exception as e:
            import traceback
            detail = traceback.format_exc()
            self._root.after(0, self.append, "err", f"\n⚠ Transcription error: {e}\n{detail}\n")

    def _insert_transcription(self, text: str) -> None:
        self._input_box.delete("1.0", tk.END)
        self._input_box.insert(tk.END, text)
        self._input_box.focus_set()

    # ── Screenshot ────────────────────────────────────────────────────────────

    def _take_screenshot(self) -> None:
        self._root.withdraw()
        self._root.after(200, self._grab_screen)

    def _grab_screen(self) -> None:
        try:
            shot = capture_screen()
            self._pending_image = shot.data_url
            self._pending_thumb = ImageTk.PhotoImage(shot.thumb)
            self._root.after(0, self._show_preview)
        except Exception as e:
            self._root.after(0, self.append, "err", f"\n⚠ Screenshot error: {e}\n\n")
        finally:
            self._root.after(0, self._root.deiconify)

    def _show_preview(self) -> None:
        self._thumb_label.config(image=self._pending_thumb)
        self._preview_frame.pack(fill=tk.X, side=tk.BOTTOM, before=self._input_box.master)

    def _clear_image(self) -> None:
        self._pending_image = None
        self._pending_thumb = None
        self._preview_frame.pack_forget()
