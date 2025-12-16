# Sparklets.IM

Website for making and sending QR code based message cards.

## Project Structure

This is a full-stack application with:

- **Frontend**: Vue 3 + Vite (in `/frontend`)
- **Backend**: FastAPI + Python (in `/backend`)

```text
sparklets.im/
├── backend/           # FastAPI backend
│   ├── main.py       # Main application entry point
│   ├── pyproject.toml # Python dependencies (managed by uv)
│   └── README.md     # Backend documentation
├── frontend/         # Vue 3 frontend
│   ├── src/          # Vue source code
│   ├── package.json  # Node dependencies
│   ├── vite.config.js # Vite configuration
│   └── README.md     # Frontend documentation
├── .gitignore
├── .env.example
└── README.md
```

## Quick Start

### Backend Setup

1. Navigate to the backend directory:

```bash
cd backend
```

2. Install dependencies using uv:

```bash
uv sync
```

3. Run the development server:

```bash
uv run python main.py
```

The API will be available at <http://localhost:8000>

- Swagger docs: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Run the development server:

```bash
npm run dev
```

The application will be available at <http://localhost:5173>

## Development

The frontend is configured to proxy API requests to the backend. Requests to `/api/*` will be forwarded to `http://localhost:8000`.

### Tech Stack

**Backend:**

- FastAPI
- Python 3.11+
- Uvicorn (ASGI server)
- Pydantic (data validation)
- uv (package management)

**Frontend:**

- Vue 3 (Composition API)
- Vite (build tool)
- Vue Router (routing)
- Pinia (state management)
- Axios (HTTP client)

## Environment Variables

Copy `.env.example` to `.env` and configure as needed:

```bash
cp .env.example .env
```

## License

MIT
