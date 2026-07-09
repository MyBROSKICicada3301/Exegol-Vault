import customtkinter as ctk

import paths
import security
from db import Database, VaultDatabaseError
from ui import theme as T
from ui.screens import LoginScreen, SetupScreen, VaultScreen

ctk.set_appearance_mode("dark")


class ExegolVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.theme = T.load_theme()
        self.db = Database()
        self.cipher = None
        self._screen = None

        self.title("Exegol Vault")
        self.geometry("900x620")
        self.minsize(720, 520)
        self.configure(fg_color=self.theme["bg"])

        icon = paths.resource_dir() / "assets" / "icon.ico"
        if icon.exists():
            self.iconbitmap(str(icon))

        try:
            self.db.connect()
        except VaultDatabaseError as exc:
            self._show_db_error(str(exc))
            return

        if self.db.get_master() is None:
            self._show(SetupScreen)
        else:
            self._show(LoginScreen)

    def _show(self, screen_cls):
        if self._screen is not None:
            self._screen.destroy()
        self._screen = screen_cls(self)
        self._screen.pack(fill="both", expand=True)

    def _show_db_error(self, detail):
        frame = ctk.CTkFrame(self, fg_color=self.theme["bg"])
        frame.pack(fill="both", expand=True)
        box = ctk.CTkFrame(frame, fg_color="transparent")
        box.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(box, text="HYPERSPACE LINK FAILED", font=T.TITLE_FONT,
                     text_color=self.theme["danger"]).pack()
        ctk.CTkLabel(
            box,
            text="Could not reach the Exegol-Vault database.\n"
                 "Check that PostgreSQL is running and .env has the right credentials.",
            font=T.BODY_FONT, text_color=self.theme["text"],
        ).pack(pady=(10, 6))
        ctk.CTkLabel(box, text=detail.strip(), font=T.SUBTITLE_FONT,
                     text_color=self.theme["text_dim"], wraplength=560).pack()

    def create_master(self, password):
        salt = security.new_kdf_salt()
        self.db.set_master(security.hash_master_password(password), salt)
        self.cipher = security.VaultCipher(password, salt)
        self._show(VaultScreen)

    def unlock(self, password):
        master = self.db.get_master()
        if master is None:
            return False
        password_hash, salt = master
        if not security.verify_master_password(password, password_hash):
            return False
        self.cipher = security.VaultCipher(password, salt)
        self._show(VaultScreen)
        return True

    def lock(self):
        self.cipher = None
        self._show(LoginScreen)

    def toggle_theme(self):
        self.theme = T.other_side(self.theme)
        T.save_theme(self.theme)
        self.configure(fg_color=self.theme["bg"])
        self._show(VaultScreen)


if __name__ == "__main__":
    app = ExegolVaultApp()
    app.mainloop()
