import os
import re
import secrets
import uuid
from contextlib import asynccontextmanager
from io import BytesIO
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi import Path as FPath
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
# keep in sync with frontend/src/lib/fonts.js
FONTS = {"kalam", "caveat", "pacifico", "fredoka", "playfair", "typewriter"}
DEFAULT_FONT = "kalam"


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
    # Never follow path components out of the images directory.
    if not filename or Path(filename).name != filename:
        return
    path = IMAGES_DIR / filename
    if path.exists():
        path.unlink()


# ---------- public ids ----------

# 16 random bytes = 128 bits -> 22 URL-safe characters. Not guessable, and changing a
# few characters of a real link lands on an id that (practically) never exists.
PUBLIC_ID_BYTES = 16
PUBLIC_ID_PATTERN = r"^[A-Za-z0-9_-]{22}$"


def new_public_id(conn) -> str:
    while True:
        candidate = secrets.token_urlsafe(PUBLIC_ID_BYTES)
        if not conn.execute("SELECT 1 FROM sparklets WHERE public_id = ?", (candidate,)).fetchone():
            return candidate


def iso_utc(value: str | None) -> str | None:
    # SQLite CURRENT_TIMESTAMP is UTC without a zone; make that explicit for clients.
    if value and "T" not in value and not value.endswith("Z"):
        return value.replace(" ", "T") + "Z"
    return value


def row_to_dict(row) -> dict:
    # The internal numeric id is deliberately never returned.
    return {
        "public_id": row["public_id"],
        "image_filename": row["image_filename"],
        "to_name": row["to_name"],
        "from_name": row["from_name"],
        "message": row["message"],
        "background_color": row["background_color"],
        "card_color": row["card_color"],
        "text_color": row["text_color"],
        "card_rotation": row["card_rotation"],
        "entry_animation": row["entry_animation"] or DEFAULT_ANIMATION,
        "font": row["font"] or DEFAULT_FONT,
        "visibility": row["visibility"],
        "created_at": iso_utc(row["created_at"]),
        "updated_at": iso_utc(row["updated_at"]),
    }


def can_view(row) -> bool:
    """Only 'public' exists today. 'restricted' will require a signed-in viewer who is
    listed in sparklet_access once the user system lands."""
    return row["visibility"] == "public"


def fetch_by_public_id(conn, public_id: str):
    row = conn.execute("SELECT * FROM sparklets WHERE public_id = ?", (public_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Sparklet not found")
    return row


PublicId = Annotated[str, FPath(pattern=PUBLIC_ID_PATTERN)]


def sparklet_fields(
    to_name: str = Form(...),
    from_name: str = Form(...),
    message: str = Form(...),
    background_color: str = Form(default="#f0f0f0"),
    card_color: str = Form(default="#ffffff"),
    text_color: str = Form(default="#333333"),
    card_rotation: int = Form(default=5),
    entry_animation: str = Form(default=DEFAULT_ANIMATION),
    font: str = Form(default=DEFAULT_FONT),
) -> dict:
    return {
        "to_name": validate_text(to_name, "To", MAX_NAME_LENGTH),
        "from_name": validate_text(from_name, "From", MAX_NAME_LENGTH),
        "message": validate_text(message, "Message", MAX_MESSAGE_LENGTH),
        "background_color": validate_color(background_color, "Background color"),
        "card_color": validate_color(card_color, "Card color"),
        "text_color": validate_color(text_color, "Text color"),
        "card_rotation": max(-10, min(10, card_rotation)),
        "entry_animation": validate_animation(entry_animation),
        "font": font if font in FONTS else DEFAULT_FONT,
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
async def list_sparklets():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM sparklets ORDER BY created_at DESC, id DESC").fetchall()
        return [row_to_dict(row) for row in rows]


@app.get("/api/sparklets/{public_id}")
async def get_sparklet(public_id: PublicId):
    with get_db() as conn:
        row = fetch_by_public_id(conn, public_id)
        if not can_view(row):
            raise HTTPException(status_code=403, detail="Sign in to view this sparklet")
        return row_to_dict(row)


@app.post("/api/sparklets", status_code=201)
async def create_sparklet(
    fields: dict = Depends(sparklet_fields),
    image: UploadFile = File(...),
):
    image_filename = await save_upload(image, matte=fields["card_color"])
    with get_db() as conn:
        public_id = new_public_id(conn)
        conn.execute(
            """
            INSERT INTO sparklets
            (public_id, to_name, from_name, message, image_filename, background_color,
             card_color, text_color, card_rotation, entry_animation, font)
            VALUES (:public_id, :to_name, :from_name, :message, :image_filename,
                    :background_color, :card_color, :text_color, :card_rotation,
                    :entry_animation, :font)
            """,
            {**fields, "public_id": public_id, "image_filename": image_filename},
        )
        conn.commit()
    return {"public_id": public_id, "message": "Sparklet created successfully"}


@app.put("/api/sparklets/{public_id}", dependencies=[Depends(require_admin)])
async def update_sparklet(
    public_id: PublicId,
    fields: dict = Depends(sparklet_fields),
    image: UploadFile | None = File(default=None),
):
    with get_db() as conn:
        row = fetch_by_public_id(conn, public_id)
        image_filename = row["image_filename"]
        if image is not None and image.filename:
            new_filename = await save_upload(image, matte=fields["card_color"])
            delete_image(image_filename)
            image_filename = new_filename

        conn.execute(
            """
            UPDATE sparklets
            SET to_name = :to_name, from_name = :from_name, message = :message,
                background_color = :background_color, card_color = :card_color,
                text_color = :text_color, card_rotation = :card_rotation,
                entry_animation = :entry_animation, font = :font,
                image_filename = :image_filename,
                updated_at = CURRENT_TIMESTAMP
            WHERE public_id = :public_id
            """,
            {**fields, "image_filename": image_filename, "public_id": public_id},
        )
        conn.commit()
    return {"public_id": public_id, "message": "Sparklet updated successfully"}


@app.delete("/api/sparklets/{public_id}", dependencies=[Depends(require_admin)])
async def delete_sparklet(public_id: PublicId):
    with get_db() as conn:
        row = fetch_by_public_id(conn, public_id)
        delete_image(row["image_filename"])
        conn.execute("DELETE FROM sparklets WHERE id = ?", (row["id"],))
        conn.commit()
    return {"message": "Sparklet deleted successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=18002, reload=True)
