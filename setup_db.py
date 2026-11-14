import sqlite3

conn = sqlite3.connect("bella_store.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    price REAL,
    sizes TEXT,
    colors TEXT,
    stock_status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_name TEXT,
    item_ordered TEXT,
    status TEXT,
    estimated_delivery TEXT,
    tracking_courier TEXT
)
""")

cursor.execute("DELETE FROM products")
cursor.execute("DELETE FROM orders")

products_data = [
    ("Men's Casual Cotton T-Shirt", "Men's Wear", 2200.00, "S, M, L, XL", "Black, White, Navy Blue", "In Stock"),
    ("Women's Linen Kurti", "Women's Wear", 3400.00, "S, M, L", "Pink, Yellow, Mint Green", "In Stock"),
    ("Unisex Denim Jacket", "Outerwear", 5500.00, "M, L, XL", "Blue, Black", "Limited Stock (Only 3 left)"),
    ("Cotton Chino Pants", "Bottoms", 3800.00, "30, 32, 34, 36", "Beige, Charcoal Grey", "In Stock")
]
cursor.executemany("INSERT INTO products (name, category, price, sizes, colors, stock_status) VALUES (?, ?, ?, ?, ?, ?)", products_data)

orders_data = [
    ("ORD-101", "Kasun Perera", "Men's Casual Cotton T-Shirt (L, Black)", "Delivered", "Delivered on Nov 12, 2026", "Domex Express"),
    ("ORD-102", "Nethmi Silva", "Women's Linen Kurti (M, Pink)", "Out for Delivery", "Expected Today before 6:00 PM", "PromptXP Courier"),
    ("ORD-103", "Dilshan Bandara", "Unisex Denim Jacket (XL, Blue)", "Processing & Packing", "Expected Nov 16, 2026", "Koombiyo Delivery"),
    ("ORD-104", "Amaya Fernando", "Cotton Chino Pants (32, Beige)", "Shipped - In Transit (Kandy Hub)", "Expected Tomorrow", "Domex Express")
]
cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", orders_data)

conn.commit()
conn.close()
print("Database 'bella_store.db' created successfully!")