# Link preview images

The pictures chat apps and social sites show when a Sparklets link is shared
(iMessage, WhatsApp, Facebook, X, Slack…). Size: **1200 × 630**, JPG/PNG/WebP.

| file name | used for |
|---|---|
| `sparklet-preview-<suffix>.jpg` | links to a sparklet (`/s/…`): "You’ve got a sparklet" |
| `site-preview-<suffix>.jpg` | everything else (home page, `/create`, `/example`) |

## Changing a preview

1. Add a new file with a **newer suffix**, e.g. `sparklet-preview-v2.jpg`
   (or a date: `sparklet-preview-2026-12-01.jpg`).
2. Deploy (`./deployment/deploy-prod.sh`).

The build picks the highest suffix for each kind (natural order: `v10` > `v9`,
later dates > earlier dates). Because the file name changes, every cache picks up the
new image. Old files can stay here or be deleted.

The preview *text* lives in `PREVIEWS` in `frontend/vite.config.js`.
