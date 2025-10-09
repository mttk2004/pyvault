"""
Password Generator Dialog for PyVault
Professional UI for generating customized secure passwords.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QPushButton, QCheckBox, QSlider, QSpinBox, QLineEdit,
    QTextEdit, QComboBox, QProgressBar, QGroupBox, QFrame, QScrollArea,
    QSizePolicy, QSpacerItem, QTabWidget, QWidget, QListWidget, QListWidgetItem,
    QMessageBox, QApplication
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QPalette

from ..utils.password_generator import (
    PasswordGenerator, PasswordConfig, PasswordResult, PasswordStrength, PRESETS
)

class StrengthMeter(QWidget):
    """Custom strength meter widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.strength = PasswordStrength.VERY_WEAK
        self.entropy = 0.0
        self.setFixedHeight(30)
        self.setMinimumWidth(200)
    
    def set_strength(self, strength: PasswordStrength, entropy: float):
        """Update the strength display."""
        self.strength = strength
        self.entropy = entropy
        self.update()
    
    def paintEvent(self, event):
        """Custom paint event for strength meter."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor("#f1f3f5"))
        
        # Strength bar
        if self.strength != PasswordStrength.VERY_WEAK:
            generator = PasswordGenerator()
            color = QColor(generator.get_strength_color(self.strength))
            
            # Calculate width based on strength
            strength_width = (self.strength.value / 5.0) * self.width()
            painter.fillRect(0, 0, int(strength_width), self.height(), color)
        
        # Text
        generator = PasswordGenerator()
        text = f"{generator.get_strength_description(self.strength)} ({self.entropy:.1f} bits)"
        painter.setPen(QColor("#1d1d1f"))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)

class PasswordHistoryWidget(QWidget):
    """Widget for displaying password generation history."""
    
    password_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the history widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("Recent Passwords")
        title.setStyleSheet("font-weight: 600; font-size: 14px; color: #1d1d1f;")
        layout.addWidget(title)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(120)
        self.history_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
                font-family: 'Monaco', 'Courier New', monospace;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f3f5;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1565c0;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
        """)
        self.history_list.itemClicked.connect(self._on_history_selected)
        layout.addWidget(self.history_list)
    
    def add_password(self, password: str):
        """Add a password to the history."""
        if password and password not in self.history:
            self.history.insert(0, password)
            # Keep only last 5 passwords
            self.history = self.history[:5]
            self._refresh_list()
    
    def _refresh_list(self):
        """Refresh the history list."""
        self.history_list.clear()
        for password in self.history:
            # Show first 20 chars with ellipsis if longer
            display_text = password if len(password) <= 20 else password[:17] + "..."
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, password)
            item.setToolTip(f"Click to select this password\nLength: {len(password)} characters")
            self.history_list.addItem(item)
    
    def _on_history_selected(self, item):
        """Handle history item selection."""
        password = item.data(Qt.ItemDataRole.UserRole)
        self.password_selected.emit(password)

