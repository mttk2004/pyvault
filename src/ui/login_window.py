# src/ui/login_window.py
import tkinter as tk
from tkinter import ttk

class LoginWindow(tk.Toplevel):
    def __init__(self, parent, vault_exists=False, on_unlock=None):
        super().__init__(parent)

        self.title("PyVault")
        self.geometry("350x180")
        self.resizable(False, False)

        self.on_unlock = on_unlock # Callback function
        self.parent = parent

        title_text = "Unlock Vault" if vault_exists else "Create New Vault"
        button_text = "Unlock" if vault_exists else "Create"

        # --- Widgets ---
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text=title_text, style='primary.TLabel', font=("-size", 16)).pack(pady=(0, 10))

        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*")
        password_entry.pack(fill=tk.X, pady=5)
        password_entry.focus_set()

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))

        unlock_button = ttk.Button(button_frame, text=button_text, command=self._handle_unlock, style='primary.TButton')
        unlock_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        quit_button = ttk.Button(button_frame, text="Quit", command=self.parent.destroy, style='secondary.TButton')
        quit_button.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0))

        # Bind the Enter key to the unlock action
        self.bind('<Return>', lambda event: self._handle_unlock())

    def _handle_unlock(self):
        password = self.password_var.get()
        if password and self.on_unlock:
            self.on_unlock(password)

    def show_unlock_feedback(self, success: bool, message: str = ""):
        """Shows feedback to the user after an unlock attempt."""
        if not success:
            from src.ui.toast import show_error
            show_error(message or "Incorrect password.")
        # On success, the main window will be shown by the UI manager.
