import customtkinter as ctk
from tkinter import messagebox, simpledialog
from database import get_connection
import home_gui
from theme import *
from image_utils import get_food_image, load_image_async

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class FoodlyApp(ctk.CTk):
    def __init__(self, user_id, res_id, res_name="Restaurant"):
        super().__init__()
        self.user_id   = user_id
        self.res_id    = res_id
        self.res_name  = res_name
        self.cart: dict = {}
        self.user_address = self._fetch_address()

        self.title(f"Foodly — {self.res_name}")
        self.after(0, lambda: self.state("zoomed"))
        self.configure(fg_color=BG)

        self.cart_bar = ctk.CTkFrame(self, fg_color=DARK_HEADER,
                                     height=72, corner_radius=20)
        self.show_menu()

    def _fetch_address(self):
        conn = get_connection()
        addr = "CGC Jhanjeri, Mohali"
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT address FROM users WHERE user_id=%s", (self.user_id,))
                r = cur.fetchone()
                if r and r[0]:
                    addr = r[0]
            except:
                pass
            finally:
                conn.close()
        return addr

    def _clear(self):
        for w in self.winfo_children():
            if w is not self.cart_bar:
                w.destroy()

    def show_menu(self):
        self._clear()
        self.cart_bar.place_forget()

        header = ctk.CTkFrame(self, fg_color=CARD, corner_radius=0, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="x", padx=40, pady=20)
        ctk.CTkButton(inner, text="← Back", width=90, height=36,
                      fg_color="#F0F0F0", text_color=TEXT,
                      hover_color=BORDER, font=FONT_BTN,
                      corner_radius=10, command=self._go_back).pack(side="left")
        ctk.CTkLabel(inner, text=self.res_name, font=("Georgia", 24, "bold"),
                     text_color=TEXT).pack(side="left", padx=20)
        meta = ctk.CTkFrame(inner, fg_color="transparent")
        meta.pack(side="left")
        ctk.CTkLabel(meta, text="⭐ 4.3  •  25-35 min  •  Free delivery",
                     font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")

        scroll = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=60, pady=20)
        ctk.CTkLabel(scroll, text="Menu", font=("Georgia", 20, "bold"),
                     text_color=TEXT).pack(anchor="w", pady=(0, 12))
        self._load_menu_items(scroll)

    def _load_menu_items(self, parent):
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM menuitems WHERE res_id=%s", (self.res_id,))
            items = cur.fetchall()
        except:
            items = []
        finally:
            conn.close()
        for item in items:
            self._menu_card(parent, item)

    def _menu_card(self, parent, item):
        is_veg = True
        if "category" in item and item["category"] and "Non" in item["category"]:
            is_veg = False
        elif any(x in item["item_name"] for x in ["Chicken", "Mutton", "Egg"]):
            is_veg = False

        card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=16,
                            border_width=1, border_color=BORDER)
        card.pack(fill="x", pady=8)

        # ── Left: text info ──────────────────────────────────────────────────
        left = ctk.CTkFrame(card, fg_color="transparent")
        left.pack(side="left", padx=25, pady=20, fill="both", expand=True)

        veg_color = SUCCESS if is_veg else DANGER
        veg_text  = "🟢 Veg" if is_veg else "🔴 Non-Veg"
        ctk.CTkLabel(left, text=veg_text, font=("Helvetica", 11, "bold"),
                     text_color=veg_color).pack(anchor="w")
        ctk.CTkLabel(left, text=item["item_name"], font=("Georgia", 18, "bold"),
                     text_color=TEXT).pack(anchor="w", pady=(3, 0))
        ctk.CTkLabel(left, text=f"₹{item['price']}",
                     font=FONT_PRICE, text_color=SUCCESS).pack(anchor="w", pady=(4, 0))

        # ── Right: food image + ADD button ───────────────────────────────────
        right = ctk.CTkFrame(card, fg_color="transparent")
        right.pack(side="right", padx=20, pady=16)

        # Image container
        img_container = ctk.CTkFrame(right, fg_color="#F0F0F0", corner_radius=12,
                                     width=160, height=110)
        img_container.pack()
        img_container.pack_propagate(False)

        # Emoji placeholder
        ph = ctk.CTkLabel(img_container, text="🍽", font=("Helvetica", 30),
                          fg_color="transparent")
        ph.place(relx=0.5, rely=0.5, anchor="center")

        # Load real image in background thread (no UI freeze)
        def _on_img_ready(photo, frame=img_container, placeholder=ph):
            if photo is None:
                return  # keep emoji placeholder
            try:
                placeholder.destroy()
                lbl = ctk.CTkLabel(frame, image=photo, text="", corner_radius=12)
                lbl.image = photo
                lbl.place(relx=0.5, rely=0.5, anchor="center")
            except Exception:
                pass  # widget gone

        load_image_async(get_food_image, _on_img_ready,
                         item["item_name"], size=(160, 110),
                         widget=img_container)

        # ADD / qty controls
        i_id = item["item_id"]
        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.pack(pady=(8, 0))

        if i_id in self.cart:
            ctrl = ctk.CTkFrame(btn_frame, fg_color="#F0FAF0", corner_radius=10)
            ctrl.pack()
            ctk.CTkButton(ctrl, text="−", width=36, height=36,
                          fg_color="transparent", text_color=DANGER,
                          font=("Helvetica", 20, "bold"),
                          command=lambda i=item: self._adjust(i, -1)).pack(side="left", padx=4)
            ctk.CTkLabel(ctrl, text=str(self.cart[i_id]["qty"]),
                         font=FONT_SUBHEAD, text_color=TEXT).pack(side="left", padx=4)
            ctk.CTkButton(ctrl, text="+", width=36, height=36,
                          fg_color="transparent", text_color=SUCCESS,
                          font=("Helvetica", 20, "bold"),
                          command=lambda i=item: self._adjust(i, 1)).pack(side="left", padx=4)
        else:
            ctk.CTkButton(btn_frame, text="ADD +", width=110, height=38,
                          fg_color=CARD, text_color=PRIMARY,
                          border_width=2, border_color=PRIMARY,
                          hover_color="#FFF3E0", font=FONT_BTN,
                          corner_radius=10,
                          command=lambda i=item: self._add_item(i)).pack()

    def _add_item(self, item):
        i_id = item["item_id"]
        if i_id in self.cart:
            self.cart[i_id]["qty"] += 1
        else:
            self.cart[i_id] = {"name": item["item_name"], "qty": 1,
                               "price": float(item["price"])}
        self._refresh_menu()
        self._update_cart_bar()

    def _adjust(self, item, delta):
        i_id = item["item_id"]
        if i_id not in self.cart:
            return
        self.cart[i_id]["qty"] += delta
        if self.cart[i_id]["qty"] <= 0:
            del self.cart[i_id]
        self._refresh_menu()
        self._update_cart_bar()

    def _refresh_menu(self):
        self.show_menu()
        self._update_cart_bar()

    def _update_cart_bar(self):
        count = sum(d["qty"] for d in self.cart.values())
        total = sum(d["qty"] * d["price"] for d in self.cart.values())
        if count == 0:
            self.cart_bar.place_forget()
            return
        for w in self.cart_bar.winfo_children():
            w.destroy()
        inner = ctk.CTkFrame(self.cart_bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=40)
        ctk.CTkLabel(inner, text=f"🛒  {count} item{'s' if count > 1 else ''} in cart",
                     font=FONT_SUBHEAD, text_color="white").pack(side="left")
        ctk.CTkLabel(inner, text=f"₹{total:.0f}",
                     font=("Georgia", 17, "bold"), text_color=PRIMARY_LIGHT).pack(side="left", padx=15)
        ctk.CTkButton(inner, text="Proceed to Checkout →",
                      fg_color=PRIMARY, hover_color=PRIMARY_DARK,
                      font=FONT_BTN, height=42, corner_radius=10,
                      width=200, command=self.show_checkout).pack(side="right")
        self.cart_bar.place(relx=0.5, rely=0.94, anchor="center", relwidth=0.75)
        self.cart_bar.lift()

    def _go_back(self):
        self.destroy()
        home_gui.HomePage(self.user_id).mainloop()

    def show_checkout(self):
        self._clear()
        self.cart_bar.place_forget()

        header = ctk.CTkFrame(self, fg_color=CARD, corner_radius=0, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        inner_h = ctk.CTkFrame(header, fg_color="transparent")
        inner_h.pack(fill="x", padx=40, pady=17)
        ctk.CTkButton(inner_h, text="← Back to Menu", width=130, height=36,
                      fg_color="#F0F0F0", text_color=TEXT,
                      hover_color=BORDER, font=FONT_BTN, corner_radius=10,
                      command=self.show_menu).pack(side="left")
        ctk.CTkLabel(inner_h, text="Checkout", font=("Georgia", 20, "bold"),
                     text_color=TEXT).pack(side="left", padx=20)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=40, pady=20)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        self._build_checkout_left(body)
        self._build_checkout_right(body)

    def _build_checkout_left(self, parent):
        left = ctk.CTkScrollableFrame(parent, fg_color="transparent", corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        addr_card = ctk.CTkFrame(left, fg_color=CARD, corner_radius=16,
                                 border_width=1, border_color=BORDER)
        addr_card.pack(fill="x", pady=(0, 15))
        row1 = ctk.CTkFrame(addr_card, fg_color="transparent")
        row1.pack(fill="x", padx=25, pady=(20, 5))
        ctk.CTkLabel(row1, text="📍  Delivery Address",
                     font=FONT_SUBHEAD, text_color=TEXT).pack(side="left")
        ctk.CTkButton(row1, text="Change", width=70, height=28,
                      fg_color="#FFF3E0", text_color=WARN,
                      hover_color="#FFE0B2", font=FONT_SMALL,
                      corner_radius=8, command=self._change_address).pack(side="right")
        self.addr_label = ctk.CTkLabel(addr_card, text=self.user_address,
                                       font=FONT_BODY, text_color=TEXT_MUTED,
                                       wraplength=400, justify="left")
        self.addr_label.pack(anchor="w", padx=25, pady=(0, 20))

        pay_card = ctk.CTkFrame(left, fg_color=CARD, corner_radius=16,
                                border_width=1, border_color=BORDER)
        pay_card.pack(fill="x")
        ctk.CTkLabel(pay_card, text="💳  Payment Method",
                     font=FONT_SUBHEAD, text_color=TEXT).pack(anchor="w", padx=25, pady=(20, 12))
        self.pay_method = ctk.StringVar(value="COD")
        for val, txt in [("COD", "Cash on Delivery"), ("Online", "Online Payment (UPI / Card)")]:
            ctk.CTkRadioButton(pay_card, text=txt, variable=self.pay_method,
                               value=val, fg_color=PRIMARY, font=FONT_BODY,
                               text_color=TEXT).pack(anchor="w", padx=35, pady=8)
        ctk.CTkFrame(pay_card, height=1).pack(pady=12)

    def _build_checkout_right(self, parent):
        right = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=16,
                             border_width=1, border_color=BORDER)
        right.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(right, text="Order Summary",
                     font=("Georgia", 20, "bold"), text_color=TEXT).pack(padx=25, pady=(25, 12), anchor="w")

        items_frame = ctk.CTkScrollableFrame(right, fg_color="transparent", height=260)
        items_frame.pack(fill="x", padx=20)

        subtotal = 0.0
        for i_id, data in self.cart.items():
            row = ctk.CTkFrame(items_frame, fg_color="transparent")
            row.pack(fill="x", pady=8)
            left_col = ctk.CTkFrame(row, fg_color="transparent")
            left_col.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(left_col, text=data["name"], font=FONT_BODY,
                         text_color=TEXT, wraplength=150, justify="left").pack(anchor="w")
            ctk.CTkLabel(left_col, text=f"x{data['qty']}",
                         font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")
            line_total = data["qty"] * data["price"]
            subtotal  += line_total
            ctk.CTkLabel(row, text=f"₹{line_total:.0f}",
                         font=FONT_SUBHEAD, text_color=TEXT).pack(side="right")

        ctk.CTkFrame(right, height=1, fg_color=BORDER).pack(fill="x", padx=20, pady=12)
        bill = ctk.CTkFrame(right, fg_color="transparent")
        bill.pack(fill="x", padx=25, pady=(0, 10))

        delivery = 45 if subtotal > 0 else 0
        gst      = round(subtotal * 0.05, 2)
        total    = subtotal + delivery + gst + 5
        self.final_total = total

        for lbl, val, bold, col in [
            ("Item Total",   f"₹{subtotal:.0f}",  False, TEXT),
            ("Delivery Fee", f"₹{delivery}",       False, WARN),
            ("GST (5%)",     f"₹{gst:.2f}",        False, TEXT_MUTED),
            ("Platform Fee", "₹5",                 False, TEXT_MUTED),
            ("Total",        f"₹{total:.0f}",       True,  SUCCESS),
        ]:
            r = ctk.CTkFrame(bill, fg_color="transparent")
            r.pack(fill="x", pady=4)
            f = FONT_SUBHEAD if bold else FONT_BODY
            ctk.CTkLabel(r, text=lbl, font=f, text_color=col).pack(side="left")
            ctk.CTkLabel(r, text=val, font=f, text_color=col).pack(side="right")

        ctk.CTkButton(right, text=f"Place Order  ₹{total:.0f}",
                      fg_color=SUCCESS, hover_color=SUCCESS_DARK,
                      font=("Helvetica", 17, "bold"), height=56,
                      corner_radius=14, command=self._place_order).pack(
                      fill="x", padx=20, pady=20)

    def _change_address(self):
        new = simpledialog.askstring("Delivery Address", "Enter new address:",
                                     initialvalue=self.user_address)
        if new:
            self.user_address = new
            self.addr_label.configure(text=new)
            conn = get_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("UPDATE users SET address=%s WHERE user_id=%s",
                                (new, self.user_id))
                    conn.commit()
                except:
                    pass
                finally:
                    conn.close()

    def _place_order(self):
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT full_name, phone FROM users WHERE user_id=%s", (self.user_id,))
            user = cur.fetchone()
            if user:
                cur.execute(
                    "INSERT INTO orders (user_id,customer_name,phone_number,res_id,"
                    "total_amount,delivery_address,order_status) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (self.user_id, user["full_name"], user["phone"], self.res_id,
                     self.final_total, self.user_address, "Pending")
                )
                conn.commit()
                messagebox.showinfo("Order Placed! 🎉",
                                    "Your order has been placed successfully!\n"
                                    "Estimated delivery: 30-40 minutes.")
                self.destroy()
                home_gui.HomePage(self.user_id).mainloop()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()


if __name__ == "__main__":
    FoodlyApp(user_id=1, res_id=1, res_name="Domino's Pizza").mainloop()