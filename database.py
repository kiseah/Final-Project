import mysql.connector

# DATABASE SETUP
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="barangay profiling"
)
cursor = conn.cursor()

current_geometry = "800x500"
is_fullscreen = False

# CREATE TABLES IF NOT EXIST
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(50)
) 
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS residents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resident_id VARCHAR(20) UNIQUE,
    full_name VARCHAR(255),
    gender VARCHAR(10),
    birthdate DATE,
    house_no VARCHAR(20),
    purok_zone VARCHAR(20)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS households (
    id INT AUTO_INCREMENT PRIMARY KEY,
    household_code VARCHAR(10),
    house_no VARCHAR(100),
    purok_zone VARCHAR(100),
    head_of_family VARCHAR(200),
    total_members INT(11)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS barangay_mintal_officials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    region VARCHAR(100),
    province VARCHAR(100),
    city_municipality VARCHAR(100),
    barangay VARCHAR(100),
    position VARCHAR(100),
    lastname VARCHAR(100),
    firstname VARCHAR(100),
    middlename VARCHAR(100),
    suffix VARCHAR(20),
    email_address VARCHAR(150),
    barangay_hall_telno VARCHAR(50)
)
""")

# ensure default admin exists
cursor.execute("SELECT * FROM users WHERE username = 'admin'")
if cursor.fetchone() is None:
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", ("admin", "1234"))
    conn.commit()