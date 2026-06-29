import os
import threading
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Callable

from config import ANTHROPIC_MODELS, OPENAI_MODELS, ROLE_PRESETS, save_config
from rag import DocumentStore
from theme import ACCENT, BG, BG_DARK, BG_MID, FG, FG_DIM, FG_MUTED, GREEN, RED, YELLOW


class SettingsTab(tk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        cfg: dict,
        doc_store: DocumentStore,
        root: tk.Tk,
        on_save: Callable[[dict], None],
    ) -> None:
        super().__init__(parent, bg=BG)
        self._cfg = cfg
        self._doc_store = doc_store
        self._root = root
        self._on_save = on_save
        self._build()

    def _build(self) -> None:
        style = ttk.Style()
        style.configure("Inner.TNotebook", background=BG, borderwidth=0)
        style.configure("Inner.TNotebook.Tab", background=BG_MID, foreground=FG_DIM,
                        padding=[8, 3], font=("Segoe UI", 8))
        style.map("Inner.TNotebook.Tab",
                  background=[("selected", BG_DARK)],
                  foreground=[("selected", FG)])

        nb = ttk.Notebook(self, style="Inner.TNotebook")
        nb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # ── Tab 1: Context (RAG) ──────────────────────────────────────────────
        ctx = tk.Frame(nb, bg=BG, padx=10, pady=8)
        nb.add(ctx, text=" Context (RAG) ")
        self._build_context(ctx)

        # ── Tab 2: Role Play ──────────────────────────────────────────────────
        role = tk.Frame(nb, bg=BG, padx=10, pady=8)
        nb.add(role, text=" Role Play ")
        self._build_roleplay(role)

        # ── Tab 3: Model ──────────────────────────────────────────────────────
        model = tk.Frame(nb, bg=BG, padx=10, pady=8)
        nb.add(model, text=" Model ")
        self._build_model(model)

    # ── Context (RAG) ─────────────────────────────────────────────────────────

    def _build_context(self, parent: tk.Frame) -> None:
        tk.Label(parent, text="Upload files to use as context for every query.",
                 bg=BG, fg=FG_DIM, font=("Segoe UI", 8), wraplength=340,
                 justify="left").pack(anchor="w", pady=(0, 6))

        # Buttons row
        btn_row = tk.Frame(parent, bg=BG)
        btn_row.pack(fill=tk.X, pady=(0, 6))

        tk.Button(btn_row, text="+ Add File", bg=ACCENT, fg=BG_DARK,
                  relief=tk.FLAT, font=("Segoe UI Semibold", 8), padx=8, pady=4,
                  activebackground="#74c7ec",
                  command=self._add_file).pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(btn_row, text="Clear All", bg=BG_MID, fg=FG_DIM,
                  relief=tk.FLAT, font=("Segoe UI", 8), padx=8, pady=4,
                  activebackground=BG,
                  command=self._clear_all_files).pack(side=tk.LEFT)

        self._rag_status = tk.Label(btn_row, text="", bg=BG, fg=FG_MUTED,
                                     font=("Segoe UI", 7))
        self._rag_status.pack(side=tk.RIGHT)

        # File list
        list_frame = tk.Frame(parent, bg=BG_MID)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self._file_list = tk.Frame(list_frame, bg=BG_MID)
        self._file_list.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        self._no_files_lbl = tk.Label(
            self._file_list, text="No files loaded yet.\nSupports: PDF, DOCX, TXT, MD, PY…",
            bg=BG_MID, fg=FG_MUTED, font=("Segoe UI", 8), justify="center",
        )
        self._no_files_lbl.pack(expand=True, pady=20)

        self._refresh_file_list()

    def _add_file(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Select context files",
            filetypes=[
                ("All supported", "*.pdf *.docx *.txt *.md *.py *.js *.ts *.json *.csv"),
                ("PDF", "*.pdf"),
                ("Word", "*.docx"),
                ("Text", "*.txt *.md"),
                ("Code", "*.py *.js *.ts"),
                ("All files", "*.*"),
            ],
        )
        if not paths:
            return
        self._rag_status.config(text="Loading…", fg=YELLOW)
        threading.Thread(target=self._load_files, args=(paths,), daemon=True).start()

    def _load_files(self, paths: tuple[str, ...]) -> None:
        errors: list[str] = []
        for path in paths:
            try:
                n = self._doc_store.add(path)
                self._root.after(0, self._refresh_file_list)
                self._root.after(0, self._rag_status.config,
                                 {"text": f"✓ {os.path.basename(path)} ({n} chunks)", "fg": GREEN})
            except Exception as e:
                errors.append(f"{os.path.basename(path)}: {e}")
        if errors:
            self._root.after(0, self._rag_status.config,
                             {"text": "⚠ " + errors[0], "fg": RED})

    def _clear_all_files(self) -> None:
        self._doc_store.clear()
        self._refresh_file_list()
        self._rag_status.config(text="Cleared", fg=FG_MUTED)

    def _refresh_file_list(self) -> None:
        for w in self._file_list.winfo_children():
            w.destroy()
        names = self._doc_store.names()
        if not names:
            tk.Label(
                self._file_list,
                text="No files loaded yet.\nSupports: PDF, DOCX, TXT, MD, PY…",
                bg=BG_MID, fg=FG_MUTED, font=("Segoe UI", 8), justify="center",
            ).pack(expand=True, pady=20)
            return
        for name in names:
            row = tk.Frame(self._file_list, bg=BG_MID)
            row.pack(fill=tk.X, padx=4, pady=2)
            tk.Label(row, text="📄", bg=BG_MID, fg=FG_DIM,
                     font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(4, 2))
            tk.Label(row, text=name, bg=BG_MID, fg=FG,
                     font=("Segoe UI", 8), anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Button(row, text="✕", bg=BG_MID, fg=RED, relief=tk.FLAT,
                      font=("Segoe UI", 8), padx=4,
                      command=lambda n=name: self._remove_file(n)).pack(side=tk.RIGHT)
        # Notify chat tab
        self._on_save(self._cfg)

    def _remove_file(self, name: str) -> None:
        self._doc_store.remove(name)
        self._refresh_file_list()

    # ── Role Play ─────────────────────────────────────────────────────────────

    def _build_roleplay(self, parent: tk.Frame) -> None:
        tk.Label(parent, text="Choose a role for the AI or write a custom system prompt.",
                 bg=BG, fg=FG_DIM, font=("Segoe UI", 8), wraplength=340,
                 justify="left").pack(anchor="w", pady=(0, 6))

        self._role_var = tk.StringVar()

        # Find which preset is active (or Custom)
        current_prompt = self._cfg.get("system_prompt", "")
        active_role = "Custom"
        for name, prompt in ROLE_PRESETS.items():
            if prompt and prompt == current_prompt:
                active_role = name
                break
        self._role_var.set(active_role)

        presets_frame = tk.Frame(parent, bg=BG)
        presets_frame.pack(fill=tk.X, pady=(0, 8))

        for name in ROLE_PRESETS:
            tk.Radiobutton(
                presets_frame, text=name, variable=self._role_var, value=name,
                bg=BG, fg=FG, selectcolor=BG_MID, activebackground=BG,
                font=("Segoe UI", 8), command=self._on_role_select,
            ).pack(anchor="w", pady=1)

        tk.Frame(parent, bg=BG_MID, height=1).pack(fill=tk.X, pady=6)

        tk.Label(parent, text="System prompt (editable):", bg=BG, fg=FG_DIM,
                 font=("Segoe UI", 8)).pack(anchor="w")
        self._sys_text = tk.Text(
            parent, bg=BG_MID, fg=FG, insertbackground=FG,
            relief=tk.FLAT, font=("Consolas", 8), height=5,
            padx=6, pady=6, wrap=tk.WORD,
        )
        self._sys_text.insert(tk.END, current_prompt)
        self._sys_text.pack(fill=tk.BOTH, expand=True, pady=(4, 8))

        tk.Button(parent, text="Apply Role", bg=ACCENT, fg=BG_DARK,
                  relief=tk.FLAT, font=("Segoe UI Semibold", 9), padx=10, pady=4,
                  activebackground="#74c7ec",
                  command=self._apply_role).pack(anchor="e")

    def _on_role_select(self) -> None:
        name = self._role_var.get()
        prompt = ROLE_PRESETS.get(name, "")
        if prompt:
            self._sys_text.delete("1.0", tk.END)
            self._sys_text.insert(tk.END, prompt)

    def _apply_role(self) -> None:
        self._cfg["system_prompt"] = self._sys_text.get("1.0", tk.END).strip()
        save_config(self._cfg)
        self._on_save(self._cfg)

    # ── Model ─────────────────────────────────────────────────────────────────

    def _build_model(self, parent: tk.Frame) -> None:
        def row(label: str, anchor: str = "w") -> tk.Frame:
            f = tk.Frame(parent, bg=BG)
            f.pack(fill=tk.X, pady=3)
            tk.Label(f, text=label, bg=BG, fg=FG_DIM, font=("Segoe UI", 8),
                     width=10, anchor=anchor).pack(side=tk.LEFT, anchor="n")
            return f

        # Provider
        self._prov_var = tk.StringVar(value=self._cfg["provider"])
        pf = row("Provider")
        for p in ("openai", "anthropic"):
            tk.Radiobutton(pf, text=p.capitalize(), variable=self._prov_var, value=p,
                           bg=BG, fg=FG, selectcolor=BG_MID, activebackground=BG,
                           font=("Segoe UI", 8),
                           command=self._on_provider_change).pack(side=tk.LEFT, padx=4)

        # Model
        self._model_var = tk.StringVar(value=self._cfg["model"])
        mf = row("Model")
        self._model_combo = ttk.Combobox(mf, textvariable=self._model_var,
                                          font=("Segoe UI", 8), state="normal")
        self._model_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._refresh_model_list()

        # Base URL
        self._url_var = tk.StringVar(value=self._cfg["base_url"])
        uf = row("Base URL")
        tk.Entry(uf, textvariable=self._url_var, bg=BG_MID, fg=FG,
                 insertbackground=FG, relief=tk.FLAT,
                 font=("Consolas", 8)).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # API Key
        self._key_var = tk.StringVar(value=self._cfg["api_key"])
        kf = row("API Key")
        self._key_entry = tk.Entry(kf, textvariable=self._key_var, bg=BG_MID, fg=FG,
                                   insertbackground=FG, relief=tk.FLAT,
                                   font=("Consolas", 8), show="•")
        self._key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(kf, text="👁", bg=BG_MID, fg=FG_DIM, relief=tk.FLAT,
                  font=("Segoe UI", 8),
                  command=self._toggle_key_vis).pack(side=tk.LEFT, padx=2)

        # Opacity
        self._opacity_var = tk.DoubleVar(value=self._cfg["opacity"])
        of = row("Opacity")
        tk.Scale(of, from_=0.2, to=1.0, resolution=0.05, orient=tk.HORIZONTAL,
                 variable=self._opacity_var, bg=BG, fg=FG, highlightthickness=0,
                 troughcolor=BG_MID, length=180,
                 command=lambda v: self._root.attributes("-alpha", float(v))
                 ).pack(side=tk.LEFT)

        tk.Button(parent, text="Save Model Settings", bg=ACCENT, fg=BG_DARK,
                  relief=tk.FLAT, font=("Segoe UI Semibold", 9), padx=10, pady=4,
                  activebackground="#74c7ec",
                  command=self._save_model).pack(pady=(10, 0))

    def _on_provider_change(self) -> None:
        self._refresh_model_list()

    def _refresh_model_list(self) -> None:
        models = OPENAI_MODELS if self._prov_var.get() == "openai" else ANTHROPIC_MODELS
        self._model_combo["values"] = models
        if self._model_var.get() not in models:
            self._model_var.set(models[0])

    def _toggle_key_vis(self) -> None:
        self._key_entry.config(show="" if self._key_entry.cget("show") else "•")

    def _save_model(self) -> None:
        self._cfg.update({
            "provider": self._prov_var.get(),
            "api_key": self._key_var.get().strip(),
            "base_url": self._url_var.get().strip(),
            "model": self._model_var.get().strip(),
            "opacity": self._opacity_var.get(),
        })
        save_config(self._cfg)
        self._on_save(self._cfg)
