#!/usr/bin/env python3
"""Transcribe YouTube videos using yt-dlp.

Extracts auto-generated captions and returns clean plaintext transcripts.
No API keys needed — just yt-dlp installed locally.
"""

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path


def clean_vtt(vtt_text: str) -> str:
    """Convert VTT subtitle format to clean plaintext."""
    # Strip VTT header
    text = re.sub(r"^WEBVTT.*?\n\n", "", vtt_text, flags=re.DOTALL)
    # Strip timestamps
    text = re.sub(
        r"\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}.*\n", "", text
    )
    # Strip HTML-like tags (positioning, alignment)
    text = re.sub(r"<[^>]+>", "", text)
    # Strip cue numbers
    text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)
    # Deduplicate overlapping lines (yt auto-subs repeat lines across cues)
    lines = text.strip().split("\n")
    seen = set()
    unique = []
    for line in lines:
        stripped = line.strip()
        if stripped and stripped not in seen:
            seen.add(stripped)
            unique.append(stripped)
    return re.sub(r"\s+", " ", " ".join(unique)).strip()


def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from a YouTube URL or return as-is if already an ID."""
    # Already a bare video ID (11 chars, alphanumeric + - _)
    if re.match(r"^[\w-]{11}$", url_or_id):
        return url_or_id
    # Standard and short URLs
    patterns = [
        r"(?:youtube\.com/watch\?.*v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)([\w-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return url_or_id  # Return as-is; let yt-dlp handle validation


def get_video_metadata(video_id: str) -> dict:
    """Fetch video metadata via yt-dlp --dump-json."""
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--no-warnings",
        "--no-download",
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout.strip().split("\n")[0])
            return {
                "title": data.get("title", ""),
                "channel": data.get("channel", data.get("uploader", "")),
                "duration": data.get("duration"),
            }
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return {}


def fetch_transcript(video_id: str, lang: str = "en") -> str | None:
    """Fetch auto-generated transcript for a YouTube video.

    Returns plaintext transcript string, or None if no captions available.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        cmd = [
            "yt-dlp",
            "--write-auto-subs",
            "--sub-lang", lang,
            "--sub-format", "vtt",
            "--skip-download",
            "--no-warnings",
            "-o", f"{temp_dir}/%(id)s",
            f"https://www.youtube.com/watch?v={video_id}",
        ]

        preexec = os.setsid if hasattr(os, "setsid") else None

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=preexec,
            )
            try:
                proc.communicate(timeout=30)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                except (ProcessLookupError, PermissionError, OSError):
                    proc.kill()
                proc.wait(timeout=5)
                return None
        except FileNotFoundError:
            return None

        # yt-dlp may save as .en.vtt or .en-orig.vtt
        vtt_path = Path(temp_dir) / f"{video_id}.{lang}.vtt"
        if not vtt_path.exists():
            for p in Path(temp_dir).glob(f"{video_id}*.vtt"):
                vtt_path = p
                break
            else:
                return None

        try:
            raw = vtt_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None

        transcript = clean_vtt(raw)
        return transcript if transcript else None


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe YouTube videos using yt-dlp"
    )
    parser.add_argument(
        "url", help="YouTube video URL or video ID"
    )
    parser.add_argument(
        "--max-words", type=int, default=0,
        help="Truncate transcript to N words (0 = unlimited)"
    )
    parser.add_argument(
        "--lang", default="en",
        help="Subtitle language code (default: en)"
    )
    args = parser.parse_args()

    # Check yt-dlp is installed
    if not shutil.which("yt-dlp"):
        print(json.dumps({
            "error": "yt-dlp is not installed. Install with: brew install yt-dlp / pip install yt-dlp"
        }))
        sys.exit(1)

    video_id = extract_video_id(args.url)

    # Fetch metadata and transcript
    metadata = get_video_metadata(video_id)
    transcript = fetch_transcript(video_id, lang=args.lang)

    result = {
        "video_id": video_id,
        "title": metadata.get("title", ""),
        "channel": metadata.get("channel", ""),
        "duration": metadata.get("duration"),
    }

    if transcript:
        if args.max_words > 0:
            words = transcript.split()
            if len(words) > args.max_words:
                transcript = " ".join(words[: args.max_words]) + "..."
        result["transcript"] = transcript
    else:
        result["error"] = "No captions found for this video"

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
