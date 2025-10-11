# src/ui/password_generator_dialog.py
import tkinter as tk
from tkinter import ttk
from src.utils import password_generator

class PasswordGeneratorDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Password Generator")
        self.transient(parent)
        self.grab_set()

        self.generated_password = tk.StringVar()
        self.result = None

        self._setup_widgets()
        self._generate_and_display_password()

        self.wait_window(self)

    def _setup_widgets(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(expand=True, fill=tk.BOTH)

        # Result display
        result_frame = ttk.Frame(frame, padding=5, style='secondary.TFrame')
        result_frame.pack(fill=tk.X, pady=(0, 15))
        
        password_label = ttk.Label(result_frame, textvariable=self.generated_password, font=("-size", 14, "bold"), anchor="center")
        password_label.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10, pady=10)

        copy_button = ttk.Button(result_frame, text="Copy", command=self._copy_password, style="secondary.TButton")
        copy_button.pack(side=tk.RIGHT, padx=10)

        # Options
        options_frame = ttk.LabelFrame(frame, text="Options", padding=15)
        options_frame.pack(fill=tk.X)

        self.length_var = tk.IntVar(value=16)
        self.uppercase_var = tk.BooleanVar(value=True)
        self.lowercase_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)

        # Length
        ttk.Label(options_frame, text="Password Length:").grid(row=0, column=0, sticky=tk.W)
        length_spinbox = ttk.Spinbox(options_frame, from_=8, to=128, textvariable=self.length_var, width=5, command=self._generate_and_display_password)
        length_spinbox.grid(row=0, column=1, sticky=tk.W)

        # Checkboxes
        ttk.Checkbutton(options_frame, text="Include Uppercase (A-Z)", variable=self.uppercase_var, command=self._generate_and_display_password).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Checkbutton(options_frame, text="Include Lowercase (a-z)", variable=self.lowercase_var, command=self._generate_and_display_password).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Checkbutton(options_frame, text="Include Digits (0-9)", variable=self.digits_var, command=self._generate_and_display_password).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Checkbutton(options_frame, text="Include Symbols (!@#$)", variable=self.symbols_var, command=self._generate_and_display_password).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Main action buttons
        button_frame = ttk.Frame(frame, padding=(0, 15, 0, 0))
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Regenerate", command=self._generate_and_display_password, style="secondary.TButton").pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Use Password", command=self._on_use_password, style="success.TButton").pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=10)

    def _generate_and_display_password(self):
        try:
            password = password_generator.generate_password(
                length=self.length_var.get(),
                include_uppercase=self.uppercase_var.get(),
                include_lowercase=self.lowercase_var.get(),
                include_digits=self.digits_var.get(),
                include_symbols=self.symbols_var.get()
            )
            self.generated_password.set(password)
        except ValueError as e:
            self.generated_password.set(str(e))

    def _copy_password(self):
        import pyperclip
        pyperclip.copy(self.generated_password.get())
        from src.ui.toast import show_success
        show_success("Password copied to clipboard!")

    def _on_use_password(self):
        self.result = self.generated_password.get()
        self.destroy()
