import os
import re
import secrets
import uuid
from contextlib import asynccontextmanager
from io import BytesIO
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageOps, UnidentifiedImageError

from database import get_db, init_db

BASE_DIR = Path(__file__).parent
CONTENTS_DIR = BASE_DIR / "contents"
IMAGES_DIR = CONTENTS_DIR / "imgs"


def _load_dotenv(path: Path) -> None:
    """Load KEY=VALUE pairs from a .env file without overriding real env vars."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


_load_dotenv(BASE_DIR / ".env")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:18003").split(",")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

MAX_NAME_LENGTH = 20
MAX_MESSAGE_LENGTH = 140
MAX_IMAGE_WIDTH = 1000  # 2x the largest card the site renders
JPEG_QUALITY = 82
HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
ANIMATIONS = {"drop", "flip", "twirl", "rise", "pop", "none"}
DEFAULT_ANIMATION = "drop"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    init_db()
    yield


app = FastAPI(
    title="Sparklets.im API",
    description="Backend API for Sparklets.im",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IMAGES_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/contents", StaticFiles(directory=str(CONTENTS_DIR)), name="contents")


# ---------- helpers ----------


def require_admin(x_admin_token: str = Header(default="")) -> None:
    if not ADMIN_TOKEN:
        raise HTTPException(
            status_code=503, detail="Management is disabled. Set ADMIN_TOKEN on the server."
        )
    if not secrets.compare_digest(x_admin_token, ADMIN_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid admin token")


def validate_color(value: str, field: str) -> str:
    if not HEX_COLOR.match(value):
        raise HTTPException(status_code=422, detail=f"{field} must be a hex color like #aabbcc")
    return value.lower()


def validate_animation(value: str) -> str:
    return value if value in ANIMATIONS else DEFAULT_ANIMATION


def validate_text(value: str, field: str, max_length: int) -> str:
    value = value.strip()
    if not value:
        raise HTTPException(status_code=422, detail=f"{field} is required")
    if len(value) > max_length:
        raise HTTPException(
            status_code=422, detail=f"{field} must be {max_length} characters or fewer"
        )
    return value


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def process_image(data: bytes, matte: str = "#ffffff", max_width: int = MAX_IMAGE_WIDTH) -> bytes:
    """Normalize an upload: fix EXIF rotation, flatten transparency onto the card color,
    cap the width and encode as a compact progressive JPEG (metadata stripped)."""
    try:
        img = Image.open(BytesIO(data))
        img = ImageOps.exif_transpose(img)
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=400, detail="That file isn't a supported image") from exc

    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
        background = Image.new("RGB", img.size, hex_to_rgb(matte))
        background.paste(img, mask=img.split()[-1])
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    if img.width > max_width:
        new_height = round(img.height * max_width / img.width)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

    output = BytesIO()
    img.save(output, format="JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    return output.getvalue()


async def save_upload(image: UploadFile, matte: str) -> str:
    processed = process_image(await image.read(), matte)
    filename = f"{uuid.uuid4().hex}.jpg"
    (IMAGES_DIR / filename).write_bytes(processed)
    return filename


def delete_image(filename: str) -> None:
    # Never delete the seeded demo image, and never follow path components.
    if not filename or filename == "demo.jpg" or Path(filename).name != filename:
        return
    path = IMAGES_DIR / filename
    if path.exists():
        path.unlink()


def row_to_dict(row) -> dict:
    created = row["date_created"]
    # SQLite CURRENT_TIMESTAMP is UTC without a zone; make that explicit for clients.
    if created and "T" not in created and not created.endswith("Z"):
        created = created.replace(" ", "T") + "Z"
    rotation = row["card_rotation"]
    return {
        "id": row["id"],
        "image_filename": row["image_filename"],
        "to_name": row["to_name"],
        "from_name": row["from_name"],
        "message": row["message"],
        "date_created": created,
        "background_color": row["background_color"],
        "card_color": row["card_color"],
        "text_color": row["text_color"],
        "card_rotation": 5 if rotation is None else rotation,
        "entry_animation": row["entry_animation"] or DEFAULT_ANIMATION,
        "image_offset_x": row["image_offset_x"] or 0,
        "image_offset_y": row["image_offset_y"] or 0,
        "image_scale": row["image_scale"] or 1,
    }


# ---------- routes ----------


@app.get("/")
async def root():
    return {"message": "Welcome to Sparklets.im API"}


@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/admin/check", dependencies=[Depends(require_admin)])
async def admin_check():
    return {"ok": True}


@app.get("/api/sparklets", dependencies=[Depends(require_admin)])
async def get_all_sparklets():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM sparklets ORDER BY date_created DESC, id DESC").fetchall()
        return [row_to_dict(row) for row in rows]


@app.get("/api/sparklets/{sparklet_id}")
async def get_sparklet(sparklet_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM sparklets WHERE id = ?", (sparklet_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Sparklet not found")
        return row_to_dict(row)


@app.post("/api/sparklets")
async def create_sparklet(
    to_name: str = Form(...),
    from_name: str = Form(...),
    message: str = Form(...),
    background_color: str = Form(default="#f0f0f0"),
    card_color: str = Form(default="#ffffff"),
    text_color: str = Form(default="#333333"),
    card_rotation: int = Form(default=5),
    entry_animation: str = Form(default=DEFAULT_ANIMATION),
    image: UploadFile = File(...),
):
    values = (
        validate_text(to_name, "To", MAX_NAME_LENGTH),
        validate_text(from_name, "From", MAX_NAME_LENGTH),
        validate_text(message, "Message", MAX_MESSAGE_LENGTH),
        validate_color(background_color, "Background color"),
        validate_color(card_color, "Card color"),
        validate_color(text_color, "Text color"),
        max(-10, min(10, card_rotation)),
        validate_animation(entry_animation),
    )
    image_filename = await save_upload(image, matte=values[4])

    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO sparklets
            (to_name, from_name, message, background_color, card_color, text_color,
             card_rotation, entry_animation, image_filename,
             image_offset_x, image_offset_y, image_scale)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 1)
            """,
            (*values, image_filename),
        )
        conn.commit()
        sparklet_id = cursor.lastrowid

    return {"id": sparklet_id, "message": "Sparklet created successfully"}


