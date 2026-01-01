#!/usr/bin/env python3
"""
Pocket (heypocket.com) API client.

Reads transcripts and summaries from Pocket AI devices via reverse-engineered API.
API Base: https://production.heypocketai.com/api/v1
Auth: Firebase Bearer token extracted from browser

Usage:
    # Extract token (requires Chrome with --profile, logged into app.heypocket.com)
    python3 reader.py extract
    
    # List recordings
    python3 reader.py [days]
"""

import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List
from pathlib import Path

API_BASE = "https://production.heypocketai.com/api/v1"
TOKEN_CACHE_FILE = Path.home() / ".pocket_token.json"


@dataclass
class PocketRecording:
    """A Pocket recording with metadata."""
    id: str
    title: str
    description: str
    duration: int
    recorded_at: datetime
    created_at: datetime
    has_transcription: bool
    has_summarization: bool
    transcription_status: str
    summarization_status: str
    num_speakers: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    tags: List[str] = None
    folder_id: Optional[str] = None
    
    @classmethod
    def from_api(cls, data: dict) -> 'PocketRecording':
        return cls(
            id=data['id'],
            title=data.get('title', 'Untitled'),
            description=data.get('description', ''),
            duration=data.get('duration', 0) or 0,
            recorded_at=_parse_datetime(data.get('recordingAt')),
            created_at=_parse_datetime(data.get('createdAt')),
            has_transcription=data.get('hasTranscription', False),
            has_summarization=data.get('hasSummarization', False),
            transcription_status=data.get('transcriptionStatus', 'unknown'),
            summarization_status=data.get('summarizationStatus', 'unknown'),
            num_speakers=int(data.get('numOfSpeakers', 0) or 0),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            tags=[t.get('name', '') for t in data.get('tags', [])],
            folder_id=data.get('folderId'),
        )
    
    @property
    def duration_str(self) -> str:
        if self.duration < 60:
            return f"{self.duration}s"
        elif self.duration < 3600:
            return f"{self.duration // 60}m"
        else:
            h = self.duration // 3600
            m = (self.duration % 3600) // 60
            return f"{h}h {m}m"


@dataclass
class PocketSummarization:
    """Summarization data for a recording."""
    id: str
    recording_id: str
    summary: str
    action_items: List[dict]
    transcript: Optional[str] = None
    created_at: Optional[datetime] = None


def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    if not dt_str:
        return None
    try:
        for fmt in ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ"]:
            try:
                return datetime.strptime(dt_str, fmt)
            except ValueError:
                continue
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except:
        return None


def get_token() -> Optional[str]:
    """Get Firebase token from cache file."""
    if TOKEN_CACHE_FILE.exists():
        try:
            data = json.loads(TOKEN_CACHE_FILE.read_text())
            if data.get('expires_at', 0) > datetime.now().timestamp():
                return data.get('access_token')
        except:
            pass
    return None


def save_token(access_token: str, refresh_token: str = None, expires_in: int = 3600):
    """Save token to cache file."""
    data = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_at': (datetime.now() + timedelta(seconds=expires_in)).timestamp()
    }
    TOKEN_CACHE_FILE.write_text(json.dumps(data))
    print(f"Token saved to {TOKEN_CACHE_FILE}")


def _api_request(endpoint: str, token: str, params: dict = None) -> dict:
    """Make authenticated API request."""
    import urllib.request
    import urllib.parse
    
    url = f"{API_BASE}{endpoint}"
    if params:
        url += '?' + urllib.parse.urlencode(params)
    
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        raise Exception(f"API error: {e}")


def get_recordings(days: int = 30, limit: int = 50, token: str = None) -> List[PocketRecording]:
    """Get recent recordings."""
    token = token or get_token()
    if not token:
        raise Exception("No token. Run: python3 reader.py extract")
    
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    params = {
        'limit': limit,
        'include_empty': 'false',
        'sort_by': 'recording_at',
        'sort_order': 'desc',
        'start_date': start_date,
    }
    
    data = _api_request('/recordings', token, params)
    recordings = [PocketRecording.from_api(r) for r in data.get('data', [])]
    return recordings[:limit]  # Enforce limit client-side (API may return more)


