# wishlist.py — Foodly Favourites / Wishlist
# Toggle heart on restaurants; show a dedicated favourites page

import customtkinter as ctk
from database import get_connection
from theme import *

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


def is_favourite(user_id: int, res_id: int) -> bool:
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM wishlist WHERE user_id=%s AND res_id=%s",
                    (user_id, res_id))
        return cur.fetchone() is not None
    except:
        return False
    finally:
        conn.close()


def toggle_favourite(user_id: int, res_id: int) -> bool:
    """Returns True if now favourited, False if removed."""
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM wishlist WHERE user_id=%s AND res_id=%s",
                    (user_id, res_id))
        if cur.fetchone():
            cur.execute("DELETE FROM wishlist WHERE user_id=%s AND res_id=%s",
                        (user_id, res_id))
            conn.commit()
            return False
        else:
            cur.execute("INSERT INTO wishlist (user_id, res_id) VALUES (%s, %s)",
                        (user_id, res_id))
            conn.commit()
            return True
    except:
        return False
    finally:
        conn.close()


def get_favourites(user_id: int) -> list:
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT r.* FROM restaurants r "
            "JOIN wishlist w ON r.res_id=w.res_id "
            "WHERE w.user_id=%s",
            (user_id,)
        )
        return cur.fetchall()
    except:
        return []
    finally:
        conn.close()


class FavouritesPage(ctk.CTkToplevel):
    def __init__(self, parent, user_id: int, open_menu_callback=None):
        super().__init__(parent)
        self.user_id = user_id
        self.open_menu_callback = open_menu_callback
        self.title("Foodly — My Favourites")
        self.geometry("580x640")
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
        ctk.CTkLabel(inner, text="❤️  My Favourites",
                     font=("Georgia", 20, "bold"), text_color="white").pack(side="left")
        ctk.CTkButton(inner, text="✕", width=36, height=32,
                      fg_color="#263238", hover_color=DANGER,
                      font=FONT_SUBHEAD, corner_radius=8,
                      command=self.destroy).pack(side="right")

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=15)
        self._load()

    def _load(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        restaurants = get_favourites(self.user_id)
        if not restaurants:
            ctk.CTkLabel(self.scroll,
                         text="💔  No favourites yet!\nHeart a restaurant to save it here.",
                         font=FONT_HEADING, text_color=TEXT_MUTED,
                         justify="center").pack(pady=80)
            return
        for res in restaurants:
            self._fav_card(res)

    def _fav_card(self, res):
        card = ctk.CTkFrame(self.scroll, fg_color=CARD, corner_radius=16,
                            border_width=1, border_color=BORDER)
        card.pack(fill="x", pady=8)

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=20, pady=16)

        left = ctk.CTkFrame(body, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(left, text=res["res_name"], font=FONT_SUBHEAD,
                     text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(left, text="⭐ 4.3  •  25-35 min  •  Free delivery",
                     font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w", pady=(4, 0))

        right = ctk.CTkFrame(body, fg_color="transparent")
        right.pack(side="right")

        # Remove from favourites
        ctk.CTkButton(right, text="💔 Remove", width=110, height=36,
                      fg_color="#FFEBEE", text_color=DANGER,
                      hover_color="#FFCDD2", font=FONT_SMALL,
                      corner_radius=10,
                      command=lambda r_id=res["res_id"]: self._remove(r_id)).pack()

        if self.open_menu_callback:
            ctk.CTkButton(card, text="View Menu →", height=36,
                          fg_color=PRIMARY, hover_color=PRIMARY_DARK,
                          font=FONT_BTN, corner_radius=0,
                          command=lambda r=res: (self.destroy(),
                                                 self.open_menu_callback(r["res_id"], r["res_name"]))
                          ).pack(fill="x")

    def _remove(self, res_id):
        toggle_favourite(self.user_id, res_id)
        self._load()