import customtkinter as ctk

from ui import theme as T
from ui.dialogs import HolocronDialog, Order66Dialog

CLIPBOARD_CLEAR_MS = 20_000


class _Screen(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app, fg_color=app.theme["bg"])
        self.app = app
        self.theme = app.theme


class SetupScreen(_Screen):
    def __init__(self, app):
        super().__init__(app)
        box = ctk.CTkFrame(self, fg_color="transparent")
        box.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(box, text="EXEGOL VAULT", font=T.TITLE_FONT,
                     text_color=self.theme["accent"]).pack()
        ctk.CTkLabel(box, text="No master code exists. Forge one to seal the archives.",
                     font=T.SUBTITLE_FONT, text_color=self.theme["text_dim"]).pack(pady=(4, 24))

        self.pw = ctk.CTkEntry(box, placeholder_text="Master code (min 8 characters)",
                               show="•", width=320, font=T.BODY_FONT,
                               fg_color=self.theme["panel"], border_color=self.theme["accent_dim"])
        self.pw.pack(pady=6)
        self.pw2 = ctk.CTkEntry(box, placeholder_text="Speak it again", show="•",
                                width=320, font=T.BODY_FONT,
                                fg_color=self.theme["panel"], border_color=self.theme["accent_dim"])
        self.pw2.pack(pady=6)

        self.error = ctk.CTkLabel(box, text="", font=T.SUBTITLE_FONT,
                                  text_color=self.theme["danger"])
        self.error.pack(pady=(4, 0))

        ctk.CTkButton(box, text="Forge Master Code", width=320, height=40,
                      command=self._submit, font=T.BODY_BOLD,
                      fg_color=self.theme["accent"], hover_color=self.theme["accent_hover"],
                      text_color=self.theme["on_accent"]).pack(pady=(10, 4))
        ctk.CTkLabel(box, text="Guard it well. It cannot be recovered.",
                     font=T.SUBTITLE_FONT, text_color=self.theme["text_dim"]).pack()

        self.pw.focus_set()
        for widget in (self.pw, self.pw2):
            widget.bind("<Return>", lambda _e: self._submit())

    def _submit(self):
        pw, pw2 = self.pw.get(), self.pw2.get()
        if len(pw) < 8:
            self.error.configure(text="Too weak. At least 8 characters, apprentice.")
            return
        if pw != pw2:
            self.error.configure(text="The codes do not match.")
            return
        self.app.create_master(pw)


class LoginScreen(_Screen):
    def __init__(self, app):
        super().__init__(app)
        box = ctk.CTkFrame(self, fg_color="transparent")
        box.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(box, text="EXEGOL VAULT", font=T.TITLE_FONT,
                     text_color=self.theme["accent"]).pack()
        ctk.CTkLabel(box, text="The archives are sealed. Identify yourself.",
                     font=T.SUBTITLE_FONT, text_color=self.theme["text_dim"]).pack(pady=(4, 24))

        self.pw = ctk.CTkEntry(box, placeholder_text="Master code", show="•",
                               width=320, font=T.BODY_FONT,
                               fg_color=self.theme["panel"], border_color=self.theme["accent_dim"])
        self.pw.pack(pady=6)

        self.error = ctk.CTkLabel(box, text="", font=T.SUBTITLE_FONT,
                                  text_color=self.theme["danger"])
        self.error.pack(pady=(4, 0))

        ctk.CTkButton(box, text="Unseal the Archives", width=320, height=40,
                      command=self._submit, font=T.BODY_BOLD,
                      fg_color=self.theme["accent"], hover_color=self.theme["accent_hover"],
                      text_color=self.theme["on_accent"]).pack(pady=(10, 0))
        ctk.CTkLabel(box, text=self.theme["tagline"], font=T.SUBTITLE_FONT,
                     text_color=self.theme["text_dim"]).pack(pady=(16, 0))

        self.pw.focus_set()
        self.pw.bind("<Return>", lambda _e: self._submit())

    def _submit(self):
        if not self.app.unlock(self.pw.get()):
            self.pw.delete(0, "end")
            self.error.configure(text="Access denied. The Force is not with you.")