def get_recording_full(recording_id: str, token: str = None) -> dict:
    """Get recording with transcript, summary, and action items."""
    token = token or get_token()
    if not token:
        raise Exception("No token available.")
    
    data = _api_request(f'/recordings/{recording_id}', token, {'include': 'all'})
    
    recording = PocketRecording.from_api(data.get('recording', {}))
    
    transcription = data.get('transcription', {})
    transcript = transcription.get('transcription', {}).get('text', '') if transcription else ''
    
    summarizations = data.get('summarizations', {})
    summary = ''
    action_items = []
    if summarizations:
        first_key = next(iter(summarizations.keys()), None)
        if first_key:
            v2 = summarizations[first_key].get('v2', {})
            summary = v2.get('summary', {}).get('markdown', '')
            action_items = v2.get('actionItems', {}).get('items', [])
    
    return {
        'recording': recording,
        'transcript': transcript,
        'summary': summary,
        'action_items': action_items,
        'speakers': data.get('speakers', []),
    }


def get_transcript(recording_id: str, token: str = None) -> Optional[str]:
    """Get raw transcript text."""
    token = token or get_token()
    if not token:
        raise Exception("No token available.")
    
    data = _api_request(f'/recordings/{recording_id}', token, {'include': 'all'})
    transcription = data.get('transcription', {})
    if not transcription:
        return None
    return transcription.get('transcription', {}).get('text', None)


