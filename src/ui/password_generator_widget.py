"""
Compact Password Generator Widget for PyVault Tab Interface
A streamlined version of the password generator designed for embedded use.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QPushButton, QCheckBox, QSlider, QSpinBox, QLineEdit,
    QComboBox, QProgressBar, QGroupBox, QFrame, QScrollArea,
    QSizePolicy, QSpacerItem, QListWidget, QListWidgetItem,
    QMessageBox, QApplication, QSplitter, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPainter, QColor

from ..utils.password_generator import (
    PasswordGenerator, PasswordConfig, PasswordResult, PasswordStrength, PRESETS
)


class CompactStrengthMeter(QWidget):
    """Compact strength meter widget for tab interface."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.strength = PasswordStrength.VERY_WEAK
        self.entropy = 0.0
        self.setFixedHeight(20)
        self.setMinimumWidth(150)
    
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
        text = f"{generator.get_strength_description(self.strength)} ({self.entropy:.0f} bits)"
        painter.setPen(QColor("#1d1d1f"))
        
        # Use smaller font for compact display
        font = painter.font()
        font.setPixelSize(11)
        painter.setFont(font)
        
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)


class PasswordGeneratorWidget(QWidget):
    """Compact password generator widget for the main tab interface."""
    
    password_generated = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.generator = PasswordGenerator()
        self.config = PasswordConfig()
        self.current_result = None
        
        # Timer for real-time updates
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._generate_password)
        
        self._setup_ui()
        self._load_preset("High Security")  # Default preset
        self._generate_password()
    
    def _setup_ui(self):
        """Setup the compact widget UI."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)
        
        # Left side - Password display and controls
        left_widget = self._create_password_section()
        main_layout.addWidget(left_widget, 1)
        
        # Right side - Settings
        right_widget = self._create_settings_section()
        main_layout.addWidget(right_widget, 1)
    
    def _create_password_section(self):
        """Create the password display section."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("Password Generator")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: 600;
            color: #1d1d1f;
            padding: 10px 0;
        """)
        layout.addWidget(title)
        
        # Preset selection
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Preset:")
        preset_label.setStyleSheet("font-weight: 500; color: #495057;")
        self.presets_combo = QComboBox()
        self.presets_combo.addItems(["Custom"] + list(PRESETS.keys()))
        self.presets_combo.setCurrentText("High Security")
        self.presets_combo.currentTextChanged.connect(self._on_preset_changed)
        self.presets_combo.setStyleSheet(self._get_combo_style())
        
        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.presets_combo)
        preset_layout.addStretch()
        layout.addLayout(preset_layout)
        
        # Password display
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setStyleSheet("""
            QLineEdit {
                font-family: 'Monaco', 'Courier New', monospace;
                font-size: 14px;
                padding: 12px 16px;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background-color: #f8f9fa;
                color: #1d1d1f;
                selection-background-color: #e3f2fd;
            }
        """)
        layout.addWidget(self.password_display)
        
        # Strength meter
        self.strength_meter = CompactStrengthMeter()
        layout.addWidget(self.strength_meter)
        
        # Character distribution
        self.distribution_label = QLabel()
        self.distribution_label.setStyleSheet("""
            color: #6c757d;
            font-size: 11px;
            padding: 5px 0;
        """)
        layout.addWidget(self.distribution_label)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        self.copy_button = QPushButton("📋 Copy")
        self.copy_button.clicked.connect(self._copy_password)
        self.copy_button.setStyleSheet(self._get_secondary_button_style())
        
        self.regenerate_button = QPushButton("🔄 Generate")
        self.regenerate_button.clicked.connect(self._generate_password)
        self.regenerate_button.setStyleSheet(self._get_primary_button_style())
        
        actions_layout.addWidget(self.copy_button)
        actions_layout.addStretch()
        actions_layout.addWidget(self.regenerate_button)
        
        layout.addLayout(actions_layout)
        
        # Warnings
        self.warnings_label = QLabel()
        self.warnings_label.setStyleSheet("""
            color: #dc3545;
            font-size: 11px;
            font-weight: 500;
            padding: 5px 0;
        """)
        self.warnings_label.setWordWrap(True)
        layout.addWidget(self.warnings_label)
        
        layout.addStretch()
        
        return widget
    
    def _create_settings_section(self):
        """Create the settings section."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # Basic Settings Group
        basic_group = QGroupBox("Basic Settings")
        basic_group.setStyleSheet(self._get_group_style())
        basic_layout = QFormLayout(basic_group)
        basic_layout.setSpacing(12)
        
        # Length
        length_layout = QHBoxLayout()
        self.length_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_slider.setMinimum(4)
        self.length_slider.setMaximum(64)
        self.length_slider.setValue(16)
        self.length_slider.valueChanged.connect(self._on_length_changed)
        
        self.length_spinbox = QSpinBox()
        self.length_spinbox.setMinimum(4)
        self.length_spinbox.setMaximum(64)
        self.length_spinbox.setValue(16)
        self.length_spinbox.valueChanged.connect(self._on_length_spinbox_changed)
        self.length_spinbox.setFixedWidth(60)
        
        length_layout.addWidget(self.length_slider)
        length_layout.addWidget(self.length_spinbox)
        basic_layout.addRow("Length:", length_layout)
        
        # Character types
        self.uppercase_check = QCheckBox("Uppercase (A-Z)")
        self.uppercase_check.setChecked(True)
        self.uppercase_check.toggled.connect(self._on_config_changed)
        basic_layout.addRow(self.uppercase_check)
        
        self.lowercase_check = QCheckBox("Lowercase (a-z)")
        self.lowercase_check.setChecked(True)
        self.lowercase_check.toggled.connect(self._on_config_changed)
        basic_layout.addRow(self.lowercase_check)
        
        self.numbers_check = QCheckBox("Numbers (0-9)")
        self.numbers_check.setChecked(True)
        self.numbers_check.toggled.connect(self._on_config_changed)
        basic_layout.addRow(self.numbers_check)
        
        self.special_check = QCheckBox("Special Characters")
        self.special_check.setChecked(True)
        self.special_check.toggled.connect(self._on_config_changed)
        basic_layout.addRow(self.special_check)
        
        layout.addWidget(basic_group)
        
        # Advanced Settings Group (collapsible or compact)
        advanced_group = QGroupBox("Advanced Settings")
        advanced_group.setStyleSheet(self._get_group_style())
        advanced_layout = QFormLayout(advanced_group)
        advanced_layout.setSpacing(8)
        
        # Minimum constraints (simplified)
        constraints_layout = QGridLayout()
        
        constraints_layout.addWidget(QLabel("Min:"), 0, 0)
        constraints_layout.addWidget(QLabel("Upper"), 0, 1)
        constraints_layout.addWidget(QLabel("Lower"), 0, 2)
        constraints_layout.addWidget(QLabel("Num"), 0, 3)
        constraints_layout.addWidget(QLabel("Spec"), 0, 4)
        
        self.min_uppercase_spin = QSpinBox()
        self.min_uppercase_spin.setMaximum(32)
        self.min_uppercase_spin.setFixedWidth(50)
        self.min_uppercase_spin.valueChanged.connect(self._on_config_changed)
        
        self.min_lowercase_spin = QSpinBox()
        self.min_lowercase_spin.setMaximum(32)
        self.min_lowercase_spin.setFixedWidth(50)
        self.min_lowercase_spin.valueChanged.connect(self._on_config_changed)
        
        self.min_numbers_spin = QSpinBox()
        self.min_numbers_spin.setMaximum(32)
        self.min_numbers_spin.setFixedWidth(50)
        self.min_numbers_spin.valueChanged.connect(self._on_config_changed)
        
        self.min_special_spin = QSpinBox()
        self.min_special_spin.setMaximum(32)
        self.min_special_spin.setFixedWidth(50)
        self.min_special_spin.valueChanged.connect(self._on_config_changed)
        
        constraints_layout.addWidget(self.min_uppercase_spin, 1, 1)
        constraints_layout.addWidget(self.min_lowercase_spin, 1, 2)
        constraints_layout.addWidget(self.min_numbers_spin, 1, 3)
        constraints_layout.addWidget(self.min_special_spin, 1, 4)
        
        advanced_layout.addRow(constraints_layout)
        
        # Exclusion options
        self.exclude_ambiguous_check = QCheckBox("Exclude ambiguous (0,O,l,1)")
        self.exclude_ambiguous_check.toggled.connect(self._on_config_changed)
        advanced_layout.addRow(self.exclude_ambiguous_check)
        
        self.exclude_similar_check = QCheckBox("Exclude similar characters")
        self.exclude_similar_check.toggled.connect(self._on_config_changed)
        advanced_layout.addRow(self.exclude_similar_check)
        
        # Custom exclusions
        self.custom_excluded_input = QLineEdit()
        self.custom_excluded_input.setPlaceholderText("Characters to exclude...")
        self.custom_excluded_input.textChanged.connect(self._on_config_changed)
        self.custom_excluded_input.setStyleSheet(self._get_input_style())
        advanced_layout.addRow("Exclude:", self.custom_excluded_input)
        
        layout.addWidget(advanced_group)
        
        layout.addStretch()
        
        return widget
    
    def _on_preset_changed(self, preset_name: str):
        """Handle preset selection change."""
        if preset_name != "Custom":
            self._load_preset(preset_name)
    
    def _load_preset(self, preset_name: str):
        """Load a preset configuration."""
        if preset_name in PRESETS:
            self.config = PRESETS[preset_name]
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
        
        # Advanced settings
        self.min_uppercase_spin.setValue(self.config.min_uppercase)
        self.min_lowercase_spin.setValue(self.config.min_lowercase)
        self.min_numbers_spin.setValue(self.config.min_numbers)
        self.min_special_spin.setValue(self.config.min_special)
        
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
        
        self.config.min_uppercase = self.min_uppercase_spin.value()
        self.config.min_lowercase = self.min_lowercase_spin.value()
        self.config.min_numbers = self.min_numbers_spin.value()
        self.config.min_special = self.min_special_spin.value()
        
        self.config.exclude_ambiguous = self.exclude_ambiguous_check.isChecked()
        self.config.exclude_similar = self.exclude_similar_check.isChecked()
        self.config.custom_excluded = self.custom_excluded_input.text()
        
        # Set preset to Custom since user modified settings
        self.presets_combo.blockSignals(True)
        self.presets_combo.setCurrentText("Custom")
        self.presets_combo.blockSignals(False)
        
        # Trigger password generation with small delay
        self.update_timer.start(500)  # 500ms delay for real-time feel
    
    def _generate_password(self):
        """Generate a new password with current settings."""
        self.generator.update_config(self.config)
        self.current_result = self.generator.generate_password()
        
        # Update UI
        self.password_display.setText(self.current_result.password)
        self.strength_meter.set_strength(self.current_result.strength, self.current_result.entropy)
        
        # Update distribution display
        dist = self.current_result.character_distribution
        dist_text = f"Upper: {dist.get('uppercase', 0)}, Lower: {dist.get('lowercase', 0)}, Num: {dist.get('numbers', 0)}, Spec: {dist.get('special', 0)}"
        self.distribution_label.setText(dist_text)
        
        # Update warnings
        if self.current_result.warnings:
            self.warnings_label.setText("⚠️ " + "; ".join(self.current_result.warnings))
            self.warnings_label.show()
        else:
            self.warnings_label.hide()
    
    def _copy_password(self):
        """Copy the current password to clipboard."""
        if self.current_result and self.current_result.password:
            QApplication.clipboard().setText(self.current_result.password)
            self.copy_button.setText("✓ Copied!")
            QTimer.singleShot(2000, lambda: self.copy_button.setText("📋 Copy"))
    
    def get_current_password(self):
        """Get the current generated password."""
        return self.current_result.password if self.current_result else ""
    
    # Styling methods
    def _get_primary_button_style(self) -> str:
        """Get primary button style."""
        return """
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """
    
    def _get_secondary_button_style(self) -> str:
        """Get secondary button style."""
        return """
            QPushButton {
                background-color: transparent;
                color: #1d1d1f;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #f5f5f7;
                border-color: #adb5bd;
            }
        """
    
    def _get_group_style(self) -> str:
        """Get group box style."""
        return """
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                color: #1d1d1f;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding-top: 10px;
                margin-top: 6px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
    
    def _get_combo_style(self) -> str:
        """Get combobox style."""
        return """
            QComboBox {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 12px;
                background-color: white;
                font-size: 13px;
                color: #1d1d1f;
                min-width: 150px;
            }
            QComboBox:hover {
                border-color: #adb5bd;
            }
            QComboBox:focus {
                border-color: #2196f3;
            }
        """
    
    def _get_input_style(self) -> str:
        """Get input field style."""
        return """
            QLineEdit {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                color: #1d1d1f;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2196f3;
                outline: none;
            }
        """
