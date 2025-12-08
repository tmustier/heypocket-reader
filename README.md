# heypocket-reader

A Claude Code skill for reading transcripts and summaries from [Pocket AI](https://heypocket.com) recording devices.

## What is Pocket?

Pocket is an AI-powered wearable device that records conversations and generates transcripts, summaries, and action items. This skill provides programmatic access to your Pocket data via their unofficial API.

## Features

- **List recordings** with metadata (title, duration, date, speakers)
- **Get full transcripts** of recorded conversations (50k+ characters)
- **Get AI summaries** in markdown format
- **Extract action items** from recordings
- **Search recordings** by text

## Installation

### For Claude Code Users

Download the `.skill` file from [Releases](../../releases) and add it to your Claude Code skills.

### Manual Installation

```bash
git clone https://github.com/tmustier/heypocket-reader.git ~/.claude/skills/heypocket-reader
```

## Setup

### Prerequisites

1. A Pocket account with recordings
2. Chrome browser
3. A way to start Chrome with remote debugging (see examples below)

### Step 1: Start Chrome with Remote Debugging

Choose one of these methods:

**Manual (macOS):**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/chrome-debug-profile"
```

**Manual (Linux):**
```bash
google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/chrome-debug-profile"
```

**Using Puppeteer:**
```bash
npx puppeteer browsers install chrome
node -e "require('puppeteer').launch({headless: false, args: ['--remote-debugging-port=9222']})"
```

**Using Playwright:**
```bash
npx playwright install chromium
npx playwright open --remote-debugging-port=9222 https://app.heypocket.com
```

### Step 2: Log into Pocket

Navigate to https://app.heypocket.com in the Chrome window and log in with your account.

### Step 3: Extract Token

```bash
python3 ~/.claude/skills/heypocket-reader/scripts/reader.py extract
```

The token is saved to `~/.pocket_token.json` and expires in 1 hour. Re-run the extract command when it expires.

## Usage

### CLI

```bash
# List recent recordings
python3 scripts/reader.py

# List recordings from last 7 days
python3 scripts/reader.py 7
```

### Python

```python
from reader import get_recordings, get_recording_full, search_recordings

# List recordings
recordings = get_recordings(days=30, limit=20)
for r in recordings:
    print(f"{r.recorded_at:%Y-%m-%d} | {r.duration_str} | {r.title}")

# Get full transcript and summary
full = get_recording_full(recording_id)
print(full['transcript'])   # Raw text (50k+ chars)
print(full['summary'])      # Markdown summary
print(full['action_items']) # List of action items

# Search
results = search_recordings("meeting")
```

## API Reference

| Function | Description |
|----------|-------------|
| `get_recordings(days, limit)` | List recent recordings |
| `get_recording_full(id)` | Get transcript + summary + action items + speakers |
| `get_transcript(id)` | Get raw transcript text |
| `get_summarization(id)` | Get markdown summary |
| `search_recordings(query, days, limit)` | Search recordings by text |

## Technical Details

- **API Base**: `https://production.heypocketai.com/api/v1`
- **Auth**: Firebase Bearer token from browser IndexedDB
- **Token Expiry**: 1 hour (Firebase default)
- **Key Parameter**: `?include=all` to get transcript and summary

This skill was created by reverse-engineering the Pocket web app at `app.heypocket.com`.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Disclaimer

This is an unofficial integration. Use at your own risk. Not affiliated with or endorsed by Pocket/Open Vision Engineering Inc.
