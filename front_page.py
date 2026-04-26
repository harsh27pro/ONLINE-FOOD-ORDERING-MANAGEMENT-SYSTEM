import customtkinter as ctk
import auth_gui
from theme import *

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class FrontPage(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Foodly — Delivery in Minutes")
        self.after(0, lambda: self.state("zoomed"))
        self.configure(fg_color=BG)
        self._build_ui()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Left panel (dark hero) ──
        self.left = ctk.CTkFrame(self, fg_color=DARK_HEADER, corner_radius=0)
        self.left.place(relx=0, rely=0, relwidth=0.52, relheight=1)
        self._build_left()

        # ── Right panel (cards) ──
        self.right = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        self.right.place(relx=0.52, rely=0, relwidth=0.48, relheight=1)
        self._build_right()

    def _build_left(self):
        p = self.left

        # Top nav
        nav = ctk.CTkFrame(p, fg_color="transparent")
        nav.pack(fill="x", padx=40, pady=(30, 0))
        ctk.CTkLabel(nav, text="🍽  Foodly", font=("Georgia", 22, "bold"),
                     text_color=PRIMARY).pack(side="left")
        ctk.CTkButton(nav, text="Login / Sign up", width=130, height=38,
                      fg_color=PRIMARY, hover_color=PRIMARY_DARK,
                      font=FONT_BTN, corner_radius=20,
                      command=self.open_login).pack(side="right")

        # Hero text
        ctk.CTkLabel(p, text="Hungry?\nWe've got\nyou covered.",
                     font=("Georgia", 52, "bold"), text_color="#FFFFFF",
                     justify="left").pack(anchor="w", padx=50, pady=(80, 12))

        ctk.CTkLabel(p, text="Order food & groceries from the best\nrestaurants near you — delivered fast.",
                     font=("Helvetica", 15), text_color="#B0BEC5",
                     justify="left").pack(anchor="w", padx=50, pady=(0, 40))

        # Search bar
        search_frame = ctk.CTkFrame(p, fg_color="#263238", corner_radius=30)
        search_frame.pack(fill="x", padx=40, pady=(0, 10))
        ctk.CTkLabel(search_frame, text="🔍", font=("Helvetica", 18),
                     text_color=TEXT_MUTED).pack(side="left", padx=(20, 5), pady=18)
        ctk.CTkEntry(search_frame, placeholder_text="Search restaurant or dish...",
                     fg_color="transparent", border_width=0,
                     font=("Helvetica", 14), text_color="white",
                     placeholder_text_color="#78909C").pack(side="left", fill="x",
                     expand=True, pady=5, padx=(0, 20))

        # Stats row
        stats = ctk.CTkFrame(p, fg_color="transparent")
        stats.pack(fill="x", padx=50, pady=(40, 0))
        for val, lbl in [("500+", "Restaurants"), ("30 min", "Avg Delivery"), ("4.8★", "Avg Rating")]:
            blk = ctk.CTkFrame(stats, fg_color="transparent")
            blk.pack(side="left", expand=True)
            ctk.CTkLabel(blk, text=val, font=("Georgia", 26, "bold"),
                         text_color=PRIMARY).pack()
            ctk.CTkLabel(blk, text=lbl, font=FONT_SMALL,
                         text_color="#90A4AE").pack()

    def _build_right(self):
        p = self.right

        ctk.CTkLabel(p, text="What are you\ncravingsfor?",
                     font=("Georgia", 30, "bold"), text_color=TEXT,
                     justify="left").pack(anchor="w", padx=35, pady=(40, 5))
        ctk.CTkLabel(p, text="Choose a category to get started",
                     font=FONT_BODY, text_color=TEXT_MUTED).pack(anchor="w", padx=35, pady=(0, 25))

        categories = [
            ("🍕", "Food Delivery",  "From top restaurants\nUp to 60% off",  PRIMARY,   PRIMARY_DARK),
            ("🛒", "Instamart",      "Groceries in 10 mins\nUp to 50% off",  SUCCESS,   SUCCESS_DARK),
            ("🥂", "Dine Out",       "Table reservations\nExclusive deals",  "#8E24AA", "#6A1B9A"),
            ("🎂", "Sweets & Cakes", "Fresh bakery items\nOrder in advance", WARN,      "#EF6C00"),
        ]

        for emoji, title, subtitle, col, col_dark in categories:
            self._category_card(p, emoji, title, subtitle, col, col_dark)

    def _category_card(self, parent, emoji, title, subtitle, col, col_dark):
        card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=20,
                            border_width=1, border_color=BORDER)
        card.pack(fill="x", padx=30, pady=10)

        left = ctk.CTkFrame(card, fg_color="transparent")
        left.pack(side="left", padx=25, pady=22, fill="both", expand=True)

        ctk.CTkLabel(left, text=emoji, font=("Helvetica", 30)).pack(anchor="w")
        ctk.CTkLabel(left, text=title, font=FONT_SUBHEAD,
                     text_color=TEXT).pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(left, text=subtitle, font=FONT_SMALL,
                     text_color=TEXT_MUTED, justify="left").pack(anchor="w")

        ctk.CTkButton(card, text="→", width=50, height=50, corner_radius=25,
                      fg_color=col, hover_color=col_dark,
                      font=("Helvetica", 22, "bold"),
                      command=self.open_login).pack(side="right", padx=25)

    def open_login(self):
        self.destroy()
        auth_gui.AuthPage().mainloop()


if __name__ == "__main__":
    FrontPage().mainloop()
