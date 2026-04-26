# review_gui.py — Foodly Ratings & Reviews
# Let users rate and review restaurants after delivery

import customtkinter as ctk
from database import get_connection
from tkinter import messagebox
from theme import *

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class ReviewPage(ctk.CTkToplevel):
    def __init__(self, parent, user_id: int, res_id: int, res_name: str, order_id: int = None):
        super().__init__(parent)
        self.user_id  = user_id
        self.res_id   = res_id
        self.res_name = res_name
        self.order_id = order_id
        self.rating   = 0
        self._star_btns = []

        self.title(f"Review — {res_name}")
        self.geometry("480x560")
        self.configure(fg_color=BG)
        self.attributes("-topmost", True)
        self.grab_set()
        self.lift()
        self._build_ui()
        self._load_existing()

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=DARK_HEADER, corner_radius=0, height=72)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        inner = ctk.CTkFrame(hdr, fg_color="transparent")
        inner.pack(fill="x", padx=25, pady=18)
        ctk.CTkLabel(inner, text="⭐  Rate & Review",
                     font=("Georgia", 20, "bold"), text_color="white").pack(side="left")
        ctk.CTkButton(inner, text="✕", width=36, height=32,
                      fg_color="#263238", hover_color=DANGER,
                      font=FONT_SUBHEAD, corner_radius=8,
                      command=self.destroy).pack(side="right")

        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=20,
                            border_width=1, border_color=BORDER)
        card.pack(fill="both", expand=True, padx=25, pady=20)

        # Restaurant name
        ctk.CTkLabel(card, text=self.res_name, font=("Georgia", 22, "bold"),
                     text_color=TEXT).pack(pady=(25, 5))
        ctk.CTkLabel(card, text="How was your experience?",
                     font=FONT_BODY, text_color=TEXT_MUTED).pack()

        # Star rating
        star_frame = ctk.CTkFrame(card, fg_color="transparent")
        star_frame.pack(pady=20)
        self._star_btns = []
        for i in range(1, 6):
            btn = ctk.CTkButton(star_frame, text="☆", font=("Helvetica", 36),
                                width=52, height=52,
                                fg_color="transparent", text_color=WARN,
                                hover_color="#FFF8E1",
                                command=lambda v=i: self._set_rating(v))
            btn.pack(side="left", padx=4)
            self._star_btns.append(btn)

        self.rating_label = ctk.CTkLabel(card, text="Tap a star to rate",
                                          font=FONT_BODY, text_color=TEXT_MUTED)
        self.rating_label.pack()

        # Separator
        ctk.CTkFrame(card, height=1, fg_color=BORDER).pack(fill="x", padx=25, pady=15)

        # Review text
        ctk.CTkLabel(card, text="Write a Review (optional)",
                     font=("Helvetica", 12, "bold"), text_color=TEXT_MUTED).pack(
                     anchor="w", padx=25)
        self.review_box = ctk.CTkTextbox(card, height=120, corner_radius=10,
                                          font=FONT_BODY, fg_color="#F8F9FA",
                                          border_width=1, border_color=BORDER,
                                          text_color=TEXT)
        self.review_box.pack(fill="x", padx=25, pady=(8, 0))

        # Submit
        ctk.CTkButton(card, text="Submit Review", height=50,
                      fg_color=PRIMARY, hover_color=PRIMARY_DARK,
                      font=("Helvetica", 15, "bold"), corner_radius=12,
                      command=self._submit).pack(fill="x", padx=25, pady=20)

    def _set_rating(self, value: int):
        self.rating = value
        labels = ["", "Poor 😞", "Fair 😐", "Good 🙂", "Great 😊", "Excellent 🤩"]
        self.rating_label.configure(text=labels[value], text_color=WARN)
        for i, btn in enumerate(self._star_btns):
            btn.configure(text="★" if i < value else "☆")

    def _load_existing(self):
        """Pre-fill if user already reviewed this restaurant."""
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT rating, review_text FROM reviews "
                "WHERE user_id=%s AND res_id=%s ORDER BY review_id DESC LIMIT 1",
                (self.user_id, self.res_id)
            )
            row = cur.fetchone()
            if row:
                self._set_rating(int(row["rating"]))
                if row["review_text"]:
                    self.review_box.insert("1.0", row["review_text"])
        except Exception:
            pass  # reviews table might not exist yet
        finally:
            conn.close()

    def _submit(self):
        if self.rating == 0:
            messagebox.showwarning("No Rating", "Please select a star rating before submitting.",
                                   parent=self)
            return
        review_text = self.review_box.get("1.0", "end").strip()
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            # Upsert review
            cur.execute(
                "INSERT INTO reviews (user_id, res_id, order_id, rating, review_text) "
                "VALUES (%s, %s, %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE rating=%s, review_text=%s",
                (self.user_id, self.res_id, self.order_id,
                 self.rating, review_text, self.rating, review_text)
            )
            # Update average rating on restaurant
            cur.execute(
                "UPDATE restaurants SET avg_rating = ("
                "  SELECT ROUND(AVG(rating), 1) FROM reviews WHERE res_id=%s"
                ") WHERE res_id=%s",
                (self.res_id, self.res_id)
            )
            conn.commit()
            messagebox.showinfo("Thank You! 🎉", "Your review has been submitted.", parent=self)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
        finally:
            conn.close()


