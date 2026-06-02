# Asset-Energy AI landing page

This folder contains a simple, modern, responsive static landing page:

- `index.html`
- `styles.css`
- `Asset-Energy.ai Energy Policy .png` (existing image)

## Run locally

From this directory:

```bash
python3 -m http.server 5173
```

Then open `http://localhost:5173`.

## News (standalone articles)

- `news/posts.json` — source of truth (title/date/slug/excerpt)
- `news.html` — generated list of posts (do not edit by hand)
- `news/your-article-slug.html` — full article page

To add a post:

1. Run:

```bash
cd "/Users/richardcrounse/Documents/Asset-Energy-Web"
python3 scripts/new-oped.py "Your headline" --deck "One-sentence summary"
```

2. Open the created file under `news/` in Cursor and write the OpEd (edit `.article-full-body`).
3. Commit and push (GitHub Desktop → **Push origin**).

If you ever need to regenerate the index:

```bash
python3 scripts/build-news.py
```

## Next steps (optional)

- Deploy to Cloudflare Pages (static).
- Replace the `AE` mark with a proper logo and update the favicon.
- Add analytics (Plausible / GA) if you want usage metrics.

## Deploy (Cloudflare Pages + static site)

### 1) Create a Cloudflare Pages project

- In Cloudflare Dashboard → **Pages** → **Create a project**
- Choose **Direct upload** (quick) or connect a Git repo
- Upload / deploy the contents of this folder

### 2) Domain

In Cloudflare Pages → your project → **Custom domains**, add:

- `asset-energy.ai`

Cloudflare will guide you through the DNS records.

