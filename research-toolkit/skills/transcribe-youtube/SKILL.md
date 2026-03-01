---
name: transcribe-youtube
description: Transcribe YouTube videos using yt-dlp — no API keys or credits needed. Extracts auto-generated captions from any YouTube video and returns clean plaintext. Use when you need the transcript or captions from a YouTube video.
argument-hint: <YouTube URL or video ID>
user-invocable: true
allowed-tools: Bash, Read
---

# Transcribe YouTube

Extract transcripts from YouTube videos using [yt-dlp](https://github.com/yt-dlp/yt-dlp). No API keys, no credits, no accounts — just `yt-dlp` installed locally.

## Setup

Requires `yt-dlp` to be installed and available in PATH.

```bash
# Check if yt-dlp is installed
which yt-dlp
```

If not installed, help the user install it:

```bash
# macOS (Homebrew)
brew install yt-dlp

# pip
pip install yt-dlp

# pipx
pipx install yt-dlp
```

## Usage

Run the transcription script with a YouTube URL or video ID:

```bash
python ./scripts/transcribe.py "$ARGUMENTS"
```

The script will:
1. Download auto-generated English captions (VTT format) via yt-dlp
2. Clean the VTT markup into plain text (strips timestamps, deduplicates overlapping lines)
3. Print the transcript to stdout as JSON with video metadata

### Output Format

```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "channel": "Channel Name",
  "duration": 212,
  "transcript": "Full plaintext transcript..."
}
```

If captions are not available, the output will include an `"error"` field instead of `"transcript"`.

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--max-words N` | Truncate transcript to N words | unlimited |
| `--lang LANG` | Subtitle language code | `en` |

### Examples

```bash
# Transcribe by URL
python ./scripts/transcribe.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Transcribe by video ID
python ./scripts/transcribe.py dQw4w9WgXcQ

# Limit transcript length
python ./scripts/transcribe.py --max-words 500 "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Get Spanish captions
python ./scripts/transcribe.py --lang es "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Errors

| Condition | Behavior |
|-----------|----------|
| yt-dlp not installed | Exits with error message and install instructions |
| No captions available | Returns JSON with `"error": "No captions found"` |
| Invalid URL/ID | Returns JSON with `"error"` describing the issue |
| Network timeout | 30-second timeout per video; returns error on timeout |

## Typical Workflow

**Research workflow:** User provides a video URL, get the transcript, then analyze or summarize the content.

```bash
# 1. Get transcript
python ./scripts/transcribe.py "https://www.youtube.com/watch?v=VIDEO_ID"

# 2. Read and analyze the output
```
