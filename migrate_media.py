"""
Migration script: Add video_url column to products table
and create product_images table.
"""
import sqlite3
import os

DB_PATH = os.path.join('instance', 'traiteur.db')

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Check existing columns
c.execute("PRAGMA table_info(products)")
cols = [row[1] for row in c.fetchall()]
print("Existing product columns:", cols)

# Add video_url if missing
if 'video_url' not in cols:
    c.execute("ALTER TABLE products ADD COLUMN video_url TEXT")
    print("Added video_url column to products table")
else:
    print("video_url column already exists")

# Create product_images table if missing
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='product_images'")
if not c.fetchone():
    c.execute("""
        CREATE TABLE product_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            image_url TEXT NOT NULL,
            position INTEGER DEFAULT 0,
            is_primary BOOLEAN DEFAULT 0,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    print("Created product_images table")
else:
    print("product_images table already exists")

# Migrate existing images to product_images table
c.execute("SELECT id, image FROM products WHERE image IS NOT NULL AND image != ''")
products_with_images = c.fetchall()
for prod_id, image_url in products_with_images:
    # Check if already migrated
    c.execute("SELECT id FROM product_images WHERE product_id = ?", (prod_id,))
    if not c.fetchone():
        c.execute(
            "INSERT INTO product_images (product_id, image_url, position, is_primary) VALUES (?, ?, 1, 1)",
            (prod_id, image_url)
        )
        print(f"  Migrated image for product {prod_id}")

conn.commit()
conn.close()
print("\nMigration complete!")