def get_summarization(recording_id: str, token: str = None) -> Optional[PocketSummarization]:
    """Get summary for a recording."""
    token = token or get_token()
    if not token:
        raise Exception("No token available.")
    
    data = _api_request(f'/recordings/{recording_id}', token, {'include': 'all'})
    
    summarizations = data.get('summarizations', {})
    if not summarizations:
        return None
    
    first_key = next(iter(summarizations.keys()), None)
    if not first_key:
        return None
    
    summ = summarizations[first_key]
    v2 = summ.get('v2', {})
    
    return PocketSummarization(
        id=summ.get('id', ''),
        recording_id=recording_id,
        summary=v2.get('summary', {}).get('markdown', ''),
        action_items=v2.get('actionItems', {}).get('items', []),
        transcript=None,
        created_at=None,
    )


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two lat/lon points."""
    from math import radians, sin, cos, sqrt, atan2
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))


def search_recordings(
    query: str = None,
    days: int = 90,
    limit: int = 20,
    lat: float = None,
    lon: float = None,
    radius_km: float = 1.0,
    token: str = None
) -> List[PocketRecording]:
    """
    Search recordings with client-side filtering.
    
    Filters on: title, description, tags. Location optional.
    
    For transcript search: use get_recording_full() per recording - expensive but possible.
    
    Args:
        query: Text to search in title/description/tags (optional if using location)
        days: How far back to search
        limit: Max results to return
        lat/lon: Filter by location (requires both)
        radius_km: Radius for location filter (default 1km)
    """
    token = token or get_token()
    if not token:
        raise Exception("No token available.")
    
    if not query and not (lat and lon):
        raise ValueError("Provide query and/or lat+lon")
    
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    params = {
        'limit': 100,
        'start_date': start_date,
        'sort_by': 'recording_at',
        'sort_order': 'desc',
    }
    
    data = _api_request('/recordings', token, params)
    all_recordings = [PocketRecording.from_api(r) for r in data.get('data', [])]
    
    query_lower = query.lower() if query else None
    matches = []
    
    for r in all_recordings:
        # Location filter
        if lat and lon:
            if not (r.latitude and r.longitude):
                continue
            if _haversine_km(lat, lon, r.latitude, r.longitude) > radius_km:
                continue
        
        # Text filter
        if query_lower:
            searchable = f"{r.title} {r.description} {' '.join(r.tags or [])}".lower()
            if query_lower not in searchable:
                continue
        
        matches.append(r)
        if len(matches) >= limit:
            break
    
    return matches


def extract_token_from_browser() -> Optional[str]:
    """
    Extract Firebase token using Playwright.
    
    Opens browser to app.heypocket.com, waits for login if needed,
    then extracts token from IndexedDB.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed. Run: python3 -m pip install playwright && python3 -m playwright install chromium")
        return None
    
    import time
    
    js_code = '''() => {
        return new Promise((resolve) => {
            const idbRequest = indexedDB.open("firebaseLocalStorageDb");
            idbRequest.onsuccess = () => {
                const db = idbRequest.result;
                const tx = db.transaction("firebaseLocalStorage", "readonly");
                const store = tx.objectStore("firebaseLocalStorage");
                const getAll = store.getAll();
                getAll.onsuccess = () => {
                    for (const item of getAll.result) {
                        if (item?.value?.stsTokenManager?.accessToken) {
                            const tm = item.value.stsTokenManager;
                            resolve({
                                accessToken: tm.accessToken,
                                refreshToken: tm.refreshToken,
                                expirationTime: tm.expirationTime
                            });
                            return;
                        }
                    }
                    resolve({error: "No token found in IndexedDB"});
                };
                getAll.onerror = () => resolve({error: "Failed to read IndexedDB"});
            };
            idbRequest.onerror = () => resolve({error: "Failed to open IndexedDB"});
        });
    }'''
    
    # Use persistent profile so login is remembered
    profile_dir = Path.home() / '.pocket_browser_profile'
    
    print("Launching browser...")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            str(profile_dir),
            headless=False,
            viewport={'width': 1280, 'height': 800}
        )
        page = context.pages[0] if context.pages else context.new_page()
        
        print("Navigating to app.heypocket.com...")
        page.goto("https://app.heypocket.com", wait_until="networkidle")
        
        # Check if we need to login - poll instead of wait_for_function
        if "/login" in page.url.lower() or "/sign" in page.url.lower():
            print("\n⚠️  Please log in to Pocket in the browser window.")
            print("   Waiting for login to complete (up to 5 minutes)...")
            for _ in range(60):  # 5 minutes, checking every 5 seconds
                time.sleep(5)
                current_url = page.url
                if "/login" not in current_url and "/sign" not in current_url:
                    print("   Login detected! Extracting token...")
                    time.sleep(3)  # Let IndexedDB populate
                    break
            else:
                print("   Timeout waiting for login.")
                context.close()
                return None
        
        # Extract token from IndexedDB
        data = page.evaluate(js_code)
        context.close()
        
        if 'accessToken' in data:
            save_token(data['accessToken'], data.get('refreshToken'), expires_in=3600)
            return data['accessToken']
        else:
            print(f"Token extraction failed: {data.get('error', 'unknown error')}")
            return None


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'extract':
        print("Extracting token from browser...")
        print("(Browser will open - log in if prompted)")
        print()
        token = extract_token_from_browser()
        if token:
            print(f"Success! Token saved (first 50 chars: {token[:50]}...)")
        else:
            print("Failed to extract token.")
            sys.exit(1)
        sys.exit(0)
    
    if len(sys.argv) > 1 and sys.argv[1] == 'set-token':
        if len(sys.argv) < 3:
            print("Usage: python3 reader.py set-token <TOKEN>")
            print()
            print("To get the token:")
            print("  1. Open https://app.heypocket.com in Chrome")
            print("  2. Open DevTools (Cmd+Option+I)")
            print("  3. Go to Network tab, refresh the page")
            print("  4. Click any request to production.heypocketai.com")
            print("  5. Copy the Bearer token from Authorization header")
            sys.exit(1)
        token = sys.argv[2]
        save_token(token, expires_in=3600)
        print(f"Token saved! (first 50 chars: {token[:50]}...)")
        sys.exit(0)
    
    token = get_token()
    if not token:
        print("No token. Run: python3 reader.py set-token <TOKEN>")
        print("  or: python3 reader.py extract (requires browser skill)")
        sys.exit(1)
    
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    
    print(f"=== Pocket Recordings (last {days} days) ===\n")
    recordings = get_recordings(days=days, limit=20, token=token)
    
    for r in recordings:
        date = r.recorded_at.strftime('%Y-%m-%d') if r.recorded_at else '?'
        status = '✓' if r.has_summarization else '○'
        speakers = f"({r.num_speakers}sp)" if r.num_speakers else ""
        print(f"  {date} | {r.duration_str:>6} | {status} {r.title[:45]} {speakers}")
