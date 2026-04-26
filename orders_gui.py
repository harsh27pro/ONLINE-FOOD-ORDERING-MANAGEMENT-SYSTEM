import customtkinter as ctk
from database import get_connection
from tkinter import messagebox
from theme import *

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class OrdersPage(ctk.CTkToplevel):
    def __init__(self, user_id, open_menu_callback=None):
        super().__init__()
        self.user_id = user_id
        self.open_menu_callback = open_menu_callback
        self.title("Foodly — My Orders")
        self.geometry("720x820")
        self.configure(fg_color=BG)
        self.attributes("-topmost", True)
        self.grab_set()
        self.lift()
        self._build_ui()

    def _build_ui(self):
        # ── Header ───────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=DARK_HEADER, corner_radius=0, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="x", padx=30, pady=22)
        ctk.CTkLabel(inner, text="📜  My Orders", font=("Georgia", 22, "bold"),
                     text_color="white").pack(side="left")
        ctk.CTkButton(inner, text="✕ Close", width=80, height=32,
                      fg_color="#263238", hover_color=DANGER,
                      font=FONT_SMALL, corner_radius=8,
                      command=self.destroy).pack(side="right")

        # ── Stats bar ─────────────────────────────────────────────────────────
        stats = self._fetch_stats()
        stat_bar = ctk.CTkFrame(self, fg_color=PRIMARY, corner_radius=0, height=56)
        stat_bar.pack(fill="x")
        stat_bar.pack_propagate(False)
        for val, lbl in [(str(stats["total"]), "Total Orders"),
                         (f"₹{stats['spent']:.0f}", "Total Spent"),
                         (str(stats["delivered"]), "Delivered")]:
            blk = ctk.CTkFrame(stat_bar, fg_color="transparent")
            blk.pack(side="left", expand=True)
            ctk.CTkLabel(blk, text=f"{val}  {lbl}",
                         font=("Helvetica", 13, "bold"),
                         text_color="white").pack(pady=16)

        # ── Scroll area ───────────────────────────────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.scroll.pack(fill="both", expand=True, padx=25, pady=15)
        self._load_orders()

    def _fetch_stats(self):
        conn = get_connection()
        stats = {"total": 0, "spent": 0, "delivered": 0}
        if not conn:
            return stats
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT COUNT(*) AS total, "
                "COALESCE(SUM(total_amount),0) AS spent, "
                "SUM(order_status='Delivered') AS delivered "
                "FROM orders WHERE user_id=%s",
                (self.user_id,)
            )
            row = cur.fetchone()
            if row:
                stats = {"total": row["total"] or 0,
                         "spent": float(row["spent"] or 0),
                         "delivered": int(row["delivered"] or 0)}
        except:
            pass
        finally:
            conn.close()
        return stats

    def _load_orders(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT o.order_id, o.total_amount, o.order_status, "
                "o.res_id, r.res_name "
                "FROM orders o JOIN restaurants r ON o.res_id = r.res_id "
                "WHERE o.user_id=%s ORDER BY o.order_id DESC",
                (self.user_id,)
            )
            orders = cur.fetchall()
        except:
            orders = []
        finally:
            conn.close()

        if not orders:
            ctk.CTkLabel(self.scroll, text="🍽  No orders yet!\nStart ordering from top restaurants.",
                         font=FONT_HEADING, text_color=TEXT_MUTED,
                         justify="center").pack(pady=80)
            return

        for order in orders:
            self._order_card(order)

    def _order_card(self, order):
        st = order["order_status"]
        st_color = {"Pending": WARN, "Delivered": SUCCESS,
                    "Cancelled": DANGER, "Preparing": PRIMARY,
                    "On the Way": "#7B1FA2"}.get(st, TEXT_MUTED)
        st_icon  = {"Pending": "🕐", "Delivered": "✅",
                    "Cancelled": "❌", "Preparing": "👨‍🍳",
                    "On the Way": "🛵"}.get(st, "•")

        card = ctk.CTkFrame(self.scroll, fg_color=CARD, corner_radius=16,
                            border_width=1, border_color=BORDER)
        card.pack(fill="x", pady=8)

        # Top row
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(16, 6))
        ctk.CTkLabel(top, text=order["res_name"], font=FONT_SUBHEAD,
                     text_color=TEXT).pack(side="left")
        status_badge = ctk.CTkFrame(top, fg_color=st_color, corner_radius=8)
        status_badge.pack(side="right")
        ctk.CTkLabel(status_badge, text=f"{st_icon}  {st}",
                     font=("Helvetica", 12, "bold"), text_color="white").pack(padx=10, pady=4)

        # Meta row
        meta = ctk.CTkFrame(card, fg_color="transparent")
        meta.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkLabel(meta, text=f"Order #{order['order_id']}",
                     font=FONT_SMALL, text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkLabel(meta, text=f"₹{order['total_amount']}",
                     font=("Georgia", 16, "bold"), text_color=SUCCESS).pack(side="right")

        # Separator
        ctk.CTkFrame(card, height=1, fg_color=BORDER).pack(fill="x")

        # Action row
        actions = ctk.CTkFrame(card, fg_color="#FAFAFA", corner_radius=0)
        actions.pack(fill="x", padx=0, pady=0)

        if st == "Pending":
            ctk.CTkButton(actions, text="🗺 Track Order", height=38,
                          fg_color="transparent", text_color=PRIMARY,
                          hover_color="#E3F2FD", font=FONT_BTN, corner_radius=0,
                          command=lambda o_id=order["order_id"]: self._track(o_id)).pack(
                          side="left", padx=10, pady=8)
            ctk.CTkButton(actions, text="❌ Cancel", height=38,
                          fg_color="transparent", text_color=DANGER,
                          hover_color="#FFEBEE", font=FONT_BTN, corner_radius=0,
                          command=lambda o_id=order["order_id"]: self._cancel(o_id)).pack(
                          side="left", padx=4, pady=8)
            ctk.CTkButton(actions, text="✅ Mark Delivered",
                          height=38, fg_color="transparent", text_color=TEXT_MUTED,
                          hover_color=BORDER, font=FONT_SMALL, corner_radius=0,
                          command=lambda o_id=order["order_id"]: self._mark_delivered(o_id)).pack(
                          side="right", padx=10, pady=8)

        elif st == "Delivered":
            ctk.CTkButton(actions, text="⭐ Rate & Review", height=38,
                          fg_color="transparent", text_color=WARN,
                          hover_color="#FFF8E1", font=FONT_BTN, corner_radius=0,
                          command=lambda o=order: self._review(o)).pack(
                          side="left", padx=10, pady=8)
            if self.open_menu_callback:
                ctk.CTkButton(actions, text="🔁 Reorder", height=38,
                              fg_color="transparent", text_color=SUCCESS,
                              hover_color="#E8F5E9", font=FONT_BTN, corner_radius=0,
                              command=lambda o=order: self._reorder(o)).pack(
                              side="left", padx=4, pady=8)
            ctk.CTkButton(actions, text="🗺 Track", height=38,
                          fg_color="transparent", text_color=TEXT_MUTED,
                          hover_color=BORDER, font=FONT_SMALL, corner_radius=0,
                          command=lambda o_id=order["order_id"]: self._track(o_id)).pack(
                          side="right", padx=10, pady=8)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _track(self, order_id):
        from order_tracker import OrderTrackerPage
        OrderTrackerPage(self, order_id, self.user_id)

    def _review(self, order):
        from review_gui import ReviewPage
        ReviewPage(self, self.user_id, order["res_id"],
                   order["res_name"], order["order_id"])

    def _reorder(self, order):
        self.destroy()
        if self.open_menu_callback:
            self.open_menu_callback(order["res_id"], order["res_name"])

    def _cancel(self, order_id):
        if messagebox.askyesno("Cancel Order", "Are you sure you want to cancel this order?"):
            self._update_status(order_id, "Cancelled")

    def _mark_delivered(self, order_id):
        if messagebox.askyesno("Admin Action", "Mark this order as Delivered?"):
            self._update_status(order_id, "Delivered")

    def _update_status(self, order_id, status):
        conn = get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("UPDATE orders SET order_status=%s WHERE order_id=%s",
                            (status, order_id))
                conn.commit()
            except:
                pass
            finally:
                conn.close()
        self._load_orders()


if __name__ == "__main__":
    root = ctk.CTk()
    ctk.CTkButton(root, text="Open Orders", command=lambda: OrdersPage(1)).pack(pady=20)
    root.mainloop()