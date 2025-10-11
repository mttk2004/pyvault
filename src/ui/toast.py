# src/ui/toast.py
from ttkbootstrap.toast import ToastNotification

def show_toast(title, message, duration=3000, bootstyle='default', parent=None):
    """A wrapper for showing toast notifications."""
    toast = ToastNotification(
        title=title,
        message=message,
        duration=duration,
        bootstyle=bootstyle,
        position=(10, 10, 'se') # Show in the bottom-right corner
    )
    toast.show_toast()

def show_success(message, title="Success", parent=None):
    show_toast(title, message, bootstyle='success', parent=parent)

def show_error(message, title="Error", parent=None):
    show_toast(title, message, bootstyle='danger', parent=parent)

def show_info(message, title="Info", parent=None):
    show_toast(title, message, bootstyle='info', parent=parent)
