# 🍽 Foodly – Food Delivery Desktop Application

Foodly is a modern desktop-based food delivery application built using **Python, CustomTkinter, and MySQL**.
It provides a smooth and interactive user experience for browsing restaurants, ordering food, and tracking deliveries in real time.

---

## 🚀 Features

* 🔐 User Authentication (Login & Signup)
* 🏠 Interactive Home Page with Restaurant Listings
* 🔍 Search Restaurants & Dishes
* 🛒 Add to Cart & Checkout System
* 📦 Real-time Order Tracking
* ❤️ Wishlist / Favourites System
* ⭐ Ratings & Reviews
* 👤 User Profile Management
* 🎨 Modern UI using CustomTkinter

---

## 🛠 Tech Stack

* **Frontend:** Python (CustomTkinter)
* **Backend:** Python
* **Database:** MySQL
* **Libraries:** PIL, threading, mysql-connector

---

## 📂 Project Structure

```bash
foodly-app/
│
├── auth_gui.py
├── home_gui.py
├── orders_gui.py
├── order_tracker.py
├── profile_gui.py
├── review_gui.py
├── database.py
├── image_utils.py
├── theme.py
├── toast.py
├── main.py
├── run.py
└── foodorderdb_database.sql
```

---

## ⚙️ Setup Instructions

1. Clone the repository:

```bash
git clone https://github.com/your-username/foodly-app.git
```

2. Install dependencies:

```bash
pip install customtkinter pillow mysql-connector-python
```

3. Setup MySQL Database:

* Create a database named `foodorderdb`
* Import the SQL file:

```bash
foodorderdb_database.sql
```

4. Update database credentials in `database.py`

5. Run the application:

```bash
python main.py
```

---

## 🔒 Security Note

Database credentials are stored locally.
It is recommended to use environment variables (`.env`) for production use.

---

## 🤝 Contribution

Contributions are welcome! Feel free to fork this repository and submit a pull request.

---

## 📄 License

This project is open-source and available under the MIT License.

---

## 💡 Author

Developed by **Harsh** 🚀
