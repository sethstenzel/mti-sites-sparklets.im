# Sparklets.IM Backend

FastAPI backend for Sparklets.IM

## Setup

1. Install dependencies using uv:
```bash
cd backend
uv sync
```

2. Create demo sparklet (optional but recommended):
```bash
uv run python seed_demo.py
```

This will create:
- A demo image at `contents/imgs/demo.jpg`
- A demo sparklet with ID 1 in the database

3. Run the development server:
```bash
uv run python main.py
```

Or use uvicorn directly:
```bash
uv run uvicorn main:app --reload
```

The API will be available at http://localhost:18002

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:18002/docs
- ReDoc: http://localhost:18002/redoc

## Development

Run tests:
```bash
uv run pytest
```

Format code:
```bash
uv run ruff check --fix
```
