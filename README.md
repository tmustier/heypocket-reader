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
2. Browser automation capability (Chrome DevTools Protocol)
3. Chrome browser

### Authentication

Pocket uses Firebase authentication. To extract your token:

1. Start Chrome with remote debugging enabled (port 9222) and your user profile
2. Navigate to https://app.heypocket.com and log in
3. Run the token extraction:
   ```bash
   python3 ~/.claude/skills/heypocket-reader/scripts/reader.py extract
   ```

The token is saved to `~/.pocket_token.json` and expires in 1 hour.

#### Browser Automation Note

The `extract` command requires a browser automation tool that can evaluate JavaScript in Chrome via CDP (Chrome DevTools Protocol). If you have a browser skill installed, use it to:
1. Start Chrome with `--remote-debugging-port=9222` and your profile
2. Navigate to app.heypocket.com
3. Then run the extract command

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
print(full['transcript'])  # Raw text
print(full['summary'])     # Markdown

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

This skill was created by reverse-engineering the Pocket web app at `app.heypocket.com`.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Disclaimer

This is an unofficial integration. Use at your own risk. Not affiliated with or endorsed by Pocket/Open Vision Engineering Inc.
