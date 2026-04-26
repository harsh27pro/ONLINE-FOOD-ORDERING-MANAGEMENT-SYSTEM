# order_tracker.py — Foodly Live Order Tracker
# Animated step-by-step order status timeline

import customtkinter as ctk
from database import get_connection
from theme import *

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

STEPS = [
    ("🧾", "Order Placed",       "We've received your order!"),
    ("👨‍🍳", "Preparing Food",    "The restaurant is cooking your order."),
    ("🛵", "Out for Delivery",   "Your delivery partner is on the way!"),
    ("✅", "Delivered",          "Enjoy your meal! 😋"),
]

STATUS_TO_STEP = {
    "Pending":    0,
    "Confirmed":  1,
    "Preparing":  1,
    "On the Way": 2,
    "Delivered":  3,
    "Cancelled":  -1,
}


class OrderTrackerPage(ctk.CTkToplevel):
    def __init__(self, parent, order_id: int, user_id: int):
        super().__init__(parent)
        self.order_id = order_id
        self.user_id  = user_id
        self.title(f"Foodly — Track Order #{order_id}")
        self.geometry("520x720")
        self.configure(fg_color=BG)
        self.attributes("-topmost", True)
        self.grab_set()
        self.lift()
        self._build_ui()
        self._auto_refresh()

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=DARK_HEADER, corner_radius=0, height=72)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        inner = ctk.CTkFrame(hdr, fg_color="transparent")
        inner.pack(fill="x", padx=25, pady=18)
        ctk.CTkLabel(inner, text=f"🛵  Track Order #{self.order_id}",
                     font=("Georgia", 20, "bold"), text_color="white").pack(side="left")
        ctk.CTkButton(inner, text="✕", width=36, height=32,
                      fg_color="#263238", hover_color=DANGER,
                      font=FONT_SUBHEAD, corner_radius=8,
                      command=self.destroy).pack(side="right")

        # ETA banner
        self.eta_frame = ctk.CTkFrame(self, fg_color=PRIMARY, corner_radius=0, height=60)
        self.eta_frame.pack(fill="x")
        self.eta_frame.pack_propagate(False)
        self.eta_label = ctk.CTkLabel(self.eta_frame,
                                      text="⏱  Estimated Delivery: 30-40 minutes",
                                      font=("Helvetica", 14, "bold"), text_color="white")
        self.eta_label.pack(expand=True)

        # Timeline card
        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=20,
                            border_width=1, border_color=BORDER)
        card.pack(fill="both", expand=True, padx=25, pady=20)

        ctk.CTkLabel(card, text="Order Status", font=FONT_HEADING,
                     text_color=TEXT).pack(pady=(20, 5), padx=25, anchor="w")

        self.timeline_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.timeline_frame.pack(fill="both", expand=True, padx=25, pady=10)

        self._draw_timeline(self._fetch_step())

        # Refresh button
        ctk.CTkButton(card, text="🔄  Refresh Status", height=42,
                      fg_color="#F8F9FA", text_color=PRIMARY,
                      hover_color="#FFF3E0", font=FONT_BTN,
                      border_width=2, border_color=PRIMARY,
                      corner_radius=10, command=self._manual_refresh).pack(
                      fill="x", padx=25, pady=(0, 20))

    def _fetch_step(self):
        conn = get_connection()
        if not conn:
            return 0
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT order_status FROM orders WHERE order_id=%s", (self.order_id,))
            row = cur.fetchone()
            if row:
                status = row["order_status"]
                if status == "Cancelled":
                    return -1
                return STATUS_TO_STEP.get(status, 0)
        except:
            pass
        finally:
            conn.close()
        return 0

    def _draw_timeline(self, active_step: int):
        for w in self.timeline_frame.winfo_children():
            w.destroy()

        if active_step == -1:
            ctk.CTkLabel(self.timeline_frame,
                         text="❌  This order has been cancelled.",
                         font=FONT_SUBHEAD, text_color=DANGER).pack(pady=40)
            self.eta_label.configure(text="Order Cancelled")
            self.eta_frame.configure(fg_color=DANGER)
            return

        for i, (icon, title, subtitle) in enumerate(STEPS):
            is_done   = i < active_step
            is_active = i == active_step

            # Step row
            row = ctk.CTkFrame(self.timeline_frame, fg_color="transparent")
            row.pack(fill="x", pady=6)

            # Left: connector + circle
            left_col = ctk.CTkFrame(row, fg_color="transparent", width=50)
            left_col.pack(side="left", fill="y")
            left_col.pack_propagate(False)

            # Vertical line above (except first)
            if i > 0:
                line_color = SUCCESS if is_done or is_active else BORDER
                ctk.CTkFrame(left_col, fg_color=line_color,
                             width=3, height=20).place(relx=0.5, rely=0, anchor="n")

            # Circle indicator
            if is_done:
                circle_color = SUCCESS
                circle_text  = "✓"
                text_col     = "white"
            elif is_active:
                circle_color = PRIMARY
                circle_text  = icon
                text_col     = "white"
            else:
                circle_color = BORDER
                circle_text  = icon
                text_col     = TEXT_MUTED

            circle = ctk.CTkFrame(left_col, fg_color=circle_color,
                                  width=44, height=44, corner_radius=22)
            circle.pack(anchor="center", pady=(22 if i > 0 else 8, 0))
            circle.pack_propagate(False)
            ctk.CTkLabel(circle, text=circle_text,
                         font=("Helvetica", 16, "bold"),
                         text_color=text_col).place(relx=0.5, rely=0.5, anchor="center")

            # Vertical line below (except last)
            if i < len(STEPS) - 1:
                line_color = SUCCESS if is_done else BORDER
                ctk.CTkFrame(left_col, fg_color=line_color,
                             width=3, height=20).place(relx=0.5, rely=1, anchor="s")

            # Right: text content
            right_col = ctk.CTkFrame(row, fg_color="transparent")
            right_col.pack(side="left", fill="both", expand=True, padx=18, pady=8)

            title_font = ("Helvetica", 15, "bold") if is_active else FONT_BODY
            title_col  = TEXT if (is_done or is_active) else TEXT_MUTED

            ctk.CTkLabel(right_col, text=title, font=title_font,
                         text_color=title_col).pack(anchor="w")
            if is_active:
                ctk.CTkLabel(right_col, text=subtitle,
                             font=FONT_SMALL, text_color=PRIMARY).pack(anchor="w", pady=(2, 0))
            elif is_done:
                ctk.CTkLabel(right_col, text="Completed ✓",
                             font=FONT_SMALL, text_color=SUCCESS).pack(anchor="w", pady=(2, 0))

        # Update ETA label
        if active_step == 3:
            self.eta_label.configure(text="🎉  Your order has been delivered!")
            self.eta_frame.configure(fg_color=SUCCESS)
        elif active_step == 2:
            self.eta_label.configure(text="⏱  Arriving in 10-15 minutes")
        elif active_step == 1:
            self.eta_label.configure(text="⏱  Estimated Delivery: 25-35 minutes")
        else:
            self.eta_label.configure(text="⏱  Estimated Delivery: 30-40 minutes")

    def _manual_refresh(self):
        self._draw_timeline(self._fetch_step())

    def _auto_refresh(self):
        """Auto-refresh every 30 seconds."""
        try:
            if self.winfo_exists():
                self._draw_timeline(self._fetch_step())
                self.after(30000, self._auto_refresh)
        except Exception:
            pass


if __name__ == "__main__":
    root = ctk.CTk()
    ctk.CTkButton(root, text="Track", command=lambda: OrderTrackerPage(root, 1, 1)).pack(pady=20)
    root.mainloop()