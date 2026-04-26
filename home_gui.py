import customtkinter as ctk
from tkinter import messagebox
from database import get_connection
import main
import profile_gui
import orders_gui
from theme import *
from image_utils import get_restaurant_image, load_image_async

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class HomePage(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.title("Foodly — Home")
        self.after(0, lambda: self.state("zoomed"))
        self.configure(fg_color=BG)
        self._build_ui()

    def _build_ui(self):
        self._build_sidebar()
        self._build_main()

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, fg_color=DARK_HEADER, corner_radius=0, width=220)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        ctk.CTkLabel(sb, text="Foodly", font=("Georgia", 22, "bold"),
                     text_color=PRIMARY).pack(pady=(35, 40), padx=25, anchor="w")
        for icon, label, cmd in [
            ("🏠", "Home",       self._refresh_restaurants),
            ("📜", "My Orders",  self.open_history),
            ("❤", "Favourites", self.open_favourites),
            ("👤", "Profile",    self.open_profile),
        ]:
            ctk.CTkButton(sb, text=f"  {icon} {label}", anchor="w",
                          fg_color="transparent", hover_color="#263238",
                          font=FONT_SUBHEAD, text_color="#CFD8DC",
                          height=46, corner_radius=10, command=cmd).pack(fill="x", padx=15, pady=3)

        ctk.CTkButton(sb, text="  Logout", anchor="w",
                      fg_color="transparent", hover_color="#B71C1C",
                      font=FONT_SUBHEAD, text_color="#EF9A9A",
                      height=46, corner_radius=10,
                      command=self._logout).pack(fill="x", padx=15, pady=3, side="bottom")

    def _logout(self):
        self.destroy()
        import front_page
        front_page.FrontPage().mainloop()

    def _build_main(self):
        self.main_area = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        self.main_area.pack(side="left", fill="both", expand=True)
        self._build_topbar()
        self._build_banner()
        self._build_restaurant_section()

    def _build_topbar(self):
        bar = ctk.CTkFrame(self.main_area, fg_color=CARD, corner_radius=0, height=70)
        bar.pack(fill="x")
        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="x", padx=35, pady=15)
        ctk.CTkLabel(inner, text="CGC Jhanjeri, Mohali",
                     font=FONT_SUBHEAD, text_color=TEXT).pack(side="left")
        self.search_entry = ctk.CTkEntry(inner,
            placeholder_text="Search restaurants or dishes...",
            width=380, height=40, corner_radius=20,
            fg_color="#F8F9FA", border_color=BORDER, font=FONT_BODY)
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", self._on_search)

    def _build_banner(self):
        banner = ctk.CTkFrame(self.main_area, fg_color=PRIMARY, corner_radius=20, height=100)
        banner.pack(fill="x", padx=30, pady=(15, 0))
        banner.pack_propagate(False)
        left = ctk.CTkFrame(banner, fg_color="transparent")
        left.pack(side="left", padx=35, pady=15)
        ctk.CTkLabel(left, text="Up to 60% off on your first order!",
                     font=("Georgia", 20, "bold"), text_color="white").pack(anchor="w")
        ctk.CTkLabel(left, text="Use code  FOODLY60  at checkout",
                     font=("Helvetica", 13), text_color="#FFCCBC").pack(anchor="w", pady=(4, 0))
        right = ctk.CTkFrame(banner, fg_color="transparent")
        right.pack(side="right", padx=35)
        for badge in ["Free Delivery", "30 min", "Top Rated"]:
            b = ctk.CTkFrame(right, fg_color="#E64A19", corner_radius=20)
            b.pack(side="left", padx=5)
            ctk.CTkLabel(b, text=badge, font=("Helvetica", 12, "bold"),
                         text_color="white").pack(padx=12, pady=6)

    def _build_restaurant_section(self):
        ctk.CTkLabel(self.main_area, text="Restaurants Near You",
                     font=FONT_HEADING, text_color=TEXT).pack(anchor="w", padx=35, pady=(20, 12))
        self.res_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.res_frame.pack(fill="both", expand=True, padx=25, pady=(0, 30))
        self._load_restaurants()

    def _refresh_restaurants(self):
        self._load_restaurants()

    def _load_restaurants(self, query=""):
        for w in self.res_frame.winfo_children():
            w.destroy()
        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor(dictionary=True)
            if query:
                cursor.execute("SELECT * FROM restaurants WHERE res_name LIKE %s", (f"%{query}%",))
            else:
                cursor.execute("SELECT * FROM restaurants")
            rows = cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            rows = []
        finally:
            conn.close()

        if not rows:
            ctk.CTkLabel(self.res_frame, text="No restaurants found",
                         font=FONT_HEADING, text_color=TEXT_MUTED).pack(pady=60)
            return

        col_count = 3
        current_row = None
        for idx, res in enumerate(rows):
            if idx % col_count == 0:
                current_row = ctk.CTkFrame(self.res_frame, fg_color="transparent")
                current_row.pack(fill="x", pady=8)
            self._restaurant_card(current_row, res)

    def _restaurant_card(self, parent, res):
        from wishlist import is_favourite, toggle_favourite

        card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=18,
                            border_width=1, border_color=BORDER)
        card.pack(side="left", padx=8, expand=True, fill="x")

        # Banner image area
        img_frame = ctk.CTkFrame(card, fg_color=DARK_HEADER, corner_radius=12, height=130)
        img_frame.pack(fill="x")
        img_frame.pack_propagate(False)

        placeholder_lbl = ctk.CTkLabel(img_frame, text="", font=("Helvetica", 40),
                                       fg_color="transparent")
        placeholder_lbl.pack(pady=28)

        def _on_img_ready(photo, frame=img_frame, plbl=placeholder_lbl):
            if photo is None:
                return
            try:
                plbl.destroy()
                lbl = ctk.CTkLabel(frame, image=photo, text="")
                lbl.image = photo
                lbl.pack(fill="both", expand=True)
            except Exception:
                pass

        load_image_async(get_restaurant_image, _on_img_ready,
                         res["res_name"], size=(340, 130),
                         widget=img_frame)

        # Discount badge
        badge = ctk.CTkFrame(img_frame, fg_color=SUCCESS, corner_radius=8)
        badge.place(x=10, y=100)
        ctk.CTkLabel(badge, text="60% OFF", font=("Helvetica", 10, "bold"),
                     text_color="white").pack(padx=8, pady=3)

        # Heart button — top right of image
        r_id = res["res_id"]
        fav  = is_favourite(self.user_id, r_id)

        heart_btn = ctk.CTkButton(img_frame,
                                   text="♥" if fav else "♡",
                                   width=36, height=36,
                                   fg_color="white",
                                   hover_color="#FFEBEE",
                                   font=("Helvetica", 18, "bold"),
                                   corner_radius=18,
                                   text_color=DANGER if fav else "#AAAAAA")
        heart_btn.place(relx=1.0, rely=0.0, x=-8, y=8, anchor="ne")

        def _toggle(btn=heart_btn, res_id=r_id):
            now_fav = toggle_favourite(self.user_id, res_id)
            btn.configure(
                text="♥" if now_fav else "♡",
                text_color=DANGER if now_fav else "#AAAAAA"
            )
        heart_btn.configure(command=_toggle)

        # Info section
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(body, text=res["res_name"], font=FONT_SUBHEAD,
                     text_color=TEXT).pack(anchor="w")
        meta = ctk.CTkFrame(body, fg_color="transparent")
        meta.pack(fill="x", pady=(4, 0))

        rating_val = "4.0"
        if "avg_rating" in res and res["avg_rating"]:
            rating_val = str(res["avg_rating"])

        ctk.CTkLabel(meta, text=f"* {rating_val}", font=FONT_SMALL,
                     text_color=WARN).pack(side="left")
        ctk.CTkLabel(meta, text=" • 25-35 min", font=FONT_SMALL,
                     text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkLabel(meta, text="Free delivery", font=FONT_SMALL,
                     text_color=SUCCESS).pack(side="right")

        ctk.CTkButton(card, text="View Menu", height=38, corner_radius=10,
                      fg_color=PRIMARY, hover_color=PRIMARY_DARK, font=FONT_BTN,
                      command=lambda r_id=res["res_id"], r_name=res["res_name"]:
                              self._open_menu(r_id, r_name)).pack(fill="x", padx=16, pady=(6, 16))

    def _on_search(self, event):
        self._load_restaurants(self.search_entry.get())

    def _open_menu(self, r_id, r_name):
        self.destroy()
        main.FoodlyApp(self.user_id, r_id, r_name).mainloop()

    def open_history(self):
        orders_gui.OrdersPage(self.user_id,
                              open_menu_callback=self._open_menu)

    def open_favourites(self):
        from wishlist import FavouritesPage
        FavouritesPage(self, self.user_id, open_menu_callback=self._open_menu)

    def open_profile(self):
        profile_gui.ProfilePage(self.user_id)


if __name__ == "__main__":
    HomePage(user_id=1).mainloop()