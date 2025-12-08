# heypocket-reader

Access transcripts and summaries from [Pocket AI](https://heypocket.com) recording devices.

## Features

- **List recordings** with metadata (title, duration, date, location, speakers)
- **Get full transcripts** (50k+ characters)
- **Get AI summaries** in markdown format
- **Extract action items** and **speaker profiles**
- **Search recordings** by title/description/tags and/or location

## Installation

Download the `.skill` file from [Releases](../../releases) or:

```bash
git clone https://github.com/tmustier/heypocket-reader.git ~/.claude/skills/heypocket-reader
```

## Setup

### 1. Start Chrome with Remote Debugging

**macOS:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/chrome-debug-profile"
```

**Linux:**
```bash
google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/chrome-debug-profile"
```

**Puppeteer:**
```bash
npx puppeteer browsers install chrome
node -e "require('puppeteer').launch({headless: false, args: ['--remote-debugging-port=9222']})"
```

**Playwright:**
```bash
npx playwright install chromium
npx playwright open --remote-debugging-port=9222 https://app.heypocket.com
```

### 2. Log into Pocket

Navigate to https://app.heypocket.com and log in.

### 3. Extract Token

```bash
python3 scripts/reader.py extract
```

Token saved to `~/.pocket_token.json`. Expires in 1 hour.

## Usage

```python
from reader import get_recordings, get_recording_full, search_recordings

# List recordings
for r in get_recordings(days=30):
    print(f"{r.recorded_at:%Y-%m-%d} | {r.title}")

# Get full data
full = get_recording_full(recording_id)
full['transcript']    # Raw text
full['summary']       # Markdown
full['action_items']  # List
full['speakers']      # Dict with speaker profiles (names, IDs)

# Search by title/description/tags
search_recordings(query="meeting")

# Search by location
search_recordings(lat=51.51, lon=-0.13, radius_km=5)

# Combined
search_recordings(query="AI", lat=51.51, lon=-0.13, radius_km=50)
```

## API Reference

| Function | Description |
|----------|-------------|
| `get_recordings(days, limit)` | List recent recordings |
| `get_recording_full(id)` | Get transcript + summary + action items + speakers |
| `search_recordings(query, lat, lon, radius_km)` | Search by title/description/tags and/or location |

## Transcript Search

Full-text transcript search requires fetching each recording (1 API call each). Not built-in, but easy to implement:

```python
for r in get_recordings(days=30):
    full = get_recording_full(r.id)
    if "search term" in full['transcript'].lower():
        print(f"Found in: {r.title}")
```

## Technical Details

- **API Base**: `https://production.heypocketai.com/api/v1`
- **Auth**: Firebase Bearer token from browser IndexedDB
- **Token Expiry**: 1 hour

## License

MIT License

## Disclaimer

Unofficial integration. Not affiliated with Pocket/Open Vision Engineering Inc.
