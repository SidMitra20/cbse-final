DROP DATABASE IF EXISTS airbnb_db;
CREATE DATABASE airbnb_db;
USE airbnb_db;

-- 1. Users Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL,
    full_name VARCHAR(100) NOT NULL
);

-- 2. Destination Table
CREATE TABLE destination (
    dest_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL
);

-- 3. Houses Table
CREATE TABLE houses (
    house_id INT AUTO_INCREMENT PRIMARY KEY,
    dest_id INT,
    title VARCHAR(100) NOT NULL,
    size VARCHAR(20) NOT NULL,
    price_per_night DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (dest_id) REFERENCES destination(dest_id) ON DELETE CASCADE
);

-- 4. Bookings Table
CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    house_id INT,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (house_id) REFERENCES houses(house_id) ON DELETE CASCADE
);

-- --- 10 DESTINATIONS (Ordered so Goa=1, NYC=2, Bali=3, Paris=4) ---
INSERT INTO destination (name, category) VALUES
('Goa', 'Beach'),          -- dest_id = 1
('New York', 'City'),     -- dest_id = 2
('Bali', 'Beach'),         -- dest_id = 3
('Paris', 'City'),         -- dest_id = 4
('Swiss Alps', 'Mountain'),-- dest_id = 5
('Santorini', 'Island'),   -- dest_id = 6
('Tokyo', 'City'),         -- dest_id = 7
('Kyoto', 'Mountain'),     -- dest_id = 8
('Maldives', 'Island'),    -- dest_id = 9
('Maui', 'Island');        -- dest_id = 10

-- --- 3 HOUSES PER DESTINATION ---

-- 1. Goa (dest_id = 1) -> House IDs 1, 2, 3 (Matches 1.png, 2.png, 3.png)
INSERT INTO houses (dest_id, title, size, price_per_night) VALUES
(1, 'Sunny Anjuna Beach Villa', 'Villa', 8000.00),
(1, 'Calangute Studio Flat', '1 BHK', 2200.00),
(1, 'Portuguese Heritage Home', '2 BHK', 4500.00);

-- 2. New York (dest_id = 2) -> House IDs 4, 5, 6 (Matches 4.png, 5.png, 6.png)
INSERT INTO houses (dest_id, title, size, price_per_night) VALUES
(2, 'Manhattan Skyline Penthouse', 'Villa', 22000.00),
(2, 'Brooklyn Cozy Studio', '1 BHK', 7500.00),
(2, 'SoHo Modern Apartment', '2 BHK', 14000.00);

-- 3. Bali (dest_id = 3) -> House IDs 7, 8, 9 (Matches 7.png, 8.png, 9.png)
INSERT INTO houses (dest_id, title, size, price_per_night) VALUES
(3, 'Ubud Jungle Villa with Pool', 'Villa', 12000.00),
(3, 'Seminyak Beachfront Bamboo Cottage', '1 BHK', 4500.00),
(3, 'Canggu Surfer Loft', '2 BHK', 7000.00);

-- 4. Paris (dest_id = 4) -> House IDs 10, 11, 12 (Matches 10.png, 11.png, 12.png)
INSERT INTO houses (dest_id, title, size, price_per_night) VALUES
(4, 'Eiffel Tower View Apartment', '2 BHK', 18000.00),
(4, 'Le Marais Historic Studio', '1 BHK', 8500.00),
(4, 'Montmartre Luxury Loft', 'Villa', 25000.00);

-- 5. Swiss Alps (dest_id = 5) -> House IDs 13, 14, 15
INSERT INTO houses (dest_id, title, size, price_per_night) VALUES
(5, 'Zermatt Wooden Chalet', 'Villa', 30000.00),
(5, 'Alpine Ski Studio', '1 BHK', 11000.00),
(5, 'Matterhorn View Lodge', '2 BHK', 19000.00);

-- 6. Santorini (dest_id = 6) -> House IDs 16, 17, 18
INSERT INTO houses (dest_id, title, size, price_per_night) VALUES
(6, 'Oia Cave House with Caldera View', '2 BHK', 21000.00),
(6, 'White Dome Cliffside Villa', 'Villa', 32000.00),
(6, 'Fira Town Studio', '1 BHK', 9000.00);

-- 7. Tokyo (dest_id = 7) -> House IDs 19, 20, 21
INSERT INTO houses (dest_id, title, size, price_per_night) VALUES
(7, 'Shinjuku High-Rise Flat', '2 BHK', 13000.00),
(7, 'Shibuya Compact Apartment', '1 BHK', 6500.00),
(7, 'Minato Luxury Penthouse', 'Villa', 28000.00);

-- 8. Kyoto (dest_id = 8) -> House IDs 22, 23, 24
INSERT INTO houses (dest_id, title, size, price_per_night) VALUES
(8, 'Traditional Machiya Townhouse', '2 BHK', 12500.00),
(8, 'Arashiyama Bamboo Cottage', '1 BHK', 7800.00),
(8, 'Zen Garden Villa', 'Villa', 20000.00);

-- 9. Maldives (dest_id = 9) -> House IDs 25, 26, 27
INSERT INTO houses (dest_id, title, size, price_per_night) VALUES
(9, 'Overwater Bungalow', 'Villa', 45000.00),
(9, 'Private Island Beach Hut', '1 BHK', 18000.00),
(9, 'Coral Reef Lagoon Villa', '2 BHK', 28000.00);

-- 10. Maui (dest_id = 10) -> House IDs 28, 29, 30
INSERT INTO houses (dest_id, title, size, price_per_night) VALUES
(10, 'Oceanfront Hawaiian Condo', '2 BHK', 16000.00),
(10, 'Lahaina Sunset Cottage', '1 BHK', 9500.00),
(10, 'Wailea Luxury Beach Estate', 'Villa', 35000.00);
