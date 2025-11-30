import sqlite3

DATABASE = "database.db"

products = [
    {"name": "TCL Fire TV", "price": 115.99, "description": ""},
    {"name": "iPhone 15", "price": 999.99, "description": ""},
    {"name": "Samsung Galaxy S24", "price": 899.99, "description": ""},
    {"name": "Sony Headphones", "price": 199.99, "description": ""},
    {"name": "Dell Laptop", "price": 749.99, "description": ""},
    {"name": "Apple MacBook Air", "price": 1299.99, "description": ""},
    {"name": "Google Pixel 8", "price": 699.99, "description": ""},
    {"name": "Amazon Echo Dot", "price": 49.99, "description": ""},
    {"name": "Logitech MX Master 3 Mouse", "price": 99.99, "description": ""},
    {"name": "Kindle Paperwhite", "price": 139.99, "description": ""},
    {"name": "Nintendo Switch", "price": 299.99, "description": ""},
    {"name": "Sony PlayStation 5", "price": 499.99, "description": ""},
    {"name": "Xbox Series X", "price": 499.99, "description": ""},
    {"name": "Apple AirPods Pro", "price": 249.99, "description": ""},
    {"name": "Samsung Galaxy Tab S9", "price": 649.99, "description": ""}
]

conn = sqlite3.connect(DATABASE)
cur = conn.cursor()


cur.executescript('''
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS products;
''')

cur.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0
)
''')

cur.execute('''
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT
)
''')

cur.execute('''
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

for p in products:
    cur.execute(
        "INSERT INTO products (name, price, description) VALUES (?, ?, ?)",
        (p["name"], p["price"], p["description"])
    )

conn.commit()
conn.close()

print("Database initialized successfully")