class PasswordGeneratorDialog(QDialog):
    """Professional password generator dialog."""
    
    password_generated = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.generator = PasswordGenerator()
        self.config = PasswordConfig()
        self.current_result = None
        self.session_presets = {}  # For custom presets during session
        
        self.setWindowTitle("Password Generator")
        self.setModal(True)
        self.setMinimumSize(700, 800)
        self.resize(800, 900)
        
        # Timer for real-time updates
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._generate_password)
        
        self._setup_ui()
        self._load_preset("High Security")  # Default preset
        self._generate_password()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Password Generator")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 600;
            color: #1d1d1f;
            padding: 10px 0;
        """)
        main_layout.addWidget(title)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-bottom: none;
                border-radius: 6px 6px 0 0;
                padding: 10px 20px;
                margin-right: 2px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #2196f3;
            }
            QTabBar::tab:hover {
                background-color: #e9ecef;
            }
        """)
        
        # Tab 1: Basic Settings
        basic_tab = self._create_basic_tab()
        self.tabs.addTab(basic_tab, "Basic")
        
        # Tab 2: Advanced Settings
        advanced_tab = self._create_advanced_tab()
        self.tabs.addTab(advanced_tab, "Advanced")
        
        main_layout.addWidget(self.tabs)
        
        # Password preview section
        preview_section = self._create_preview_section()
        main_layout.addWidget(preview_section)
        
        # History section
        self.history_widget = PasswordHistoryWidget()
        self.history_widget.password_selected.connect(self._use_selected_password)
        main_layout.addWidget(self.history_widget)
        
        # Buttons
        button_layout = self._create_button_layout()
        main_layout.addLayout(button_layout)
    
    def _create_basic_tab(self) -> QWidget:
        """Create the basic settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # Presets section
        presets_group = QGroupBox("Presets")
        presets_layout = QVBoxLayout(presets_group)
        
        self.presets_combo = QComboBox()
        self.presets_combo.addItems(["Custom"] + list(PRESETS.keys()))
        self.presets_combo.currentTextChanged.connect(self._on_preset_changed)
        self.presets_combo.setStyleSheet(self._get_combo_style())
        presets_layout.addWidget(self.presets_combo)
        
        layout.addWidget(presets_group)
        
        # Length section
        length_group = QGroupBox("Password Length")
        length_layout = QFormLayout(length_group)
        
        self.length_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_slider.setRange(4, 128)
        self.length_slider.setValue(16)
        self.length_slider.valueChanged.connect(self._on_length_changed)
        
        self.length_spinbox = QSpinBox()
        self.length_spinbox.setRange(4, 128)
        self.length_spinbox.setValue(16)
        self.length_spinbox.valueChanged.connect(self._on_length_spinbox_changed)
        
        length_controls = QHBoxLayout()
        length_controls.addWidget(self.length_slider, 1)
        length_controls.addWidget(self.length_spinbox)
        
        length_layout.addRow("Length:", length_controls)
        layout.addWidget(length_group)
        
        # Character types section
        char_types_group = QGroupBox("Character Types")
        char_types_layout = QVBoxLayout(char_types_group)
        
        self.uppercase_check = QCheckBox("Uppercase letters (A-Z)")
        self.uppercase_check.setChecked(True)
        self.uppercase_check.stateChanged.connect(self._on_config_changed)
        
        self.lowercase_check = QCheckBox("Lowercase letters (a-z)")
        self.lowercase_check.setChecked(True)
        self.lowercase_check.stateChanged.connect(self._on_config_changed)
        
        self.numbers_check = QCheckBox("Numbers (0-9)")
        self.numbers_check.setChecked(True)
        self.numbers_check.stateChanged.connect(self._on_config_changed)
        
        self.special_check = QCheckBox("Special characters")
        self.special_check.setChecked(True)
        self.special_check.stateChanged.connect(self._on_config_changed)
        
        for checkbox in [self.uppercase_check, self.lowercase_check, self.numbers_check, self.special_check]:
            checkbox.setStyleSheet(self._get_checkbox_style())
            char_types_layout.addWidget(checkbox)
        
        layout.addWidget(char_types_group)
        
        # Special characters customization
        special_group = QGroupBox("Special Characters")
        special_layout = QFormLayout(special_group)
        
        self.special_chars_input = QLineEdit("!@#$%^&*()_+-=[]{}|;:,.<>?")
        self.special_chars_input.textChanged.connect(self._on_config_changed)
        self.special_chars_input.setStyleSheet(self._get_input_style())
        special_layout.addRow("Characters:", self.special_chars_input)
        
        layout.addWidget(special_group)
        
        layout.addStretch()
        return tab
    
    def _create_advanced_tab(self) -> QWidget:
        """Create the advanced settings tab."""
        tab = QWidget()
        scroll = QScrollArea()
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setSpacing(20)
        
        # Minimum constraints
        min_group = QGroupBox("Minimum Character Requirements")
        min_layout = QFormLayout(min_group)
        
        self.min_uppercase_spin = QSpinBox()
        self.min_uppercase_spin.setRange(0, 32)
        self.min_uppercase_spin.valueChanged.connect(self._on_config_changed)
        min_layout.addRow("Min uppercase:", self.min_uppercase_spin)
        
        self.min_lowercase_spin = QSpinBox()
        self.min_lowercase_spin.setRange(0, 32)
        self.min_lowercase_spin.valueChanged.connect(self._on_config_changed)
        min_layout.addRow("Min lowercase:", self.min_lowercase_spin)
        
        self.min_numbers_spin = QSpinBox()
        self.min_numbers_spin.setRange(0, 32)
        self.min_numbers_spin.valueChanged.connect(self._on_config_changed)
        min_layout.addRow("Min numbers:", self.min_numbers_spin)
        
        self.min_special_spin = QSpinBox()
        self.min_special_spin.setRange(0, 32)
        self.min_special_spin.valueChanged.connect(self._on_config_changed)
        min_layout.addRow("Min special:", self.min_special_spin)
        
        for spinbox in [self.min_uppercase_spin, self.min_lowercase_spin, 
                       self.min_numbers_spin, self.min_special_spin]:
            spinbox.setStyleSheet(self._get_spinbox_style())
        
        layout.addWidget(min_group)
        
        # Maximum constraints
        max_group = QGroupBox("Maximum Character Limits (optional)")
        max_layout = QFormLayout(max_group)
        
        self.max_uppercase_spin = QSpinBox()
        self.max_uppercase_spin.setRange(0, 128)
        self.max_uppercase_spin.setSpecialValueText("No limit")
        self.max_uppercase_spin.valueChanged.connect(self._on_config_changed)
        max_layout.addRow("Max uppercase:", self.max_uppercase_spin)
        
        self.max_lowercase_spin = QSpinBox()
        self.max_lowercase_spin.setRange(0, 128)
        self.max_lowercase_spin.setSpecialValueText("No limit")
        self.max_lowercase_spin.valueChanged.connect(self._on_config_changed)
        max_layout.addRow("Max lowercase:", self.max_lowercase_spin)
        
        self.max_numbers_spin = QSpinBox()
        self.max_numbers_spin.setRange(0, 128)
        self.max_numbers_spin.setSpecialValueText("No limit")
        self.max_numbers_spin.valueChanged.connect(self._on_config_changed)
        max_layout.addRow("Max numbers:", self.max_numbers_spin)
        
        self.max_special_spin = QSpinBox()
        self.max_special_spin.setRange(0, 128)
        self.max_special_spin.setSpecialValueText("No limit")
        self.max_special_spin.valueChanged.connect(self._on_config_changed)
        max_layout.addRow("Max special:", self.max_special_spin)
        
        for spinbox in [self.max_uppercase_spin, self.max_lowercase_spin,
                       self.max_numbers_spin, self.max_special_spin]:
            spinbox.setStyleSheet(self._get_spinbox_style())
        
        layout.addWidget(max_group)
        
        # Character exclusions
        exclusions_group = QGroupBox("Character Exclusions")
        exclusions_layout = QVBoxLayout(exclusions_group)
        
        self.exclude_ambiguous_check = QCheckBox("Exclude ambiguous characters (0, O, l, 1, I)")
        self.exclude_ambiguous_check.stateChanged.connect(self._on_config_changed)
        self.exclude_ambiguous_check.setStyleSheet(self._get_checkbox_style())
        exclusions_layout.addWidget(self.exclude_ambiguous_check)
        
        self.exclude_similar_check = QCheckBox("Exclude similar characters (il1, O0, etc.)")
        self.exclude_similar_check.stateChanged.connect(self._on_config_changed)
        self.exclude_similar_check.setStyleSheet(self._get_checkbox_style())
        exclusions_layout.addWidget(self.exclude_similar_check)
        
        # Custom exclusions
        custom_layout = QFormLayout()
        self.custom_excluded_input = QLineEdit()
        self.custom_excluded_input.setPlaceholderText("Enter characters to exclude")
        self.custom_excluded_input.textChanged.connect(self._on_config_changed)
        self.custom_excluded_input.setStyleSheet(self._get_input_style())
        custom_layout.addRow("Custom exclusions:", self.custom_excluded_input)
        exclusions_layout.addLayout(custom_layout)
        
        layout.addWidget(exclusions_group)
        
        layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        tab_layout = QVBoxLayout(tab)
        tab_layout.addWidget(scroll)
        
        return tab
    
    def _create_preview_section(self) -> QWidget:
        """Create the password preview section."""
        group = QGroupBox("Generated Password")
        layout = QVBoxLayout(group)
        
        # Password display
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setStyleSheet("""
            QLineEdit {
                font-family: 'Monaco', 'Courier New', monospace;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background-color: #f8f9fa;
                color: #1d1d1f;
                selection-background-color: #e3f2fd;
            }
        """)
        layout.addWidget(self.password_display)
        
        # Password actions
        actions_layout = QHBoxLayout()
        
        self.copy_button = QPushButton("📋 Copy")
        self.copy_button.clicked.connect(self._copy_password)
        self.copy_button.setStyleSheet(self._get_secondary_button_style())
        
        self.regenerate_button = QPushButton("🔄 Generate New")
        self.regenerate_button.clicked.connect(self._generate_password)
        self.regenerate_button.setStyleSheet(self._get_primary_button_style())
        
        actions_layout.addWidget(self.copy_button)
        actions_layout.addStretch()
        actions_layout.addWidget(self.regenerate_button)
        
        layout.addLayout(actions_layout)
        
        # Strength meter
        self.strength_meter = StrengthMeter()
        layout.addWidget(self.strength_meter)
        
        # Character distribution
        self.distribution_label = QLabel()
        self.distribution_label.setStyleSheet("""
            color: #6c757d;
            font-size: 12px;
            padding: 5px 0;
        """)
        layout.addWidget(self.distribution_label)
        
        # Warnings
        self.warnings_label = QLabel()
        self.warnings_label.setStyleSheet("""
            color: #dc3545;
            font-size: 12px;
            font-weight: 500;
            padding: 5px 0;
        """)
        self.warnings_label.setWordWrap(True)
        layout.addWidget(self.warnings_label)
        
        return group
    
    def _create_button_layout(self) -> QHBoxLayout:
        """Create the dialog button layout."""
        layout = QHBoxLayout()
        
        # Save preset button
        self.save_preset_button = QPushButton("Save Preset")
        self.save_preset_button.clicked.connect(self._save_custom_preset)
        self.save_preset_button.setStyleSheet(self._get_secondary_button_style())
        layout.addWidget(self.save_preset_button)
        
        layout.addStretch()
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet(self._get_secondary_button_style())
        layout.addWidget(cancel_button)
        
        # Use password button
        self.use_button = QPushButton("Use This Password")
        self.use_button.clicked.connect(self._use_password)
        self.use_button.setStyleSheet(self._get_primary_button_style())
        self.use_button.setDefault(True)
        layout.addWidget(self.use_button)
        
        return layout
    
    def _on_preset_changed(self, preset_name: str):
        """Handle preset selection change."""
        if preset_name != "Custom":
            self._load_preset(preset_name)
    
    def _load_preset(self, preset_name: str):
        """Load a preset configuration."""
        if preset_name in PRESETS:
            self.config = PRESETS[preset_name]
        elif preset_name in self.session_presets:
            self.config = self.session_presets[preset_name]
        else:
            return
        
        self._update_ui_from_config()
        self._generate_password()
    
    def _update_ui_from_config(self):
        """Update UI controls based on current config."""
        # Block signals to prevent recursive updates
        widgets = []
        widgets.extend(self.findChildren(QCheckBox))
        widgets.extend(self.findChildren(QSpinBox))
        widgets.extend(self.findChildren(QSlider))
        widgets.extend(self.findChildren(QLineEdit))
        
        for widget in widgets:
            widget.blockSignals(True)
        
        # Basic settings
        self.length_slider.setValue(self.config.length)
        self.length_spinbox.setValue(self.config.length)
        self.uppercase_check.setChecked(self.config.use_uppercase)
        self.lowercase_check.setChecked(self.config.use_lowercase)
        self.numbers_check.setChecked(self.config.use_numbers)
        self.special_check.setChecked(self.config.use_special)
        self.special_chars_input.setText(self.config.special_chars)
        
        # Advanced settings
        self.min_uppercase_spin.setValue(self.config.min_uppercase)
        self.min_lowercase_spin.setValue(self.config.min_lowercase)
        self.min_numbers_spin.setValue(self.config.min_numbers)
        self.min_special_spin.setValue(self.config.min_special)
        
        self.max_uppercase_spin.setValue(self.config.max_uppercase or 0)
        self.max_lowercase_spin.setValue(self.config.max_lowercase or 0)
        self.max_numbers_spin.setValue(self.config.max_numbers or 0)
        self.max_special_spin.setValue(self.config.max_special or 0)
        
        self.exclude_ambiguous_check.setChecked(self.config.exclude_ambiguous)
        self.exclude_similar_check.setChecked(self.config.exclude_similar)
        self.custom_excluded_input.setText(self.config.custom_excluded)
        
        # Unblock signals
        for widget in widgets:
            widget.blockSignals(False)
    
    def _on_length_changed(self, value: int):
        """Handle length slider change."""
        self.length_spinbox.blockSignals(True)
        self.length_spinbox.setValue(value)
        self.length_spinbox.blockSignals(False)
        self._on_config_changed()
    
    def _on_length_spinbox_changed(self, value: int):
        """Handle length spinbox change."""
        self.length_slider.blockSignals(True)
        self.length_slider.setValue(value)
        self.length_slider.blockSignals(False)
        self._on_config_changed()
    
    def _on_config_changed(self):
        """Handle configuration changes."""
        # Update config from UI
        self.config.length = self.length_spinbox.value()
        self.config.use_uppercase = self.uppercase_check.isChecked()
        self.config.use_lowercase = self.lowercase_check.isChecked()
        self.config.use_numbers = self.numbers_check.isChecked()
        self.config.use_special = self.special_check.isChecked()
        self.config.special_chars = self.special_chars_input.text()
        
        self.config.min_uppercase = self.min_uppercase_spin.value()
        self.config.min_lowercase = self.min_lowercase_spin.value()
        self.config.min_numbers = self.min_numbers_spin.value()
        self.config.min_special = self.min_special_spin.value()
        
        self.config.max_uppercase = self.max_uppercase_spin.value() or None
        self.config.max_lowercase = self.max_lowercase_spin.value() or None
        self.config.max_numbers = self.max_numbers_spin.value() or None
        self.config.max_special = self.max_special_spin.value() or None
        
        self.config.exclude_ambiguous = self.exclude_ambiguous_check.isChecked()
        self.config.exclude_similar = self.exclude_similar_check.isChecked()
        self.config.custom_excluded = self.custom_excluded_input.text()
        
        # Set preset to Custom since user modified settings
        self.presets_combo.blockSignals(True)
        self.presets_combo.setCurrentText("Custom")
        self.presets_combo.blockSignals(False)
        
        # Trigger password generation with small delay
        self.update_timer.start(300)  # 300ms delay for real-time feel
    
    def _generate_password(self):
        """Generate a new password with current settings."""
        self.generator.update_config(self.config)
        self.current_result = self.generator.generate_password()
        
        # Update UI
        self.password_display.setText(self.current_result.password)
        self.strength_meter.set_strength(self.current_result.strength, self.current_result.entropy)
        
        # Update distribution display
        dist = self.current_result.character_distribution
        dist_text = f"Uppercase: {dist.get('uppercase', 0)}, Lowercase: {dist.get('lowercase', 0)}, Numbers: {dist.get('numbers', 0)}, Special: {dist.get('special', 0)}"
        self.distribution_label.setText(dist_text)
        
        # Update warnings
        if self.current_result.warnings:
            self.warnings_label.setText("⚠️ " + "; ".join(self.current_result.warnings))
            self.warnings_label.show()
        else:
            self.warnings_label.hide()
        
        # Enable/disable use button
        self.use_button.setEnabled(bool(self.current_result.password))
    
    def _copy_password(self):
        """Copy the current password to clipboard."""
        if self.current_result and self.current_result.password:
            QApplication.clipboard().setText(self.current_result.password)
            self.copy_button.setText("✓ Copied!")
            QTimer.singleShot(2000, lambda: self.copy_button.setText("📋 Copy"))
    
    def _use_password(self):
        """Use the current password."""
        if self.current_result and self.current_result.password:
            self.history_widget.add_password(self.current_result.password)
            self.password_generated.emit(self.current_result.password)
            self.accept()
    
    def _use_selected_password(self, password: str):
        """Use a password selected from history."""
        self.password_display.setText(password)
        self.password_generated.emit(password)
        self.accept()
    
    def _save_custom_preset(self):
        """Save current settings as a custom preset."""
        from PySide6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(
            self,
            "Save Preset",
            "Enter preset name:",
            text="My Custom Preset"
        )
        
        if ok and name.strip():
            name = name.strip()
            if name in PRESETS:
                QMessageBox.warning(self, "Error", "Cannot overwrite built-in presets.")
                return
            
            # Save to session presets
            self.session_presets[name] = PasswordConfig(
                length=self.config.length,
                use_uppercase=self.config.use_uppercase,
                use_lowercase=self.config.use_lowercase,
                use_numbers=self.config.use_numbers,
                use_special=self.config.use_special,
                min_uppercase=self.config.min_uppercase,
                min_lowercase=self.config.min_lowercase,
                min_numbers=self.config.min_numbers,
                min_special=self.config.min_special,
                max_uppercase=self.config.max_uppercase,
                max_lowercase=self.config.max_lowercase,
                max_numbers=self.config.max_numbers,
                max_special=self.config.max_special,
                exclude_ambiguous=self.config.exclude_ambiguous,
                exclude_similar=self.config.exclude_similar,
                custom_excluded=self.config.custom_excluded,
                special_chars=self.config.special_chars
            )
            
            # Add to presets combo
            self.presets_combo.addItem(name)
            self.presets_combo.setCurrentText(name)
            
            QMessageBox.information(self, "Success", f"Preset '{name}' saved!")
    
    # Styling methods
    def _get_primary_button_style(self) -> str:
        """Get primary button style."""
        return """
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #9e9e9e;
            }
        """
    
    def _get_secondary_button_style(self) -> str:
        """Get secondary button style."""
        return """
            QPushButton {
                background-color: transparent;
                color: #1d1d1f;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #f5f5f7;
                border-color: #adb5bd;
            }
            QPushButton:pressed {
                background-color: #e9ecef;
            }
        """
    
    def _get_checkbox_style(self) -> str:
        """Get checkbox style."""
        return """
            QCheckBox {
                font-size: 14px;
                color: #1d1d1f;
                spacing: 8px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #2196f3;
                border-color: #2196f3;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
        """
    
    def _get_combo_style(self) -> str:
        """Get combobox style."""
        return """
            QComboBox {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                font-size: 14px;
                color: #1d1d1f;
                min-width: 200px;
            }
            QComboBox:hover {
                border-color: #adb5bd;
            }
            QComboBox:focus {
                border-color: #2196f3;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """
    
    def _get_input_style(self) -> str:
        """Get input field style."""
        return """
            QLineEdit {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: #1d1d1f;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2196f3;
                outline: none;
            }
        """
    
    def _get_spinbox_style(self) -> str:
        """Get spinbox style."""
        return """
            QSpinBox {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: #1d1d1f;
                background-color: white;
                min-width: 80px;
            }
            QSpinBox:focus {
                border-color: #2196f3;
            }
        """
