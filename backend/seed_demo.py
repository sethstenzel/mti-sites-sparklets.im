"""Seed the database with a demo sparklet."""
import sqlite3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Create a demo image
def create_demo_image():
    # Create a 400x400 image with a gradient background
    img = Image.new('RGB', (400, 400), color='#87CEEB')
    draw = ImageDraw.Draw(img)

    # Draw a simple sun
    draw.ellipse([150, 100, 250, 200], fill='#FFD700', outline='#FFA500', width=3)

    # Draw some clouds
    draw.ellipse([50, 50, 120, 90], fill='white')
    draw.ellipse([80, 40, 150, 80], fill='white')
    draw.ellipse([280, 60, 350, 100], fill='white')
    draw.ellipse([310, 50, 380, 90], fill='white')

    # Draw a simple landscape
    draw.polygon([(0, 300), (200, 200), (400, 300)], fill='#90EE90')
    draw.polygon([(100, 300), (300, 150), (400, 300)], fill='#3CB371')

    # Save the image
    img_path = Path(__file__).parent / "contents" / "imgs" / "demo.jpg"
    img.save(img_path, 'JPEG')
    print(f"Demo image created at {img_path}")


def seed_database():
    db_path = Path(__file__).parent / "sparklets.sqlite"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sparklets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_filename TEXT NOT NULL,
            to_name TEXT NOT NULL,
            from_name TEXT NOT NULL,
            message TEXT NOT NULL,
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            background_color TEXT NOT NULL,
            card_color TEXT NOT NULL,
            text_color TEXT NOT NULL,
            card_rotation INTEGER DEFAULT 5
        )
    """)

    # Check if demo sparklet already exists
    cursor.execute("SELECT id FROM sparklets WHERE id = 1")
    if cursor.fetchone():
        print("Demo sparklet already exists")
        conn.close()
        return

    # Insert demo sparklet
    cursor.execute("""
        INSERT INTO sparklets
        (id, image_filename, to_name, from_name, message, background_color, card_color, text_color, card_rotation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        1,
        "demo.jpg",
        "Sarah",
        "Alex",
        "Hope you're having an amazing day! Just wanted to send some sunshine your way. Can't wait to catch up soon! ☀️",
        "#FFF8DC",
        "#FFFACD",
        "#2F4F4F",
        7
    ))

    conn.commit()
    conn.close()
    print("Demo sparklet created with ID 1")


if __name__ == "__main__":
    create_demo_image()
    seed_database()
