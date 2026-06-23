"""Generate thumbnail images from the first frame of each video in assets/video/.

Outputs to assets/images/video-thumbs/{dir}/{name}.png alongside the source
videos.  Skips any video that already has a thumbnail.  Requires ffmpeg.

Run standalone:  uv run _plugins/generate_video_thumbs.py
Called by:        _plugins/video_thumbs.rb (Jekyll hook, same as OG images)
"""

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VIDEO_DIR = REPO_ROOT / "assets" / "video"
THUMB_DIR = REPO_ROOT / "assets" / "images" / "video-thumbs"
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}


def get_duration(video_path):
    """Get video duration in seconds via ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return float(result.stdout.strip())


def generate_thumbnail(video_path, thumb_path):
    thumb_path.parent.mkdir(parents=True, exist_ok=True)
    duration = get_duration(video_path)
    seek_args = ["-ss", str(duration / 2)] if duration else []
    result = subprocess.run(
        [
            "ffmpeg", "-y",
            *seek_args,
            "-i", str(video_path),
            "-frames:v", "1",
            "-f", "image2",
            str(thumb_path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  WARN: ffmpeg failed for {video_path}: {result.stderr.strip()}")
        return False
    return True


def main():
    if not VIDEO_DIR.exists():
        print("No assets/video/ directory found.")
        return

    videos = [
        p for p in VIDEO_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS
    ]
    if not videos:
        print("No video files found.")
        return

    generated = 0
    skipped = 0
    for video in sorted(videos):
        rel = video.relative_to(VIDEO_DIR)
        thumb = THUMB_DIR / rel.with_suffix(".png")
        if thumb.exists():
            skipped += 1
            continue
        print(f"  Generating thumbnail: {thumb.relative_to(REPO_ROOT)}")
        if generate_thumbnail(video, thumb):
            generated += 1

    print(f"Video thumbs: {generated} generated, {skipped} already existed.")


if __name__ == "__main__":
    main()
