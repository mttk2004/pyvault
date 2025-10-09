"""
Simple toast notifications for PyVault
"""

from PySide6.QtWidgets import QMessageBox


def show_success_toast(message, parent=None):
    """Show a success message"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle("Success")
    msg.setText(message)
    msg.exec()


def show_error_toast(message, parent=None):
    """Show an error message"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle("Error")
    msg.setText(message)
    msg.exec()


def show_warning_toast(message, parent=None):
    """Show a warning message"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle("Warning")
    msg.setText(message)
    msg.exec()


def show_info_toast(message, parent=None):
    """Show an info message"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle("Info")
    msg.setText(message)
    msg.exec()
