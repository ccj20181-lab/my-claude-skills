---
name: yt-dlp
description: Video downloader for 1000+ websites including Bilibili, Xiaohongshu, Vimeo, Twitter, TikTok. Successfully tested with Bilibili and Xiaohongshu. YouTube videos may require manual authentication due to 2025 anti-bot restrictions. Supports quality selection, audio extraction, subtitles, and playlists. Automatically downloads to ~/Downloads/videos/. Use when user asks to download videos, extract audio, or save media from URLs.
---

# yt-dlp Video Downloader

## Overview

Download videos from 1000+ websites using yt-dlp. Supports quality selection, audio extraction, subtitle downloads, and format conversion.

## Quick Start

### Basic Download

```
Download this video: https://www.youtube.com/watch?v=xxxxx
```

Process:
1. Get video info (title, duration, quality options)
2. Download to `~/Downloads/videos/`
3. Display progress and confirm completion

### Download with Options

**Specify quality:**
```
Download 1080p: https://youtube.com/watch?v=xxxxx
```

**Audio only:**
```
Download audio only: https://youtu.be/xxxxx
```

**Custom output:**
```
Save to desktop: https://bilibili.com/video/BVxxxxx
```

**With subtitles:**
```
Download with subtitles: https://youtube.com/watch?v=xxxxx
```

## Supported Sites

Common platforms:
- **Video**: YouTube, Bilibili, Vimeo, Dailymotion
- **Social**: Twitter, Facebook, Instagram, TikTok
- **Music**: SoundCloud, Spotify, Bandcamp
- **Chinese**: 抖音, 快手, 微视, B站

Full list: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

## Download Workflow

### Step 1: Get Video Info

Use the script to fetch video metadata:

```python
python3 scripts/download.py "URL" --info
```

Returns: title, duration, uploader, view count, thumbnail

### Step 2: Download Video

Use the download script with parameters:

```bash
python3 scripts/download.py "URL" \
  --output ~/Downloads/videos \
  --quality best \
  --format mp4
```

**Parameters:**
- `--output DIR`: Output directory (default: ~/Downloads/videos)
- `--quality Q`: best/1080p/720p/480p (default: best)
- `--format F`: mp4/mkv/webm (default: mp4)
- `--subtitles`: Download subtitles (zh-Hans, zh-Hant, en)
- `--audio-only`: Extract audio only (MP3)

### Step 3: Verify Download

Check file exists and size:
```bash
ls -lh ~/Downloads/videos/
```

## Advanced Options

**For more advanced features** like:
- Playlist downloads
- Authentication (cookies, login)
- Proxy configuration
- Rate limiting
- Custom format selectors

See [ADVANCED.md](references/ADVANCED.md) for complete options.

## Site-Specific Tips

**YouTube**: Best quality available, includes 4K/8K
**Bilibili**: Requires cookies for some videos
**TikTok**: May need to bypass regional restrictions
**Twitter**: Works best with direct tweet URLs

See [SITES.md](references/SITES.md) for site-specific guidance.

## Limitations and Known Issues

### YouTube (2025 Restrictions)

**Problem:** YouTube has implemented strict anti-bot measures since 2025.

**Symptoms:**
- Error: "Sign in to confirm you're not a bot"
- Requires authentication even for public videos
- Some videos need PO Token (Proof of Origin Token)

**Workarounds:**
1. Use browser cookies: `--cookies-from-browser chrome/safari`
2. Export cookies manually and use: `--cookies cookies.txt`
3. Try different player clients: `--extractor-args "youtube:player_client=android"`
4. For best results, consider using alternative platforms

**Success Rate:**
- ❌ YouTube: Limited success (requires manual intervention)
- ✅ Bilibili: High success rate
- ✅ Xiaohongshu: High success rate
- ✅ Vimeo, Twitter, TikTok: Generally works well

### Bilibili

**Issue:** HTTP 412 Precondition Failed error

**Solution:**
- Use Playwright to obtain cookies first
- Or use browser cookies: `--cookies-from-browser`

**Status:** ✅ Resolved with Playwright integration

## Error Handling

**Download fails:**
1. Check URL is valid and accessible
2. Try updating yt-dlp: `pip install -U yt-dlp`
3. Use `--info` flag to debug
4. Check network connection and proxy settings

**Video unavailable:**
- Video may be private or deleted
- Regional restrictions apply
- Requires authentication (provide cookies)

**Format issues:**
- Install FFmpeg: `brew install ffmpeg`
- Try different format: `--format mkv`
- Use `--quality best` for maximum compatibility

## Dependencies

Required:
- Python 3.6+
- yt-dlp: `pip install yt-dlp`

Recommended:
- FFmpeg: `brew install ffmpeg` (for format conversion)

Installation check:
```bash
python3 -m yt_dlp --version
ffmpeg -version
```

## Resources

### scripts/
- **download.py**: Main download script with full parameter support
  - Can be executed directly or imported as module
  - Returns JSON for `--info` mode
  - Handles errors gracefully

### references/
- **ADVANCED.md**: Advanced options and use cases
- **SITES.md**: Site-specific tips and workarounds

## Example Usage Patterns

**Pattern 1: Quick Download**
```bash
python3 scripts/download.py "URL"
```

**Pattern 2: Quality Selection**
```bash
python3 scripts/download.py "URL" --quality 1080p
```

**Pattern 3: Audio Extraction**
```bash
python3 scripts/download.py "URL" --audio-only
```

**Pattern 4: Batch Download**
```bash
# Loop through URLs file
while read url; do
  python3 scripts/download.py "$url" --output ~/Downloads/batch
done < urls.txt
```

**Pattern 5: Info Gathering**
```python
import json
result = subprocess.run([
  "python3", "scripts/download.py", "URL", "--info"
], capture_output=True, text=True)
info = json.loads(result.stdout)
print(f"Title: {info['title']}")
print(f"Duration: {info['duration']}")
```
