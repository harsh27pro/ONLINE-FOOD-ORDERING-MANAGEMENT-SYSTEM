-- 1. refresh data base 
DROP DATABASE IF EXISTS foodorderdb;
CREATE DATABASE foodorderdb;
USE foodorderdb;

-- 2. USERS TABLE (For Login & Profile)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15),
    address TEXT
);

-- 3. RESTAURANTS TABLE (For Dashboard)
CREATE TABLE restaurants (
    res_id INT AUTO_INCREMENT PRIMARY KEY,
    res_name VARCHAR(100) NOT NULL,
    cuisine_type VARCHAR(50),
    rating DECIMAL(2,1)
);

-- 4. MENUITEMS TABLE (Linked to Restaurants)
CREATE TABLE menuitems (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    res_id INT,
    item_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(50),
    FOREIGN KEY (res_id) REFERENCES restaurants(res_id) ON DELETE CASCADE
);

-- 5. ORDERS TABLE (Linked to Users & Restaurants)
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    res_id INT,
    total_amount DECIMAL(10,2) NOT NULL,
    order_status VARCHAR(50) DEFAULT 'Pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (res_id) REFERENCES restaurants(res_id) ON DELETE CASCADE
);

-- INSERTING FRESH DATA (Testing)

-- Add Harsh Kumar (Login: harsh@gmail.com | Pass: 1234)
INSERT INTO users (full_name, email, password, phone, address) 
VALUES ('Harsh Kumar', 'harsh@gmail.com', '1234', '9876543210', 'CGC Jhanjeri, Mohali');

INSERT INTO users (full_name, email, password, phone, address) 
VALUES ('anish', 'anish@gmail.com', '9876', '7973583884', 'Mullana,Ambala');

TRUNCATE TABLE restaurants;

-- Insert restaurent one by one 
INSERT INTO restaurants (res_name, cuisine_type, rating) VALUES 
('Dominos', 'Pizza', 4.5),
('Burger King', 'Burgers', 4.2),
('The Punjabi Tadka', 'North Indian', 4.5), 
('China Town', 'Chinese', 4.1),
('South Feast', 'South Indian', 4.3), 
('Italiano Pizza', 'Italian', 4.6),
('Burger Singh', 'Fast Food', 4.2), 
('Rolls Mania', 'Street Food', 4.0),
('Momos Hub', 'Chinese', 4.4), 
('Amritsari Kulcha', 'North Indian', 4.7),
('Hyderabadi Dum', 'Mughlai', 4.8), 
('The Salad Bar', 'Healthy', 4.5),
('Waffle Wallah', 'Desserts', 4.3), 
('Coffee House', 'Beverages', 4.1),
('Shakes Island', 'Desserts', 4.2), 
('Kathi Junction', 'Fast Food', 4.4),
('Dosa Plaza', 'South Indian', 4.5), 
('Tandoori Nights', 'North Indian', 4.6),
('Beijing Bites', 'Chinese', 4.0), 
('The Pasta Company', 'Italian', 4.3),
('Lassi Shop', 'Beverages', 4.8), 
('Sweet Bengal', 'Sweets', 4.7),
('Sardarji Baksh', 'Coffee', 4.5), 
('Bistro 57', 'Fast Food', 4.1),
('La Pinoz', 'Pizza', 4.4), 
('Wat-a-Burger', 'Burgers', 4.2),
('Chai Sutta Bar', 'Tea/Snacks', 3.9);

-- Make Changes Permanent
COMMIT;

-- Add Sample Order for History
INSERT INTO orders (user_id, res_id, total_amount, order_status) 
VALUES (1, 1, 549.00, 'Delivered');

USE foodorderdb;
SELECT * FROM menuitems;

SELECT res_id, res_name 
FROM restaurants;

USE foodorderdb;

ALTER TABLE users 
ADD COLUMN role VARCHAR(20) DEFAULT 'customer';


TRUNCATE TABLE menuitems;

