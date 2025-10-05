"""
PyVault Toast Notification System
Beautiful, non-blocking notifications for user feedback.
"""

from typing import Optional, List
from enum import Enum
from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect,
    QApplication, QFrame
)
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint, 
    Signal, QObject, QSequentialAnimationGroup, QParallelAnimationGroup
)
from PySide6.QtGui import QPainter, QColor, QPalette

from .design_system import Icons, tokens
from .theme_manager import theme_manager


class ToastType(Enum):
    SUCCESS = "success"
    ERROR = "error" 
    WARNING = "warning"
    INFO = "info"


class Toast(QFrame):
    """Individual toast notification widget"""
    
    closed = Signal()
    
    def __init__(self, message: str, toast_type: ToastType = ToastType.INFO, 
                 duration: int = 3000, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.message = message
        self.toast_type = toast_type
        self.duration = duration
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(350, 64)
        
        self._setup_ui()
        self._setup_animations()
        self._apply_theme()
        
        # Auto-close timer
        if duration > 0:
            QTimer.singleShot(duration, self.close_with_animation)
    
    def _setup_ui(self):
        """Setup the toast UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Icon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)
        
        # Message
        self.message_label = QLabel(self.message)
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet(f"""
            color: {tokens.colors.text_primary};
            font-family: {tokens.typography.font_family_sans};
            font-size: {tokens.typography.text_sm}px;
            font-weight: {tokens.typography.font_medium};
        """)
        layout.addWidget(self.message_label, 1)
        
        # Close button (small X)
        self.close_btn = QLabel("✕")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet(f"""
            color: {tokens.colors.text_tertiary};
            font-size: 12px;
            border-radius: 10px;
        """)
        self.close_btn.mousePressEvent = lambda e: self.close_with_animation()
        layout.addWidget(self.close_btn)
        
        # Mouse hover effect for close button
        def on_close_enter(event):
            self.close_btn.setStyleSheet(f"""
                color: {tokens.colors.text_primary};
                background-color: {tokens.colors.surface_hover};
                font-size: 12px;
                border-radius: 10px;
            """)
        
        def on_close_leave(event):
            self.close_btn.setStyleSheet(f"""
                color: {tokens.colors.text_tertiary};
                background-color: transparent;
                font-size: 12px;
                border-radius: 10px;
            """)
        
        self.close_btn.enterEvent = on_close_enter
        self.close_btn.leaveEvent = on_close_leave
    
    def _setup_animations(self):
        """Setup toast animations"""
        # Opacity effect
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        # Slide in animation
        self.slide_in_animation = QPropertyAnimation(self, b"pos")
        self.slide_in_animation.setDuration(300)
        self.slide_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Fade in animation
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(250)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Slide out animation
        self.slide_out_animation = QPropertyAnimation(self, b"pos")
        self.slide_out_animation.setDuration(250)
        self.slide_out_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        
        # Fade out animation
        self.fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(200)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        
        # Animation groups
        self.show_group = QParallelAnimationGroup()
        self.show_group.addAnimation(self.slide_in_animation)
        self.show_group.addAnimation(self.fade_in_animation)
        
        self.hide_group = QParallelAnimationGroup()
        self.hide_group.addAnimation(self.slide_out_animation)
        self.hide_group.addAnimation(self.fade_out_animation)
        self.hide_group.finished.connect(self._on_hide_finished)
    
    def _apply_theme(self):
        """Apply theme-based styling"""
        colors = tokens.colors
        
        # Get theme-specific colors based on toast type
        if self.toast_type == ToastType.SUCCESS:
            bg_color = colors.success
            icon_text = "✓"
        elif self.toast_type == ToastType.ERROR:
            bg_color = colors.error
            icon_text = "✕"
        elif self.toast_type == ToastType.WARNING:
            bg_color = colors.warning
            icon_text = "⚠"
        else:  # INFO
            bg_color = colors.info
            icon_text = "ⓘ"
        
        # Icon styling
        self.icon_label.setText(icon_text)
        self.icon_label.setStyleSheet(f"""
            color: white;
            background-color: {bg_color};
            border-radius: 12px;
            font-size: 14px;
            font-weight: bold;
        """)
        
        # Main toast styling with glassmorphism effect
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }}
        """)
    
    def show_animated(self, start_pos: QPoint, end_pos: QPoint):
        """Show toast with slide and fade animation"""
        self.move(start_pos)
        self.show()
        
        self.slide_in_animation.setStartValue(start_pos)
        self.slide_in_animation.setEndValue(end_pos)
        
        self.show_group.start()
    
    def close_with_animation(self):
        """Close toast with animation"""
        # Slide out to the right
        current_pos = self.pos()
        end_pos = QPoint(current_pos.x() + 400, current_pos.y())
        
        self.slide_out_animation.setStartValue(current_pos)
        self.slide_out_animation.setEndValue(end_pos)
        
        self.hide_group.start()
    
    def _on_hide_finished(self):
        """Handle hide animation finished"""
        self.closed.emit()
        self.hide()
        self.deleteLater()


