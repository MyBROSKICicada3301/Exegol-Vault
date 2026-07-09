import customtkinter as ctk

from security import generate_password
from ui import theme as T


class HolocronDialog(ctk.CTkToplevel):
    def __init__(self, parent, theme, entry=None):
        super().__init__(parent)
        self.theme = theme
        self.result = None
        editing = entry is not None

        self.title("Modify Holocron" if editing else "Forge Holocron")
        self.configure(fg_color=theme["bg"])
        self.geometry("460x560")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        ctk.CTkLabel(
            self,
            text="MODIFY HOLOCRON" if editing else "FORGE A NEW HOLOCRON",
            font=("Segoe UI", 18, "bold"),
            text_color=theme["accent"],
        ).pack(pady=(18, 12))

        form = ctk.CTkFrame(self, fg_color=theme["panel"], corner_radius=12)
        form.pack(fill="both", expand=True, padx=18, pady=(0, 14))

        self.title_entry = self._field(form, "Title *", entry["title"] if editing else "")
        self.user_entry = self._field(form, "Username / Email", entry["username"] if editing else "")

        ctk.CTkLabel(form, text="Password *", font=T.BODY_BOLD,
                     text_color=self.theme["text_dim"], anchor="w").pack(fill="x", padx=16, pady=(10, 2))
        pw_row = ctk.CTkFrame(form, fg_color="transparent")
        pw_row.pack(fill="x", padx=16)
        self.pw_entry = ctk.CTkEntry(pw_row, font=T.MONO_FONT, show="•",
                                     fg_color=theme["bg"], border_color=theme["accent_dim"])
        self.pw_entry.pack(side="left", fill="x", expand=True)
        if editing:
            self.pw_entry.insert(0, entry["password"])
        self._pw_shown = False
        self.eye_btn = ctk.CTkButton(pw_row, text="👁", width=36, command=self._toggle_pw,
                                     fg_color=theme["panel_hover"], hover_color=theme["accent_dim"],
                                     text_color=theme["text"])
        self.eye_btn.pack(side="left", padx=(6, 0))
        ctk.CTkButton(pw_row, text="🎲 Astromech", width=110, command=self._generate,
                      fg_color=theme["accent"], hover_color=theme["accent_hover"],
                      text_color=theme["on_accent"], font=T.BODY_BOLD).pack(side="left", padx=(6, 0))

        self.url_entry = self._field(form, "URL", entry["url"] if editing else "")

        ctk.CTkLabel(form, text="Notes", font=T.BODY_BOLD,
                     text_color=self.theme["text_dim"], anchor="w").pack(fill="x", padx=16, pady=(10, 2))
        self.notes_box = ctk.CTkTextbox(form, height=80, font=T.BODY_FONT,
                                        fg_color=theme["bg"], border_color=theme["accent_dim"],
                                        border_width=1, text_color=theme["text"])
        self.notes_box.pack(fill="x", padx=16, pady=(0, 12))
        if editing:
            self.notes_box.insert("1.0", entry["notes"])

        self.error_label = ctk.CTkLabel(self, text="", font=T.SUBTITLE_FONT,
                                        text_color=theme["danger"])
        self.error_label.pack()

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=(0, 16))
        ctk.CTkButton(btn_row, text="Save to Archives", command=self._save,
                      fg_color=theme["accent"], hover_color=theme["accent_hover"],
                      text_color=theme["on_accent"], font=T.BODY_BOLD, width=160).pack(side="left", padx=6)
        ctk.CTkButton(btn_row, text="Abort", command=self.destroy,
                      fg_color=theme["panel_hover"], hover_color=theme["accent_dim"],
                      text_color=theme["text"], width=100).pack(side="left", padx=6)

        self.title_entry.focus_set()
        self.bind("<Return>", lambda _e: self._save())
        self.bind("<Escape>", lambda _e: self.destroy())

    def _field(self, parent, label, value):
        ctk.CTkLabel(parent, text=label, font=T.BODY_BOLD,
                     text_color=self.theme["text_dim"], anchor="w").pack(fill="x", padx=16, pady=(10, 2))
        entry = ctk.CTkEntry(parent, font=T.BODY_FONT, fg_color=self.theme["bg"],
                             border_color=self.theme["accent_dim"], text_color=self.theme["text"])
        entry.pack(fill="x", padx=16)
        entry.insert(0, value)
        return entry

    def _toggle_pw(self):
        self._pw_shown = not self._pw_shown
        self.pw_entry.configure(show="" if self._pw_shown else "•")

    def _generate(self):
        self.pw_entry.delete(0, "end")
        self.pw_entry.insert(0, generate_password())

    def _save(self):
        title = self.title_entry.get().strip()
        password = self.pw_entry.get()
        if not title:
            self.error_label.configure(text="A holocron needs a title.")
            return
        if not password:
            self.error_label.configure(text="A holocron without a secret is no holocron.")
            return
        self.result = {
            "title": title,
            "username": self.user_entry.get().strip(),
            "password": password,
            "url": self.url_entry.get().strip(),
            "notes": self.notes_box.get("1.0", "end").strip(),
        }
        self.destroy()


class Order66Dialog(ctk.CTkToplevel):
    def __init__(self, parent, theme, entry_title):
        super().__init__(parent)
        self.confirmed = False

        self.title("Order 66")
        self.configure(fg_color=theme["bg"])
        self.geometry("400x190")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        ctk.CTkLabel(self, text="EXECUTE ORDER 66?", font=("Segoe UI", 18, "bold"),
                     text_color=theme["danger"]).pack(pady=(22, 6))
        ctk.CTkLabel(self, text=f"'{entry_title}' will be destroyed.\nThis cannot be undone.",
                     font=T.BODY_FONT, text_color=theme["text"]).pack(pady=(0, 14))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack()
        ctk.CTkButton(row, text="Execute", command=self._confirm, width=120,
                      fg_color=theme["danger"], hover_color="#ff4d54",
                      text_color="#ffffff", font=T.BODY_BOLD).pack(side="left", padx=6)
        ctk.CTkButton(row, text="Spare it", command=self.destroy, width=120,
                      fg_color=theme["panel_hover"], hover_color=theme["accent_dim"],
                      text_color=theme["text"]).pack(side="left", padx=6)

        self.bind("<Escape>", lambda _e: self.destroy())

    def _confirm(self):
        self.confirmed = True
        self.destroy()
