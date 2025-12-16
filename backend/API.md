# Sparklets API Documentation

## Endpoints

### GET /api/sparklets/{sparklet_id}

Get a sparklet by ID.

**Parameters:**
- `sparklet_id` (path): Integer ID of the sparklet

**Response:**
```json
{
  "id": 1,
  "image_filename": "demo.jpg",
  "to_name": "Sarah",
  "from_name": "Alex",
  "message": "Hope you're having an amazing day!",
  "date_created": "2024-01-01T12:00:00",
  "background_color": "#FFF8DC",
  "card_color": "#FFFACD",
  "text_color": "#2F4F4F"
}
```

### POST /api/sparklets

Create a new sparklet.

**Form Data:**
- `to_name` (required): Recipient name (max 100 chars)
- `from_name` (required): Sender name (max 100 chars)
- `message` (required): Message text (max 140 chars)
- `image` (required): Image file
- `background_color` (optional): Hex color, default "#f0f0f0"
- `card_color` (optional): Hex color, default "#ffffff"
- `text_color` (optional): Hex color, default "#333333"

**Response:**
```json
{
  "id": 2,
  "message": "Sparklet created successfully"
}
```

## Static Files

### GET /contents/imgs/{filename}

Access uploaded images directly.

**Example:**
```
http://localhost:8000/contents/imgs/demo.jpg
```
