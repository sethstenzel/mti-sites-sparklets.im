import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'node:fs'
import path from 'node:path'

/*
 * Link previews (Open Graph / Twitter cards)
 * ------------------------------------------
 * Crawlers don't run JavaScript, so preview tags must be in the HTML itself.
 *
 *  - index.html gets the SITE preview (home page, /create, /example, …)
 *  - s.html gets the SPARKLET preview; nginx serves it for /s/<id> links.
 *    It is deliberately generic and never reveals who a sparklet is from or what it says.
 *
 * Images live in frontend/previews/ as  site-preview-<suffix>.<jpg|png|webp>  and
 * sparklet-preview-<suffix>.<…>. The file with the highest suffix wins, comparing the numbers
 * in it (v2 > v1, v10 > v9, 2026-12-01 > 2026-11-04 > v3). To change a preview, drop in a
 * file with a newer suffix and deploy; the new name also busts every cache.
 */
const SITE_URL = (process.env.SITE_URL || 'https://sparklets.im').replace(/\/$/, '')
const PREVIEW_DIR = path.resolve(__dirname, 'previews')

const PREVIEWS = {
  site: {
    title: 'Sparklets — little photo notes that open with a scan',
    description: 'Pick a photo, write a short note, and share it with a link or a printable QR code.',
    alt: 'Polaroid-style photo notes with the words: Little photo notes that open with a scan.'
  },
  sparklet: {
    title: 'You’ve got a sparklet ✨',
    description: 'A special message is waiting for you. Tap to open it.',
    alt: 'Polaroid-style photo notes with the words: You’ve got a sparklet. A special message is waiting for you.'
  }
}

const MIME = { '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp' }

// Compare suffixes by the numbers in them: v2 < v10, and dates (2026-12-01) beat small
// version numbers. Ties fall back to the file's modified time.
const suffixKey = (suffix) => (suffix.match(/\d+/g) || []).map(Number)
const compareSuffix = (a, b) => {
  const ka = suffixKey(a.suffix)
  const kb = suffixKey(b.suffix)
  for (let i = 0; i < Math.max(ka.length, kb.length); i++) {
    const d = (ka[i] ?? -1) - (kb[i] ?? -1)
    if (d) return d
  }
  return a.mtime - b.mtime
}

/** Newest file per kind, e.g. { site: 'site-preview-v2.jpg', sparklet: 'sparklet-preview-v1.jpg' }. */
const latestPreviews = () => {
  const pattern = /^(site|sparklet)-preview[-_](.+)\.(jpe?g|png|webp)$/i
  const best = {}
  for (const file of fs.readdirSync(PREVIEW_DIR)) {
    const m = file.match(pattern)
    if (!m) continue
    const kind = m[1].toLowerCase()
    const entry = { file, suffix: m[2], mtime: fs.statSync(path.join(PREVIEW_DIR, file)).mtimeMs }
    if (!best[kind] || compareSuffix(entry, best[kind]) > 0) best[kind] = entry
  }
  for (const kind of Object.keys(PREVIEWS)) {
    if (!best[kind]) throw new Error(`No ${kind}-preview-<suffix>.jpg found in ${PREVIEW_DIR}`)
  }
  return Object.fromEntries(Object.entries(best).map(([k, v]) => [k, v.file]))
}

const escapeAttr = (s) => s.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;')

const metaTags = (kind, file) => {
  const p = PREVIEWS[kind]
  const image = `${SITE_URL}/previews/${file}`
  const type = MIME[path.extname(file).toLowerCase()] || 'image/jpeg'
  const tags = [
    ['property', 'og:site_name', 'Sparklets'],
    ['property', 'og:type', 'website'],
    ['property', 'og:title', p.title],
    ['property', 'og:description', p.description],
    ['property', 'og:image', image],
    ['property', 'og:image:secure_url', image],
    ['property', 'og:image:type', type],
    ['property', 'og:image:width', '1200'],
    ['property', 'og:image:height', '630'],
    ['property', 'og:image:alt', p.alt],
    ['name', 'twitter:card', 'summary_large_image'],
    ['name', 'twitter:title', p.title],
    ['name', 'twitter:description', p.description],
    ['name', 'twitter:image', image],
    ['name', 'twitter:image:alt', p.alt],
    // sparklet links are private: never list them in search results
    ...(kind === 'sparklet' ? [['name', 'robots', 'noindex, nofollow']] : [])
  ]
  return tags.map(([attr, key, value]) => `<meta ${attr}="${key}" content="${escapeAttr(value)}">`).join('\n    ')
}

const BLOCK = /<!-- link-preview:start -->[\s\S]*?<!-- link-preview:end -->/

const linkPreviews = () => {
  let outDir = 'dist'
  let files = {}
  const block = (kind) => `<!-- link-preview:start -->\n    ${metaTags(kind, files[kind])}\n    <!-- link-preview:end -->`
  return {
    name: 'link-previews',
    configResolved(config) {
      outDir = path.resolve(config.root, config.build.outDir)
    },
    buildStart() {
      files = latestPreviews()
    },
    transformIndexHtml(html) {
      files = latestPreviews()
      return html.replace(BLOCK, block('site'))
    },
    generateBundle() {
      for (const file of Object.values(files)) {
        this.emitFile({ type: 'asset', fileName: `previews/${file}`, source: fs.readFileSync(path.join(PREVIEW_DIR, file)) })
      }
    },
    closeBundle() {
      // s.html = the built index.html with the sparklet preview swapped in
      const indexPath = path.join(outDir, 'index.html')
      if (!fs.existsSync(indexPath)) return
      const html = fs.readFileSync(indexPath, 'utf8')
      fs.writeFileSync(path.join(outDir, 's.html'), html.replace(BLOCK, block('sparklet')))
    },
    configureServer(server) {
      // dev: serve preview images straight from the folder
      server.middlewares.use('/previews', (req, res, next) => {
        const file = path.join(PREVIEW_DIR, path.basename(decodeURIComponent(req.url.split('?')[0])))
        if (!fs.existsSync(file)) return next()
        res.setHeader('Content-Type', MIME[path.extname(file).toLowerCase()] || 'application/octet-stream')
        fs.createReadStream(file).pipe(res)
      })
    }
  }
}

export default defineConfig({
  plugins: [vue(), linkPreviews()],
  define: {
    __SPARKLET_PREVIEW_URL__: JSON.stringify(`${SITE_URL}/previews/${latestPreviews().sparklet}`)
  },
  server: {
    port: 18003,
    proxy: {
      '/api': { target: 'http://localhost:18002', changeOrigin: true },
      '/contents': { target: 'http://localhost:18002', changeOrigin: true }
    }
  }
})
