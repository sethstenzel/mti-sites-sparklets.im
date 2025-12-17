from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image

from database import get_db, init_db

app = FastAPI(
    title="Sparklets.im API",
    description="Backend API for Sparklets.im",
    version="0.1.0",
)

# Helper function to resize images
def resize_image(image_bytes: bytes, max_width: int = 1000) -> bytes:
    """Resize image to max width while maintaining aspect ratio"""
    img = Image.open(image_bytes)

    # Convert RGBA to RGB if necessary
    if img.mode == 'RGBA':
        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
        rgb_img.paste(img, mask=img.split()[3])
        img = rgb_img

    # Calculate new dimensions
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

    # Save to bytes
    from io import BytesIO
    output = BytesIO()
    img.save(output, format='JPEG', quality=90)
    return output.getvalue()

# Configure CORS
import os
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:18003").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Mount static files for images
CONTENTS_DIR = Path(__file__).parent / "contents"
app.mount("/contents", StaticFiles(directory=str(CONTENTS_DIR)), name="contents")


@app.get("/")
async def root():
    return {"message": "Welcome to Sparklets.im API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/sparklets")
async def get_all_sparklets():
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM sparklets ORDER BY date_created DESC"
        )
        rows = cursor.fetchall()

        return [
            {
                "id": row["id"],
                "image_filename": row["image_filename"],
                "to_name": row["to_name"],
                "from_name": row["from_name"],
                "message": row["message"],
                "date_created": row["date_created"],
                "background_color": row["background_color"],
                "card_color": row["card_color"],
                "text_color": row["text_color"],
                "card_rotation": row["card_rotation"],
                "image_offset_x": row["image_offset_x"],
                "image_offset_y": row["image_offset_y"],
                "image_scale": row["image_scale"],
            }
            for row in rows
        ]


@app.get("/api/sparklets/{sparklet_id}")
async def get_sparklet(sparklet_id: int):
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM sparklets WHERE id = ?", (sparklet_id,)
        )
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Sparklet not found")

        return {
            "id": row["id"],
            "image_filename": row["image_filename"],
            "to_name": row["to_name"],
            "from_name": row["from_name"],
            "message": row["message"],
            "date_created": row["date_created"],
            "background_color": row["background_color"],
            "card_color": row["card_color"],
            "text_color": row["text_color"],
            "card_rotation": row["card_rotation"],
            "image_offset_x": row["image_offset_x"],
            "image_offset_y": row["image_offset_y"],
            "image_scale": row["image_scale"],
        }


@app.post("/api/sparklets")
async def create_sparklet(
    to_name: str = Form(...),
    from_name: str = Form(...),
    message: str = Form(..., max_length=100),
    background_color: str = Form(default="#f0f0f0"),
    card_color: str = Form(default="#ffffff"),
    text_color: str = Form(default="#333333"),
    card_rotation: int = Form(default=5),
    image_offset_x: float = Form(default=0),
    image_offset_y: float = Form(default=0),
    image_scale: float = Form(default=1),
    image: UploadFile = File(...),
):
    # Read and resize uploaded image
    image_content = await image.read()
    from io import BytesIO
    resized_image = resize_image(BytesIO(image_content))

    # Save resized image
    image_filename = f"{datetime.now().timestamp()}_{image.filename}"
    image_path = CONTENTS_DIR / "imgs" / image_filename

    with open(image_path, "wb") as f:
        f.write(resized_image)

    # Insert into database
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO sparklets
            (image_filename, to_name, from_name, message, background_color, card_color, text_color, card_rotation, image_offset_x, image_offset_y, image_scale)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (image_filename, to_name, from_name, message, background_color, card_color, text_color, card_rotation, image_offset_x, image_offset_y, image_scale),
        )
        conn.commit()
        sparklet_id = cursor.lastrowid

    return {"id": sparklet_id, "message": "Sparklet created successfully"}


@app.put("/api/sparklets/{sparklet_id}")
async def update_sparklet(
    sparklet_id: int,
    to_name: str = Form(...),
    from_name: str = Form(...),
    message: str = Form(..., max_length=100),
    background_color: str = Form(default="#f0f0f0"),
    card_color: str = Form(default="#ffffff"),
    text_color: str = Form(default="#333333"),
    card_rotation: int = Form(default=5),
    image: UploadFile = File(None),
):
    with get_db() as conn:
        # Check if sparklet exists
        cursor = conn.execute(
            "SELECT image_filename FROM sparklets WHERE id = ?", (sparklet_id,)
        )
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Sparklet not found")

        # Handle image update if provided
        image_filename = row["image_filename"]
        if image:
            # Delete old image
            old_image_path = CONTENTS_DIR / "imgs" / image_filename
            if old_image_path.exists():
                old_image_path.unlink()

            # Read and resize new image
            image_content = await image.read()
            from io import BytesIO
            resized_image = resize_image(BytesIO(image_content))

            # Save resized image
            image_filename = f"{datetime.now().timestamp()}_{image.filename}"
            image_path = CONTENTS_DIR / "imgs" / image_filename

            with open(image_path, "wb") as f:
                f.write(resized_image)

        # Update database
        conn.execute(
            """
            UPDATE sparklets
            SET to_name = ?, from_name = ?, message = ?,
                background_color = ?, card_color = ?, text_color = ?,
                card_rotation = ?, image_filename = ?
            WHERE id = ?
            """,
            (to_name, from_name, message, background_color, card_color, text_color, card_rotation, image_filename, sparklet_id),
        )
        conn.commit()

    return {"id": sparklet_id, "message": "Sparklet updated successfully"}


@app.delete("/api/sparklets/{sparklet_id}")
async def delete_sparklet(sparklet_id: int):
    with get_db() as conn:
        # First, get the sparklet to find the image filename
        cursor = conn.execute(
            "SELECT image_filename FROM sparklets WHERE id = ?", (sparklet_id,)
        )
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Sparklet not found")

        # Delete the image file
        image_path = CONTENTS_DIR / "imgs" / row["image_filename"]
        if image_path.exists():
            image_path.unlink()

        # Delete from database
        conn.execute("DELETE FROM sparklets WHERE id = ?", (sparklet_id,))
        conn.commit()

    return {"message": "Sparklet deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=18002, reload=True)
