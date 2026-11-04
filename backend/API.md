# Sparklets API

Sparklets are addressed only by `public_id`: a random 22-character URL-safe token
(128 bits). Internal numeric ids never leave the server. Share links look like
`https://sparklets.im/s/<public_id>`.

## Public

### `GET /api/sparklets/{public_id}`

Returns one sparklet. `404` if it doesn't exist (or the id is malformed),
`403` if its `visibility` is `restricted` (reserved for the future user system).

```json
{
  "public_id": "Mz2s9bRSw6uW11Imur1THQ",
  "image_filename": "3f1c…​.jpg",
  "to_name": "Sarah",
  "from_name": "Alex",
  "message": "Good morning!",
  "background_color": "#f3e3f1",
  "card_color": "#fffaf5",
  "text_color": "#4b3f6b",
  "card_rotation": -4,
  "entry_animation": "pop",
  "font": "kalam",
  "visibility": "public",
  "created_at": "2026-11-04T17:14:56Z",
  "updated_at": "2026-11-04T17:14:56Z"
}
```

Images are served from `/contents/imgs/{image_filename}`.

### `POST /api/sparklets` (multipart form)

| field | rules |
|---|---|
| `to_name`, `from_name` | required, 1–20 chars |
| `message` | required, 1–140 chars |
| `background_color`, `card_color`, `text_color` | `#rrggbb` |
| `card_rotation` | −10…10 |
| `entry_animation` | `drop` `flip` `twirl` `rise` `pop` `none` |
| `font` | `kalam` `caveat` `pacifico` `fredoka` `playfair` `typewriter` |
| `image` | required; any image. Converted to JPEG ≤1000px wide, transparency filled with `card_color` |

Returns `201 {"public_id": "...", "message": "..."}`.

## Admin (header `X-Admin-Token: <ADMIN_TOKEN>`)

- `GET /api/admin/check`
- `GET /api/sparklets` – list all
- `PUT /api/sparklets/{public_id}` – same form fields as create; `image` optional
- `DELETE /api/sparklets/{public_id}` – also deletes the image file

## Access control (prepared, not active)

- `sparklets.visibility`: `public` (anyone with the link) or `restricted`
  (signed-in viewer listed in `sparklet_access`). Only `public` is used today.
- `sparklets.owner_user_id`: creator's account once users exist.
- `sparklet_access`: grants per sparklet to a `user_id` or an invited `email`, with a
  `role` (`viewer`/`editor`).