INSERT INTO menuitems (res_id, item_name, price) VALUES
(1, 'Margherita Pizza', 199), (1, 'Peppy Paneer', 350), (1, 'Garlic Bread', 99),
(2, 'Whopper Burger', 149), (2, 'Crispy Veg Burger', 70), (2, 'Fries (L)', 95),
(3, 'Dal Makhani', 220), (3, 'Paneer Butter Masala', 250), (3, 'Butter Naan', 45),
(4, 'Veg Manchurian', 150), (4, 'Hakka Noodles', 140), (4, 'Spring Rolls', 110),
(5, 'Masala Dosa', 120), (5, 'Idli Sambar', 80), (5, 'Upma', 70),
(6, 'Farmhouse Pizza', 399), (6, 'Pasta Alfredo', 220), (6, 'Coke', 50),
(7, 'Jatt Putt Burger', 130), (7, 'Dilli-6 Fries', 80), (7, 'Cold Coffee', 90),
(8, 'Paneer Mayonnaise Roll', 120), (8, 'Double Egg Roll', 100), (8, 'Aloo Roll', 70),
(9, 'Veg Steamed Momos', 80), (9, 'Fried Momos', 100), (9, 'Kurkure Momos', 140),
(10, 'Paneer Kulcha with Chole', 140), (10, 'Mix Kulcha', 120), (10, 'Special Lassi', 60),
(11, 'Veg Biryani', 210), (11, 'Paneer 65', 180), (11, 'Mirchi Ka Salan', 40),
(12, 'Greek Salad', 160), (12, 'Fruit Bowl', 120), (12, 'Sprouts Mix', 90),
(13, 'Nutella Waffle', 150), (13, 'Belgian Chocolate', 140), (13, 'Honey Waffle', 110),
(14, 'Cappuccino', 120), (14, 'Hot Chocolate', 140), (14, 'Cookies', 40),
(15, 'KitKat Shake', 130), (15, 'Oreo Shake', 130), (15, 'Mango Shake', 110),
(16, 'Paneer Tikka Roll', 140), (16, 'Veg Seekh Kabab', 160), (16, 'Rumali Roti', 20),
(17, 'Mysore Masala Dosa', 150), (17, 'Onion Rava Dosa', 140), (17, 'Filter Coffee', 40),
(18, 'Soya Chaap', 180), (18, 'Malai Paneer Tikka', 240), (18, 'Tandoori Roti', 15),
(19, 'Chilli Paneer', 190), (19, 'Veg Fried Rice', 150), (19, 'Kimchi Salad', 60),
(20, 'Red Sauce Pasta', 180), (20, 'White Sauce Pasta', 200), (20, 'Pink Sauce Pasta', 220),
(21, 'Sweet Lassi', 50), (21, 'Mango Lassi', 70), (21, 'Strawberry Lassi', 70),
(22, 'Rasgulla (2pc)', 40), (22, 'Sandesh', 50), (22, 'Mishti Doi', 60),
(23, 'Irish Coffee', 180), (23, 'Hazelnut Frappe', 210), (23, 'Paneer Sandwich', 120),
(24, 'Nachos', 90), (24, 'Garlic Toast', 80), (24, 'Hot Coffee', 60),
(25, '7 Cheese Pizza', 450), (25, 'Giant Slice', 250), (25, 'Stuffed Garlic Bread', 140),
(26, 'Veggie Surprise', 90), (26, 'Mutton Like Veg Burger', 110), (26, 'Iced Tea', 70),
(27, 'Adrak Chai', 20), (27, 'Rose Chai', 25), (27, 'Bun Maska', 40);

COMMIT;

-- To add column into any table -- 
ALTER TABLE orders 
ADD COLUMN delivery_address TEXT NOT NULL AFTER total_amount;

ALTER TABLE orders 
ADD COLUMN customer_name VARCHAR(100),
ADD COLUMN customer_mobile VARCHAR(15);

-- To delete the data from any database --  
truncate table orders;
delete from orders where user_id = 1;
delete from orders where user_id = 2;
delete from orders where user_id = 4;

UPDATE Users SET address = '' WHERE address = 'CGC Jhanjeri';

INSERT INTO restaurants (res_name, cuisine_type, rating) VALUES
('Thick & Letto', 'Shakes', 9.8 );

INSERT INTO menuitems (res_id, item_name, price) VALUES
(28, 'Butter Nut', 70), (28, 'Strawberry', 90), (28, 'Pista', 99),(28, 'Chocolate', 50);

-- Foodly Advanced Features — Database Migration
-- Run this SQL in your MySQL Workbench / phpMyAdmin / CLI
-- Database: foodorderdb

USE foodorderdb;

-- ── 1. Reviews table ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reviews (
    review_id    INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT          NOT NULL,
    res_id       INT          NOT NULL,
    order_id     INT          DEFAULT NULL,
    rating       TINYINT      NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_text  TEXT         DEFAULT NULL,
    created_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_user_res_order (user_id, res_id, order_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)   ON DELETE CASCADE,
    FOREIGN KEY (res_id)  REFERENCES restaurants(res_id) ON DELETE CASCADE
);

-- ── 2. Wishlist / Favourites table ───────────────────────────
CREATE TABLE IF NOT EXISTS wishlist (
    wishlist_id  INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT NOT NULL,
    res_id       INT NOT NULL,
    added_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_user_res (user_id, res_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)      ON DELETE CASCADE,
    FOREIGN KEY (res_id)  REFERENCES restaurants(res_id) ON DELETE CASCADE
);

ALTER TABLE restaurants ADD COLUMN avg_rating DECIMAL(3,1) DEFAULT 4.0;