@app.put("/api/sparklets/{sparklet_id}", dependencies=[Depends(require_admin)])
async def update_sparklet(
    sparklet_id: int,
    to_name: str = Form(...),
    from_name: str = Form(...),
    message: str = Form(...),
    background_color: str = Form(default="#f0f0f0"),
    card_color: str = Form(default="#ffffff"),
    text_color: str = Form(default="#333333"),
    card_rotation: int = Form(default=5),
    entry_animation: str = Form(default=DEFAULT_ANIMATION),
    image: UploadFile | None = File(default=None),
):
    values = (
        validate_text(to_name, "To", MAX_NAME_LENGTH),
        validate_text(from_name, "From", MAX_NAME_LENGTH),
        validate_text(message, "Message", MAX_MESSAGE_LENGTH),
        validate_color(background_color, "Background color"),
        validate_color(card_color, "Card color"),
        validate_color(text_color, "Text color"),
        max(-10, min(10, card_rotation)),
        validate_animation(entry_animation),
    )

    with get_db() as conn:
        row = conn.execute(
            "SELECT image_filename FROM sparklets WHERE id = ?", (sparklet_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Sparklet not found")

        image_filename = row["image_filename"]
        if image is not None and image.filename:
            new_filename = await save_upload(image, matte=values[4])
            delete_image(image_filename)
            image_filename = new_filename

        conn.execute(
            """
            UPDATE sparklets
            SET to_name = ?, from_name = ?, message = ?,
                background_color = ?, card_color = ?, text_color = ?,
                card_rotation = ?, entry_animation = ?, image_filename = ?,
                image_offset_x = 0, image_offset_y = 0, image_scale = 1
            WHERE id = ?
            """,
            (*values, image_filename, sparklet_id),
        )
        conn.commit()

    return {"id": sparklet_id, "message": "Sparklet updated successfully"}


@app.delete("/api/sparklets/{sparklet_id}", dependencies=[Depends(require_admin)])
async def delete_sparklet(sparklet_id: int):
    with get_db() as conn:
        row = conn.execute(
            "SELECT image_filename FROM sparklets WHERE id = ?", (sparklet_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Sparklet not found")

        delete_image(row["image_filename"])
        conn.execute("DELETE FROM sparklets WHERE id = ?", (sparklet_id,))
        conn.commit()

    return {"message": "Sparklet deleted successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=18002, reload=True)