class VaultScreen(_Screen):
    def __init__(self, app):
        super().__init__(app)
        self._clipboard_job = None

        header = ctk.CTkFrame(self, fg_color=self.theme["panel"], corner_radius=0, height=64)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="EXEGOL VAULT", font=("Segoe UI", 20, "bold"),
                     text_color=self.theme["accent"]).pack(side="left", padx=18, pady=14)
        ctk.CTkButton(header, text="Seal Archives 🔒", width=130, command=self.app.lock,
                      fg_color=self.theme["panel_hover"], hover_color=self.theme["accent_dim"],
                      text_color=self.theme["text"]).pack(side="right", padx=(6, 18), pady=14)
        ctk.CTkButton(header, text=self.theme["toggle_label"], width=170,
                      command=self.app.toggle_theme,
                      fg_color=self.theme["panel_hover"], hover_color=self.theme["accent_dim"],
                      text_color=self.theme["text"]).pack(side="right", pady=14)

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=18, pady=(14, 8))
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        ctk.CTkEntry(toolbar, placeholder_text="Search the archives…",
                     textvariable=self.search_var, font=T.BODY_FONT, height=38,
                     fg_color=self.theme["panel"], border_color=self.theme["accent_dim"],
                     text_color=self.theme["text"]).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(toolbar, text="+ Forge Holocron", width=150, height=38,
                      command=self._add, font=T.BODY_BOLD,
                      fg_color=self.theme["accent"], hover_color=self.theme["accent_hover"],
                      text_color=self.theme["on_accent"]).pack(side="left", padx=(10, 0))

        self.status = ctk.CTkLabel(self, text="", font=T.SUBTITLE_FONT,
                                   text_color=self.theme["accent"])
        self.status.pack(padx=18, anchor="w")

        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=12, pady=(2, 12))

        self.refresh()

    def refresh(self):
        for child in self.list_frame.winfo_children():
            child.destroy()
        entries = self.app.db.list_holocrons(self.search_var.get().strip())
        if not entries:
            msg = ("Nothing found in the archives." if self.search_var.get().strip()
                   else "The archives are empty. Forge your first holocron.")
            ctk.CTkLabel(self.list_frame, text=msg, font=T.BODY_FONT,
                         text_color=self.theme["text_dim"]).pack(pady=40)
            return
        for entry in entries:
            self._row(entry)

    def _row(self, entry):
        row = ctk.CTkFrame(self.list_frame, fg_color=self.theme["panel"], corner_radius=10)
        row.pack(fill="x", padx=6, pady=4)

        text = ctk.CTkFrame(row, fg_color="transparent")
        text.pack(side="left", fill="x", expand=True, padx=14, pady=10)
        ctk.CTkLabel(text, text=entry["title"], font=T.BODY_BOLD,
                     text_color=self.theme["text"], anchor="w").pack(fill="x")
        subtitle = entry["username"] or entry["url"] or "-"
        ctk.CTkLabel(text, text=subtitle, font=T.SUBTITLE_FONT,
                     text_color=self.theme["text_dim"], anchor="w").pack(fill="x")

        btns = ctk.CTkFrame(row, fg_color="transparent")
        btns.pack(side="right", padx=10)
        for label, cmd, tip_color in (
            ("👁", lambda e=entry: self._reveal(e), self.theme["text"]),
            ("📋", lambda e=entry: self._copy(e), self.theme["text"]),
            ("✏️", lambda e=entry: self._edit(e), self.theme["text"]),
            ("💀", lambda e=entry: self._delete(e), self.theme["danger"]),
        ):
            ctk.CTkButton(btns, text=label, width=40, height=32, command=cmd,
                          fg_color=self.theme["panel_hover"],
                          hover_color=self.theme["accent_dim"],
                          text_color=tip_color, font=T.BODY_FONT).pack(side="left", padx=3)

    def _add(self):
        dialog = HolocronDialog(self, self.theme)
        self.wait_window(dialog)
        if dialog.result:
            d = dialog.result
            self.app.db.add_holocron(d["title"], d["username"],
                                     self.app.cipher.encrypt(d["password"]),
                                     d["url"], d["notes"])
            self._flash(f"'{d['title']}' archived.")
            self.refresh()

    def _edit(self, entry):
        entry = dict(entry, password=self.app.cipher.decrypt(entry["password_enc"]))
        dialog = HolocronDialog(self, self.theme, entry=entry)
        self.wait_window(dialog)
        if dialog.result:
            d = dialog.result
            self.app.db.update_holocron(entry["id"], d["title"], d["username"],
                                        self.app.cipher.encrypt(d["password"]),
                                        d["url"], d["notes"])
            self._flash(f"'{d['title']}' updated.")
            self.refresh()

    def _delete(self, entry):
        dialog = Order66Dialog(self, self.theme, entry["title"])
        self.wait_window(dialog)
        if dialog.confirmed:
            self.app.db.delete_holocron(entry["id"])
            self._flash(f"'{entry['title']}' has been dealt with. Permanently.")
            self.refresh()

    def _reveal(self, entry):
        password = self.app.cipher.decrypt(entry["password_enc"])
        popup = ctk.CTkToplevel(self)
        popup.title(entry["title"])
        popup.configure(fg_color=self.theme["bg"])
        popup.geometry("380x150")
        popup.transient(self.app)
        popup.grab_set()
        ctk.CTkLabel(popup, text=entry["title"], font=T.BODY_BOLD,
                     text_color=self.theme["accent"]).pack(pady=(18, 4))
        box = ctk.CTkEntry(popup, width=320, font=T.MONO_FONT, justify="center",
                           fg_color=self.theme["panel"], border_color=self.theme["accent_dim"],
                           text_color=self.theme["text"])
        box.pack(pady=4)
        box.insert(0, password)
        box.configure(state="readonly")
        ctk.CTkButton(popup, text="Close", width=100, command=popup.destroy,
                      fg_color=self.theme["panel_hover"], hover_color=self.theme["accent_dim"],
                      text_color=self.theme["text"]).pack(pady=8)
        popup.bind("<Escape>", lambda _e: popup.destroy())

    def _copy(self, entry):
        password = self.app.cipher.decrypt(entry["password_enc"])
        self.app.clipboard_clear()
        self.app.clipboard_append(password)
        self._flash("Transmitted to clipboard. Self-destructs in 20 seconds.")
        if self._clipboard_job:
            self.app.after_cancel(self._clipboard_job)
        self._clipboard_job = self.app.after(CLIPBOARD_CLEAR_MS,
                                             lambda: self._clear_clipboard(password))

    def _clear_clipboard(self, expected):
        self._clipboard_job = None
        try:
            if self.app.clipboard_get() == expected:
                self.app.clipboard_clear()
                self._flash("Clipboard wiped. Leave no trace.")
        except Exception:
            pass

    def _flash(self, message):
        self.status.configure(text=message)
        self.after(4000, lambda: self.status.configure(text=""))
