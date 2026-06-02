#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
POSTS_PATH = ROOT / "news" / "posts.json"
NEWS_DIR = ROOT / "news"
BUILD_SCRIPT = ROOT / "scripts" / "build-news.py"


def slugify(title: str) -> str:
    s = (title or "").strip().lower()
    s = s.replace("’", "").replace("'", "")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "oped"


def parse_date(value: str | None) -> date:
    if not value:
        return datetime.now().date()
    return datetime.strptime(value, "%Y-%m-%d").date()


def fmt_display_date(d: date) -> str:
    return d.strftime("%b %d, %Y").replace(" 0", " ")


def escape_html(value: str) -> str:
    return (
        (value or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def load_posts() -> list[dict[str, Any]]:
    return json.loads(POSTS_PATH.read_text(encoding="utf-8"))


def save_posts(posts: list[dict[str, Any]]) -> None:
    POSTS_PATH.write_text(json.dumps(posts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ensure_unique_slug(posts: list[dict[str, Any]], base_slug: str) -> str:
    existing = {p.get("slug") for p in posts}
    if base_slug not in existing:
        return base_slug
    i = 2
    while f"{base_slug}-{i}" in existing:
        i += 1
    return f"{base_slug}-{i}"


def render_article_html(*, title: str, deck: str, audience: str, category: str, d: date, slug: str) -> str:
    canonical = f"https://asset-energy.ai/news/{slug}.html"
    display_date = fmt_display_date(d)

    # This is intentionally aligned with the existing article markup/styles (`styles.v2.css`).
    return f"""\
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta
      name="description"
      content="{escape_html(deck)}"
    />
    <meta name="theme-color" content="#0b1220" />
    <link rel="icon" href="../favicon.svg" type="image/svg+xml" />
    <link rel="canonical" href="{canonical}" />

    <meta property="og:type" content="article" />
    <meta property="og:site_name" content="Asset-Energy AI" />
    <meta property="og:title" content="{escape_html(title)} | Asset-Energy AI" />
    <meta
      property="og:description"
      content="{escape_html(deck)}"
    />
    <meta property="og:url" content="{canonical}" />

    <title>{escape_html(title)} | Asset-Energy AI</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="../styles.v2.css?v=news8" />
  </head>

  <body>
    <a class="skip-link" href="#main">Skip to content</a>

    <header class="site-header">
      <div class="container header-inner">
        <a class="brand" href="../" aria-label="Asset-Energy AI home">
          <img
            class="brand-logo"
            src="../asset-energy.ai.cropped.png"
            alt="asset-energy.ai"
            width="650"
            height="103"
          />
        </a>

        <nav class="nav" aria-label="Primary">
          <a href="../#product">Product</a>
          <a href="../#use-cases">Use cases</a>
          <a href="../news.html">News</a>
          <a href="../#contact" class="btn btn-secondary">Talk to us</a>
        </nav>

        <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="mobile-nav">
          <span class="sr-only">Open menu</span>
          <span aria-hidden="true" class="nav-toggle-icon"></span>
        </button>
      </div>

      <div id="mobile-nav" class="mobile-nav" hidden>
        <div class="container mobile-nav-inner">
          <a href="../#product">Product</a>
          <a href="../#use-cases">Use cases</a>
          <a href="../news.html">News</a>
          <a href="../#contact" class="btn btn-secondary">Talk to us</a>
        </div>
      </div>
    </header>

    <main id="main" class="news-page news-article-page">
      <article class="container article-full">
        <header class="article-full-head">
          <p class="news-meta"><a href="../news.html">News</a> · {display_date} · {escape_html(category)}</p>
          <p class="article-kicker">Insights · asset-energy.ai</p>
          <h1>{escape_html(title)}</h1>
          <p class="article-deck">
            {escape_html(deck)}
          </p>
          <p class="article-audience">
            {escape_html(audience)}
          </p>
        </header>

        <div class="article-full-body">
          <p class="article-lead">
            Replace this lead paragraph. One or two sentences that state the claim, why it matters now, and who should care.
          </p>

          <h2>Section heading</h2>
          <p>
            Add your argument. Keep paragraphs short for readability.
          </p>

          <h2>What happens next</h2>
          <p>
            End with implications and a concrete next step for the reader.
          </p>
        </div>

        <p class="fineprint" style="margin-top: 22px">
          <a href="../news.html">← Back to News</a>
        </p>
      </article>
    </main>

    <footer class="site-footer">
      <div class="container footer-inner">
        <div class="footer-brand">
          <img class="footer-logo" src="../asset-energy.ai.cropped.png" alt="asset-energy.ai" width="550" height="85" />
        </div>
        <div class="footer-links">
          <a href="../#product">Product</a>
          <a href="../#use-cases">Use cases</a>
          <a href="../news.html">News</a>
          <a href="../#contact">Contact</a>
        </div>
        <div class="footer-meta">
          <span>© <span id="year"></span> Asset-Energy AI</span>
        </div>
      </div>
    </footer>

    <script>
      const toggle = document.querySelector(".nav-toggle");
      const mobileNav = document.querySelector("#mobile-nav");
      const year = document.querySelector("#year");

      year.textContent = String(new Date().getFullYear());

      function setOpen(nextOpen) {{
        toggle.setAttribute("aria-expanded", String(nextOpen));
        mobileNav.hidden = !nextOpen;
        document.body.classList.toggle("no-scroll", nextOpen);
      }}

      toggle?.addEventListener("click", () => {{
        const isOpen = toggle.getAttribute("aria-expanded") === "true";
        setOpen(!isOpen);
      }});

      mobileNav?.addEventListener("click", (e) => {{
        const target = e.target;
        if (target instanceof HTMLAnchorElement) setOpen(false);
      }});

      window.addEventListener("keydown", (e) => {{
        if (e.key === "Escape") setOpen(false);
      }});
    </script>
  </body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a new OpEd and regenerate news.html")
    parser.add_argument("title", help="OpEd headline (used to create slug + page title)")
    parser.add_argument("--date", dest="date", default=None, help="YYYY-MM-DD (default: today)")
    parser.add_argument("--category", dest="category", default="Opinion", help="e.g. Opinion")
    parser.add_argument("--deck", dest="deck", default="Opinion from Asset-Energy AI.", help="Short 1-sentence description")
    parser.add_argument(
        "--audience",
        dest="audience",
        default="For energy and sustainability leaders.",
        help="Short audience line shown under the deck",
    )
    parser.add_argument(
        "--excerpt",
        dest="excerpt",
        default=None,
        help="Excerpt shown on news.html (defaults to deck).",
    )
    args = parser.parse_args()

    posts = load_posts()
    base_slug = slugify(args.title)
    slug = ensure_unique_slug(posts, base_slug)
    d = parse_date(args.date)

    target_path = NEWS_DIR / f"{slug}.html"
    if target_path.exists():
        raise SystemExit(f"Refusing to overwrite existing file: {target_path}")

    # Guardrail: prevent accidental placeholder posts from being committed.
    if base_slug.startswith("test-") or base_slug == "test":
        raise SystemExit("Refusing to create a post with a title that looks like a test. Pick a real headline.")

    html = render_article_html(
        title=args.title,
        deck=args.deck,
        audience=args.audience,
        category=args.category,
        d=d,
        slug=slug,
    )
    target_path.write_text(html, encoding="utf-8")

    excerpt = (args.excerpt or args.deck or "").strip()
    posts.append(
        {
            "slug": slug,
            "title": args.title,
            "date": d.strftime("%Y-%m-%d"),
            "category": args.category,
            "excerpt": excerpt,
            "canonicalPath": f"/news/{slug}.html",
        }
    )
    save_posts(posts)

    # Regenerate news.html
    import subprocess

    subprocess.check_call(["python3", str(BUILD_SCRIPT)])

    print(f"Created {target_path.relative_to(ROOT)}")
    print(f"Updated news/posts.json")
    print(f"Regenerated news.html")


if __name__ == "__main__":
    main()

