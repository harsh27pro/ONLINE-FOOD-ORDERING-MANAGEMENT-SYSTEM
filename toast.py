# toast.py — Foodly Custom Toast Notifications
# Replaces plain messagebox with sleek animated toasts

import customtkinter as ctk
from theme import *


class Toast(ctk.CTkToplevel):
    """
    A sleek, auto-dismissing notification toast.
    Usage:
        Toast(parent, "Order placed! 🎉", kind="success")
        Toast(parent, "Item added to cart", kind="info")
        Toast(parent, "Invalid coupon code", kind="error")
    """
    COLORS = {
        "success": (SUCCESS,       "#E8F5E9", "✅"),
        "error":   (DANGER,        "#FFEBEE", "❌"),
        "info":    (PRIMARY,       "#FFF3E0", "ℹ️"),
        "warning": (WARN,          "#FFF8E1", "⚠️"),
    }

    def __init__(self, parent, message: str, kind: str = "info", duration: int = 3000):
        super().__init__(parent)
        self.overrideredirect(True)          # no title bar
        self.attributes("-topmost", True)
        self.configure(fg_color=CARD)

        accent, bg, icon = self.COLORS.get(kind, self.COLORS["info"])

        # Accent bar on left
        bar = ctk.CTkFrame(self, fg_color=accent, width=6, corner_radius=0)
        bar.pack(side="left", fill="y")

        body = ctk.CTkFrame(self, fg_color=bg, corner_radius=0)
        body.pack(side="left", fill="both", expand=True)

        inner = ctk.CTkFrame(body, fg_color="transparent")
        inner.pack(padx=16, pady=14)

        ctk.CTkLabel(inner, text=icon, font=("Helvetica", 20)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(inner, text=message, font=FONT_BODY, text_color=TEXT,
                     wraplength=280, justify="left").pack(side="left")

        # Position: bottom-right of parent
        self.update_idletasks()
        pw = parent.winfo_rootx() + parent.winfo_width()
        ph = parent.winfo_rooty() + parent.winfo_height()
        tw = self.winfo_reqwidth()
        th = self.winfo_reqheight()
        x = pw - tw - 30
        y = ph - th - 50
        self.geometry(f"+{x}+{y}")

        # Auto dismiss
        self.after(duration, self.destroy)


def show_toast(parent, message: str, kind: str = "info", duration: int = 3000):
    """Convenience wrapper."""
    try:
        Toast(parent, message, kind=kind, duration=duration)
    except Exception:
        pass  # silently ignore if parent is gone