class ToastManager(QObject):
    """Manages toast notifications and positioning"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_toasts: List[Toast] = []
        self.toast_spacing = 8
        self.margin = 20
    
    def show_toast(self, message: str, toast_type: ToastType = ToastType.INFO, 
                   duration: int = 3000, parent: Optional[QWidget] = None) -> Toast:
        """Show a toast notification"""
        # Use main application window as parent if none provided
        if parent is None:
            parent = QApplication.activeWindow()
        
        toast = Toast(message, toast_type, duration, parent)
        toast.closed.connect(lambda: self._on_toast_closed(toast))
        
        # Calculate position
        start_pos, end_pos = self._calculate_toast_position(toast, parent)
        
        # Add to active toasts and show
        self.active_toasts.append(toast)
        toast.show_animated(start_pos, end_pos)
        
        return toast
    
    def _calculate_toast_position(self, toast: Toast, parent: QWidget) -> tuple:
        """Calculate start and end positions for toast animation"""
        if parent:
            parent_rect = parent.geometry()
            # Position toasts in top-right corner of parent
            base_x = parent_rect.x() + parent_rect.width() - toast.width() - self.margin
            base_y = parent_rect.y() + self.margin
        else:
            # Fallback to screen positioning
            screen = QApplication.primaryScreen()
            screen_rect = screen.geometry()
            base_x = screen_rect.width() - toast.width() - self.margin
            base_y = self.margin
        
        # Calculate Y position based on existing toasts
        y_offset = sum(t.height() + self.toast_spacing for t in self.active_toasts)
        
        # Start position (slide in from right)
        start_pos = QPoint(base_x + 400, base_y + y_offset)
        # End position
        end_pos = QPoint(base_x, base_y + y_offset)
        
        return start_pos, end_pos
    
    def _on_toast_closed(self, toast: Toast):
        """Handle toast being closed"""
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)
            self._reposition_remaining_toasts()
    
    def _reposition_remaining_toasts(self):
        """Reposition remaining toasts after one is closed"""
        for i, toast in enumerate(self.active_toasts):
            if toast.parent():
                parent_rect = toast.parent().geometry()
                new_x = parent_rect.x() + parent_rect.width() - toast.width() - self.margin
                new_y = parent_rect.y() + self.margin + i * (toast.height() + self.toast_spacing)
            else:
                screen = QApplication.primaryScreen()
                screen_rect = screen.geometry()
                new_x = screen_rect.width() - toast.width() - self.margin
                new_y = self.margin + i * (toast.height() + self.toast_spacing)
            
            # Animate to new position
            animation = QPropertyAnimation(toast, b"pos")
            animation.setDuration(200)
            animation.setStartValue(toast.pos())
            animation.setEndValue(QPoint(new_x, new_y))
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            animation.start()
    
    def clear_all_toasts(self):
        """Close all active toasts"""
        for toast in self.active_toasts[:]:  # Copy list to avoid modification during iteration
            toast.close_with_animation()
    
    def show_success(self, message: str, duration: int = 3000, parent: Optional[QWidget] = None):
        """Show success toast"""
        return self.show_toast(message, ToastType.SUCCESS, duration, parent)
    
    def show_error(self, message: str, duration: int = 4000, parent: Optional[QWidget] = None):
        """Show error toast"""
        return self.show_toast(message, ToastType.ERROR, duration, parent)
    
    def show_warning(self, message: str, duration: int = 3500, parent: Optional[QWidget] = None):
        """Show warning toast"""
        return self.show_toast(message, ToastType.WARNING, duration, parent)
    
    def show_info(self, message: str, duration: int = 3000, parent: Optional[QWidget] = None):
        """Show info toast"""
        return self.show_toast(message, ToastType.INFO, duration, parent)


# Global toast manager instance
toast_manager = ToastManager()


# Convenience functions for easy access
def show_success_toast(message: str, duration: int = 3000, parent: Optional[QWidget] = None):
    """Show a success toast notification"""
    return toast_manager.show_success(message, duration, parent)


def show_error_toast(message: str, duration: int = 4000, parent: Optional[QWidget] = None):
    """Show an error toast notification"""
    return toast_manager.show_error(message, duration, parent)


def show_warning_toast(message: str, duration: int = 3500, parent: Optional[QWidget] = None):
    """Show a warning toast notification"""
    return toast_manager.show_warning(message, duration, parent)


def show_info_toast(message: str, duration: int = 3000, parent: Optional[QWidget] = None):
    """Show an info toast notification"""
    return toast_manager.show_info(message, duration, parent)


def clear_all_toasts():
    """Clear all active toast notifications"""
    toast_manager.clear_all_toasts()
