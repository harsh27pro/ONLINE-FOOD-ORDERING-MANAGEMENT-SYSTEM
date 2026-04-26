import customtkinter as ctk
from database import get_connection
from tkinter import messagebox
from theme import *
from image_utils import get_avatar_image

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class ProfilePage(ctk.CTkToplevel):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.title("Foodly — My Profile")
        self.geometry("480x660")
        self.configure(fg_color=BG)
        self.lift()
        self.focus_force()
        self.grab_set()
        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=DARK_HEADER, corner_radius=0, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="x", padx=30, pady=22)
        ctk.CTkLabel(inner, text="👤  My Profile", font=("Georgia", 22, "bold"),
                     text_color="white").pack(side="left")
        ctk.CTkButton(inner, text="✕ Close", width=80, height=32,
                      fg_color="#263238", hover_color=DANGER,
                      font=FONT_SMALL, corner_radius=8,
                      command=self.destroy).pack(side="right")

        # Avatar area (taller so image shows fully)
        avatar_frame = ctk.CTkFrame(self, fg_color=BG, corner_radius=0, height=120)
        avatar_frame.pack(fill="x")
        avatar_frame.pack_propagate(False)

        # Will be replaced once user data loads
        self._avatar_frame = avatar_frame
        self._avatar_lbl = ctk.CTkLabel(avatar_frame, text="👤", font=("Helvetica", 40))
        self._avatar_lbl.place(relx=0.5, rely=0.5, anchor="center")

        # Info card
        self.card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=20,
                                 border_width=1, border_color=BORDER)
        self.card.pack(fill="both", expand=True, padx=25, pady=(10, 20))
        self._load_data()

    def _load_data(self):
        conn = get_connection()
        if not conn:
            messagebox.showerror("Error", "Database connection failed.")
            return
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT full_name,email,phone,address FROM users WHERE user_id=%s",
                        (self.user_id,))
            user = cur.fetchone()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            user = None
        finally:
            conn.close()

        if not user:
            ctk.CTkLabel(self.card, text="User not found.", text_color=DANGER).pack(pady=50)
            return

        # ── Load avatar with user initials ──────────────────────────────────
        def _set_avatar(name=user["full_name"], frame=self._avatar_frame,
                        placeholder=self._avatar_lbl):
            try:
                photo = get_avatar_image(name, size=(90, 90))
                placeholder.destroy()
                lbl = ctk.CTkLabel(frame, image=photo, text="", fg_color="transparent")
                lbl.image = photo
                lbl.place(relx=0.5, rely=0.5, anchor="center")
            except Exception as e:
                print(f"Avatar error: {e}")

        self.after(50, _set_avatar)

        # ── User info fields ────────────────────────────────────────────────
        fields = [
            ("👤  Full Name",        user["full_name"]),
            ("📧  Email",            user["email"]),
            ("📞  Phone",            user["phone"] or "—"),
            ("📍  Delivery Address", user["address"] or "—"),
        ]

        for i, (label, value) in enumerate(fields):
            row = ctk.CTkFrame(self.card, fg_color="transparent")
            row.pack(fill="x", padx=25, pady=(16 if i == 0 else 4, 0))
            ctk.CTkLabel(row, text=label, font=("Helvetica", 12, "bold"),
                         text_color=TEXT_MUTED).pack(anchor="w")
            ctk.CTkLabel(row, text=str(value), font=("Helvetica", 15),
                         text_color=TEXT, wraplength=380, justify="left").pack(anchor="w")
            if i < len(fields) - 1:
                ctk.CTkFrame(self.card, height=1, fg_color=BORDER).pack(
                    fill="x", padx=25, pady=(12, 0))
