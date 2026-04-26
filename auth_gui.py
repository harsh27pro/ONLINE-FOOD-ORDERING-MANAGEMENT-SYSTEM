import customtkinter as ctk
from tkinter import messagebox
from database import get_connection
import home_gui
from theme import *

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class AuthPage(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Foodly — Sign In")
        self.geometry("900x620")
        self.resizable(False, False)
        self.configure(fg_color=CARD)
        self._build_shell()
        self.show_login()

    # ── Two-column shell ──────────────────────────────────────────────────────
    def _build_shell(self):
        # Left branding panel
        self.brand = ctk.CTkFrame(self, fg_color=DARK_HEADER, corner_radius=0, width=360)
        self.brand.pack(side="left", fill="y")
        self.brand.pack_propagate(False)
        self._build_brand_panel()

        # Right form panel
        self.form_panel = ctk.CTkFrame(self, fg_color=CARD, corner_radius=0)
        self.form_panel.pack(side="left", fill="both", expand=True)

    def _build_brand_panel(self):
        ctk.CTkLabel(self.brand, text="🍽", font=("Helvetica", 60)).pack(pady=(80, 10))
        ctk.CTkLabel(self.brand, text="Foodly", font=("Georgia", 42, "bold"),
                     text_color=PRIMARY).pack()
        ctk.CTkLabel(self.brand, text="Your favourite food,\ndelivered to your door.",
                     font=("Helvetica", 14), text_color="#90A4AE",
                     justify="center").pack(pady=(15, 60))

        for icon, txt in [("🚀", "Fast Delivery"), ("⭐", "Top Rated"), ("🔒", "Secure Checkout")]:
            row = ctk.CTkFrame(self.brand, fg_color="#263238", corner_radius=12)
            row.pack(fill="x", padx=30, pady=6)
            ctk.CTkLabel(row, text=icon, font=("Helvetica", 18)).pack(side="left", padx=15, pady=12)
            ctk.CTkLabel(row, text=txt, font=FONT_BODY, text_color="#CFD8DC").pack(side="left")

    def _clear_form(self):
        for w in self.form_panel.winfo_children():
            w.destroy()

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _label(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Helvetica", 12, "bold"),
                     text_color=TEXT_MUTED, anchor="w").pack(fill="x", pady=(10, 2))

    def _entry(self, parent, placeholder, show=""):
        e = ctk.CTkEntry(parent, placeholder_text=placeholder, height=46,
                         corner_radius=10, font=FONT_BODY,
                         fg_color="#F8F9FA", border_color=BORDER,
                         show=show)
        e.pack(fill="x")
        return e

    def _divider(self, parent):
        ctk.CTkFrame(parent, height=1, fg_color=BORDER).pack(fill="x", pady=15)

    # ── Login View ────────────────────────────────────────────────────────────
    def show_login(self):
        self._clear_form()
        f = self.form_panel

        ctk.CTkLabel(f, text="Welcome back 👋", font=("Georgia", 28, "bold"),
                     text_color=TEXT).pack(anchor="w", padx=50, pady=(55, 2))
        ctk.CTkLabel(f, text="Sign in to continue your foodie journey",
                     font=FONT_BODY, text_color=TEXT_MUTED).pack(anchor="w", padx=50)

        form = ctk.CTkFrame(f, fg_color="transparent")
        form.pack(fill="x", padx=50, pady=20)

        self._label(form, "Email Address")
        self.email_entry = self._entry(form, "you@example.com")

        self._label(form, "Password")
        self.pass_entry = self._entry(form, "••••••••", show="*")

        ctk.CTkButton(form, text="Sign In", height=50, corner_radius=12,
                      fg_color=PRIMARY, hover_color=PRIMARY_DARK,
                      font=("Helvetica", 16, "bold"),
                      command=self.login_logic).pack(fill="x", pady=(25, 0))

        self._divider(form)

        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack()
        ctk.CTkLabel(row, text="New to Foodly?", font=FONT_BODY,
                     text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkButton(row, text=" Create Account", font=("Helvetica", 13, "bold"),
                      fg_color="transparent", text_color=PRIMARY,
                      hover_color="#FFF3E0", width=130,
                      command=self.show_signup).pack(side="left")

    # ── Signup View ───────────────────────────────────────────────────────────
    def show_signup(self):
        self._clear_form()
        f = self.form_panel

        ctk.CTkLabel(f, text="Create Account 🎉", font=("Georgia", 28, "bold"),
                     text_color=TEXT).pack(anchor="w", padx=50, pady=(40, 2))
        ctk.CTkLabel(f, text="Join thousands of happy foodies",
                     font=FONT_BODY, text_color=TEXT_MUTED).pack(anchor="w", padx=50)

        form = ctk.CTkFrame(f, fg_color="transparent")
        form.pack(fill="x", padx=50, pady=15)

        self._label(form, "Full Name")
        self.name_reg = self._entry(form, "John Doe")

        self._label(form, "Email Address")
        self.email_reg = self._entry(form, "you@example.com")

        self._label(form, "Password")
        self.pass_reg = self._entry(form, "Min. 6 characters", show="*")

        self._label(form, "Phone Number")
        self.phone_reg = self._entry(form, "+91 98765 43210")

        ctk.CTkButton(form, text="Create My Account", height=50, corner_radius=12,
                      fg_color=SUCCESS, hover_color=SUCCESS_DARK,
                      font=("Helvetica", 16, "bold"),
                      command=self.signup_logic).pack(fill="x", pady=(22, 0))

        self._divider(form)
        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack()
        ctk.CTkLabel(row, text="Already have an account?", font=FONT_BODY,
                     text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkButton(row, text=" Sign In", font=("Helvetica", 13, "bold"),
                      fg_color="transparent", text_color=PRIMARY,
                      hover_color="#FFF3E0", width=80,
                      command=self.show_login).pack(side="left")

    # ── Logic ─────────────────────────────────────────────────────────────────
    def login_logic(self):
        e, p = self.email_entry.get().strip(), self.pass_entry.get()
        if not e or not p:
            messagebox.showwarning("Missing Fields", "Please enter your email and password.")
            return
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT user_id FROM users WHERE email=%s AND password=%s", (e, p))
                user = cursor.fetchone()
                if user:
                    self.destroy()
                    home_gui.HomePage(user["user_id"]).mainloop()
                else:
                    messagebox.showerror("Login Failed", "Incorrect email or password.")
            except Exception as err:
                print(f"Login error: {err}")
            finally:
                conn.close()

    def signup_logic(self):
        name  = self.name_reg.get().strip()
        email = self.email_reg.get().strip()
        pwd   = self.pass_reg.get()
        phone = self.phone_reg.get().strip()

        if not all([name, email, pwd]):
            messagebox.showwarning("Missing Fields", "Name, email, and password are required.")
            return
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Users (full_name,email,password,phone,address,role) VALUES (%s,%s,%s,%s,%s,%s)",
                    (name, email, pwd, phone, "CGC Jhanjeri", "customer")
                )
                conn.commit()
                messagebox.showinfo("Account Created! 🎉", "Welcome to Foodly! Please sign in.")
                self.show_login()
            except Exception as err:
                messagebox.showerror("Registration Failed", str(err))
            finally:
                conn.close()


if __name__ == "__main__":
    AuthPage().mainloop()