class ReviewsListPage(ctk.CTkToplevel):
    """Show all reviews for a restaurant."""
    def __init__(self, parent, res_id: int, res_name: str):
        super().__init__(parent)
        self.res_id   = res_id
        self.res_name = res_name
        self.title(f"Reviews — {res_name}")
        self.geometry("520x600")
        self.configure(fg_color=BG)
        self.attributes("-topmost", True)
        self.grab_set()
        self.lift()
        self._build_ui()

    def _build_ui(self):
        hdr = ctk.CTkFrame(self, fg_color=DARK_HEADER, corner_radius=0, height=72)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        inner = ctk.CTkFrame(hdr, fg_color="transparent")
        inner.pack(fill="x", padx=25, pady=18)
        ctk.CTkLabel(inner, text=f"⭐  Reviews — {self.res_name}",
                     font=("Georgia", 18, "bold"), text_color="white").pack(side="left")
        ctk.CTkButton(inner, text="✕", width=36, height=32,
                      fg_color="#263238", hover_color=DANGER,
                      font=FONT_SUBHEAD, corner_radius=8,
                      command=self.destroy).pack(side="right")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=15)
        self._load_reviews(scroll)

    def _load_reviews(self, parent):
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT r.rating, r.review_text, u.full_name "
                "FROM reviews r JOIN users u ON r.user_id=u.user_id "
                "WHERE r.res_id=%s ORDER BY r.review_id DESC",
                (self.res_id,)
            )
            rows = cur.fetchall()
        except:
            rows = []
        finally:
            conn.close()

        if not rows:
            ctk.CTkLabel(parent, text="No reviews yet. Be the first!",
                         font=FONT_BODY, text_color=TEXT_MUTED).pack(pady=60)
            return

        for rv in rows:
            card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=14,
                                border_width=1, border_color=BORDER)
            card.pack(fill="x", pady=6)
            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=18, pady=(14, 4))
            ctk.CTkLabel(top, text=rv["full_name"], font=FONT_SUBHEAD,
                         text_color=TEXT).pack(side="left")
            stars = "★" * int(rv["rating"]) + "☆" * (5 - int(rv["rating"]))
            ctk.CTkLabel(top, text=stars, font=("Helvetica", 14),
                         text_color=WARN).pack(side="right")
            if rv["review_text"]:
                ctk.CTkLabel(card, text=rv["review_text"], font=FONT_BODY,
                             text_color=TEXT_MUTED, wraplength=440,
                             justify="left").pack(anchor="w", padx=18, pady=(0, 14))