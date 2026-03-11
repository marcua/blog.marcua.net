#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pillow",
#     "pyyaml",
# ]
# ///
"""Generate Open Graph preview images for blog posts.

Each image includes the post title, subtitle, date, and first few
paragraphs of body text, styled to match the blog's dark theme.
"""

import re
from datetime import datetime
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

# --- Configuration ---
POSTS_DIR = Path("_posts")
OUTPUT_DIR = Path("assets/images/og")
WIDTH = 1200
HEIGHT = 630

# Minima dark theme colors
BG_COLOR = "#1e1e1e"
TITLE_COLOR = "#e8e8e8"
SUBTITLE_COLOR = "#c8c8c8"
BODY_COLOR = "#b0b0b0"
ACCENT_COLOR = "#7eb8da"
MUTED_COLOR = "#808080"

# Fonts (DejaVu Sans is available on most Linux systems)
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def parse_post(filepath):
    """Parse a Jekyll post's frontmatter and body text."""
    text = filepath.read_text(encoding="utf-8")
    # Split frontmatter from body
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    frontmatter = yaml.safe_load(parts[1])
    body = parts[2].strip()
    return frontmatter, body


def extract_paragraphs(body, max_chars=500):
    """Extract the first few paragraphs of plain text from markdown body."""
    # Remove markdown headings
    body = re.sub(r"^#{1,6}\s+.*$", "", body, flags=re.MULTILINE)
    # Remove markdown links, keep link text
    body = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    # Remove bold/italic markers
    body = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", body)
    # Remove images
    body = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", body)
    # Remove HTML tags
    body = re.sub(r"<[^>]+>", "", body)
    # Remove bullet markers
    body = re.sub(r"^\s*[\*\-]\s+", "", body, flags=re.MULTILINE)

    # Split into paragraphs and take non-empty ones
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    result = []
    total = 0
    for p in paragraphs:
        # Collapse internal whitespace
        p = " ".join(p.split())
        if total + len(p) > max_chars:
            # Take a partial paragraph if we haven't added anything yet
            if not result:
                result.append(p[:max_chars] + "...")
            break
        result.append(p)
        total += len(p)

    return "\n\n".join(result)


def slug_from_filename(filepath):
    """Get the URL slug from a post filename."""
    name = filepath.stem
    # Remove date prefix (YYYY-MM-DD-)
    return re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name)


def wrap_text(draw, text, font, max_width):
    """Word-wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] > max_width and current_line:
            lines.append(" ".join(current_line))
            current_line = [word]
        else:
            current_line.append(word)
    if current_line:
        lines.append(" ".join(current_line))
    return lines


def generate_og_image(frontmatter, body, output_path):
    """Generate an OG image for a single post."""
    title = frontmatter.get("title", "Untitled")
    subtitle = frontmatter.get("subtitle", "")
    date = frontmatter.get("date", "")
    if isinstance(date, datetime):
        date_str = date.strftime("%B %-d, %Y")
    elif date:
        date_s = str(date).strip()
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
            try:
                date_str = datetime.strptime(date_s, fmt).strftime("%B %-d, %Y")
                break
            except ValueError:
                continue
        else:
            date_str = date_s
    else:
        date_str = ""

    body_text = extract_paragraphs(body, max_chars=1500)

    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Load fonts
    font_title = ImageFont.truetype(FONT_BOLD, 36)
    font_subtitle = ImageFont.truetype(FONT_REGULAR, 22)
    font_body = ImageFont.truetype(FONT_REGULAR, 18)
    font_meta = ImageFont.truetype(FONT_REGULAR, 16)
    font_site = ImageFont.truetype(FONT_BOLD, 16)

    margin_x = 60
    max_text_width = WIDTH - 2 * margin_x
    y = 50

    # Site name
    draw.text((margin_x, y), "N=1 (marcua's blog)", font=font_site, fill=ACCENT_COLOR)
    y += 35

    # Thin accent line
    draw.line([(margin_x, y), (margin_x + 80, y)], fill=ACCENT_COLOR, width=2)
    y += 20

    # Title (word-wrapped)
    title_lines = wrap_text(draw, title, font_title, max_text_width)
    for line in title_lines:
        draw.text((margin_x, y), line, font=font_title, fill=TITLE_COLOR)
        y += 46
    y += 4

    # Subtitle
    if subtitle:
        sub_lines = wrap_text(draw, subtitle, font_subtitle, max_text_width)
        for line in sub_lines:
            draw.text((margin_x, y), line, font=font_subtitle, fill=SUBTITLE_COLOR)
            y += 30
        y += 8

    # Date
    if date_str:
        draw.text((margin_x, y), date_str, font=font_meta, fill=MUTED_COLOR)
        y += 30

    # Separator line
    y += 5
    draw.line([(margin_x, y), (WIDTH - margin_x, y)], fill="#333333", width=1)
    y += 15

    # Body text
    max_body_y = HEIGHT - 50  # leave some bottom margin
    paragraphs = body_text.split("\n\n")
    for para in paragraphs:
        lines = wrap_text(draw, para, font_body, max_text_width)
        for line in lines:
            if y + 24 > max_body_y:
                # Add ellipsis if we run out of room
                draw.text((margin_x, y), "...", font=font_body, fill=BODY_COLOR)
                y = max_body_y
                break
            draw.text((margin_x, y), line, font=font_body, fill=BODY_COLOR)
            y += 24
        if y >= max_body_y:
            break
        y += 10  # paragraph spacing

    # Bottom bar with domain
    bar_y = HEIGHT - 40
    draw.text((margin_x, bar_y), "blog.marcua.net", font=font_meta, fill=MUTED_COLOR)

    img.save(output_path, "PNG", optimize=True)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    posts = sorted(POSTS_DIR.glob("*.md"))
    print(f"Found {len(posts)} posts")

    for post_path in posts:
        result = parse_post(post_path)
        if result is None:
            print(f"  Skipping {post_path.name} (no frontmatter)")
            continue

        frontmatter, body = result
        slug = slug_from_filename(post_path)
        output_path = OUTPUT_DIR / f"{slug}.png"

        generate_og_image(frontmatter, body, output_path)
        print(f"  Generated {output_path}")

    print("Done!")


if __name__ == "__main__":
    main()
