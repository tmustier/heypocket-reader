---
name: heypocket-reader
description: Read transcripts and summaries from Pocket AI (heypocket.com) recording devices. Use when users want to retrieve, search, or analyze their Pocket recordings, transcripts, summaries, or action items.
---

# heypocket-reader

Access Pocket AI recordings via reverse-engineered API.

## Quick Reference

| Function | Description |
|----------|-------------|
| `get_recordings(days, limit)` | List recent recordings |
| `get_recording_full(id)` | Get transcript + summary + action items + speakers |
| `search_recordings(query, lat, lon, radius_km, days=90)` | Search by title/description/tags and/or location |

## Setup

### Automated (recommended)
```bash
python3 scripts/reader.py extract
```
Opens browser, waits for login if needed, extracts token automatically.
Requires: `pip install playwright && playwright install chromium`

### Manual
1. Open https://app.heypocket.com in Chrome and log in
2. Open DevTools (Cmd+Option+I) → Network tab
3. Refresh page, click any request to `production.heypocketai.com`
4. Copy Bearer token from Authorization header
5. Run: `python3 scripts/reader.py set-token <TOKEN>`

Token expires in ~1 hour. Re-run when needed.

## Usage

```python
from reader import get_recordings, get_recording_full, search_recordings

# List recordings
for r in get_recordings(days=30):
    print(f"{r.recorded_at:%Y-%m-%d} | {r.title}")

# Get full data
full = get_recording_full(recording_id)
full['transcript']    # Raw text (50k+ chars)
full['summary']       # Markdown
full['action_items']  # List
full['speakers']      # Dict with speaker profiles

# Search by title/description/tags
search_recordings(query="meeting")

# Search by location
search_recordings(lat=51.51, lon=-0.13, radius_km=25)

# Combined
search_recordings(query="AI", lat=51.51, lon=-0.13, radius_km=25)
```

## Transcript Search

Not built-in (expensive: 1 API call per recording). To implement:

```python
for r in get_recordings(days=30):
    full = get_recording_full(r.id)
    if "search term" in full['transcript'].lower():
        print(f"Found in: {r.title}")
```

## Data

**PocketRecording**: `id`, `title`, `description`, `duration`, `duration_str`, `recorded_at`, `num_speakers`, `latitude`, `longitude`, `tags`

**get_recording_full()**: Returns `recording`, `transcript`, `summary`, `action_items`, `speakers`
