from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import get_db, init_db

app = FastAPI(
    title="Sparklets.IM API",
    description="Backend API for Sparklets.IM",
    version="0.1.0",
)

# Configure CORS
import os
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

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
    return {"message": "Welcome to Sparklets.IM API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/sparklets")
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
            }
            for row in rows
        ]


@app.get("/sparklets/{sparklet_id}")
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
        }


@app.post("/sparklets")
async def create_sparklet(
    to_name: str = Form(...),
    from_name: str = Form(...),
    message: str = Form(..., max_length=140),
    background_color: str = Form(default="#f0f0f0"),
    card_color: str = Form(default="#ffffff"),
    text_color: str = Form(default="#333333"),
    image: UploadFile = File(...),
):
    # Save uploaded image
    image_filename = f"{datetime.now().timestamp()}_{image.filename}"
    image_path = CONTENTS_DIR / "imgs" / image_filename

    with open(image_path, "wb") as f:
        content = await image.read()
        f.write(content)

    # Insert into database
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO sparklets
            (image_filename, to_name, from_name, message, background_color, card_color, text_color)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (image_filename, to_name, from_name, message, background_color, card_color, text_color),
        )
        conn.commit()
        sparklet_id = cursor.lastrowid

    return {"id": sparklet_id, "message": "Sparklet created successfully"}


@app.put("/sparklets/{sparklet_id}")
async def update_sparklet(
    sparklet_id: int,
    to_name: str = Form(...),
    from_name: str = Form(...),
    message: str = Form(..., max_length=140),
    background_color: str = Form(default="#f0f0f0"),
    card_color: str = Form(default="#ffffff"),
    text_color: str = Form(default="#333333"),
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

            # Save new image
            image_filename = f"{datetime.now().timestamp()}_{image.filename}"
            image_path = CONTENTS_DIR / "imgs" / image_filename

            with open(image_path, "wb") as f:
                content = await image.read()
                f.write(content)

        # Update database
        conn.execute(
            """
            UPDATE sparklets
            SET to_name = ?, from_name = ?, message = ?,
                background_color = ?, card_color = ?, text_color = ?,
                image_filename = ?
            WHERE id = ?
            """,
            (to_name, from_name, message, background_color, card_color, text_color, image_filename, sparklet_id),
        )
        conn.commit()

    return {"id": sparklet_id, "message": "Sparklet updated successfully"}


@app.delete("/sparklets/{sparklet_id}")
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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
