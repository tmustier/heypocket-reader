---
name: heypocket-reader
description: Read transcripts and summaries from Pocket AI (heypocket.com) recording devices. Use when users want to retrieve, search, or analyze their Pocket recordings, transcripts, summaries, or action items. Triggers on requests involving Pocket device data, conversation transcripts, meeting recordings, or audio note retrieval.
---

# heypocket-reader

Read transcripts and summaries from Pocket AI devices via reverse-engineered API.

## Quick Reference

| Function | Description |
|----------|-------------|
| `get_recordings(days, limit)` | List recent recordings |
| `get_recording_full(id)` | Get transcript + summary + action items |
| `get_transcript(id)` | Get raw transcript text |
| `get_summarization(id)` | Get markdown summary |
| `search_recordings(query)` | Search by text |

## Setup

1. Start Chrome with `--remote-debugging-port=9222` and your profile
2. Navigate to https://app.heypocket.com and log in
3. Extract token: `python3 scripts/reader.py extract`

Token saved to `~/.pocket_token.json`, expires in 1 hour.

## Usage

```python
from reader import get_recordings, get_recording_full, search_recordings

# List recordings
for r in get_recordings(days=30):
    print(f"{r.recorded_at:%Y-%m-%d} | {r.duration_str} | {r.title}")

# Get full data (transcript + summary)
full = get_recording_full(recording_id)
print(full['transcript'])   # Raw text (50k+ chars)
print(full['summary'])      # Markdown summary
print(full['action_items']) # List

# Search
results = search_recordings("meeting", days=90)
```

## Data Model

**PocketRecording**: `id`, `title`, `description`, `duration`, `duration_str`, `recorded_at`, `num_speakers`, `latitude`, `longitude`, `tags`

**get_recording_full()**: Returns dict with `recording`, `transcript`, `summary`, `action_items`, `speakers`
