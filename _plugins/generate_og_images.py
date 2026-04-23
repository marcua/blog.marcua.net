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

# Blog design system colors
BG_COLOR = "#111113"
TITLE_COLOR = "#eeeeef"
SUBTITLE_COLOR = "#d1d1d6"
BODY_COLOR = "#d1d1d6"
ACCENT_COLOR = "#8b8ef5"
MUTED_COLOR = "#8e8e93"

# Sentinel that brackets link text through extraction, wrapping, and drawing,
# so the body draw loop can re-color those runs in ACCENT_COLOR. Using a
# control char (U+0001) so it can't collide with real post content.
LINK_MARKER = "\x01"

def _find_font(candidates):
    """Return the first font path that exists, or fall back to Pillow default."""
    for path in candidates:
        if Path(path).exists():
            return path
    return None  # will use Pillow's built-in default


FONT_BOLD = _find_font([
    # macOS
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial Bold.ttf",
    # Linux (DejaVu)
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
])

FONT_REGULAR = _find_font([
    # macOS
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial.ttf",
    # Linux (DejaVu)
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
])


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
    # Drop markdown table rows entirely (header, separator, body). Tables in
    # this blog are mostly image-with-caption layouts and have no useful plain
    # text representation in an OG preview.
    body = re.sub(r"^[ \t]*\|.*$", "", body, flags=re.MULTILINE)
    # Remove markdown headings
    body = re.sub(r"^#{1,6}\s+.*$", "", body, flags=re.MULTILINE)
    # Wrap link text in sentinel markers (drawn later in ACCENT_COLOR) and
    # drop the URL.
    body = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        lambda m: f"{LINK_MARKER}{m.group(1)}{LINK_MARKER}",
        body,
    )
    # Strip Kramdown inline attribute lists: {:target="_blank"}, {:.class}, etc.
    # Run this after link handling so orphaned IALs left behind by
    # `[text](url){:foo}` get cleaned up.
    body = re.sub(r"\{:[^}]*\}", "", body)
    # Remove bold/italic markers
    body = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", body)
    # Remove images
    body = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", body)
    # Remove HTML tags
    body = re.sub(r"<[^>]+>", "", body)
    # Turn bullet lines into separate paragraphs by adding a blank line before each
    body = re.sub(r"\n([ \t]*[\*\-]\s+)", r"\n\n\1", body)
    # Remove bullet markers themselves (only horizontal whitespace before marker)
    body = re.sub(r"^[ \t]*[\*\-]\s+", "", body, flags=re.MULTILINE)

    # Split into paragraphs and take non-empty ones
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    result = []
    total = 0
    for p in paragraphs:
        # Collapse internal whitespace
        p = " ".join(p.split())
        # Count visible chars only — link markers shouldn't eat the budget.
        visible_len = len(p.replace(LINK_MARKER, ""))
        if total + visible_len > max_chars:
            if not result:
                result.append(p[:max_chars] + "...")
            break
        result.append(p)
        total += visible_len

    return "\n\n".join(result)


def slug_from_filename(filepath):
    """Get the URL slug from a post filename."""
    name = filepath.stem
    # Remove date prefix (YYYY-MM-DD-)
    return re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name)


def wrap_text(draw, text, font, max_width):
    """Word-wrap text to fit within max_width pixels.

    Link markers are preserved in the returned lines but stripped when
    measuring widths so they don't perturb wrapping.
    """
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox(
            (0, 0), test_line.replace(LINK_MARKER, ""), font=font
        )
        if bbox[2] > max_width and current_line:
            lines.append(" ".join(current_line))
            current_line = [word]
        else:
            current_line.append(word)
    if current_line:
        lines.append(" ".join(current_line))
    return lines


def normalize_link_markers(lines):
    """Re-balance link markers across line breaks within a paragraph.

    If a link wraps across lines, the closing marker lives on a later line
    than the opening marker. This rewrites each line so it independently
    opens and closes its link runs based on the running state.
    """
    result = []
    in_link = False
    for line in lines:
        new_line = LINK_MARKER if in_link else ""
        for ch in line:
            new_line += ch
            if ch == LINK_MARKER:
                in_link = not in_link
        if in_link:
            new_line += LINK_MARKER
        result.append(new_line)
    return result


def draw_styled_line(draw, line, x, y, font, body_color, link_color):
    """Draw a single line, alternating colors at link-marker boundaries."""
    in_link = False
    for run in line.split(LINK_MARKER):
        if run:
            color = link_color if in_link else body_color
            draw.text((x, y), run, font=font, fill=color)
            x += draw.textbbox((0, 0), run, font=font)[2]
        in_link = not in_link


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

    # Load fonts (fall back to Pillow default if no system font found)
    def _load(path, size):
        if path:
            return ImageFont.truetype(path, size)
        return ImageFont.load_default(size=size)

    font_title = _load(FONT_BOLD, 36)
    font_subtitle = _load(FONT_REGULAR, 22)
    font_body = _load(FONT_REGULAR, 18)
    font_meta = _load(FONT_REGULAR, 16)
    font_site = _load(FONT_BOLD, 16)

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
        lines = normalize_link_markers(
            wrap_text(draw, para, font_body, max_text_width)
        )
        for line in lines:
            if y + 24 > max_body_y:
                # Add ellipsis if we run out of room
                draw.text((margin_x, y), "...", font=font_body, fill=BODY_COLOR)
                y = max_body_y
                break
            draw_styled_line(
                draw, line, margin_x, y, font_body, BODY_COLOR, ACCENT_COLOR
            )
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
