# Advanced yt-dlp Options

Advanced configuration options for power users.

## Playlist Downloads

Download entire playlists:

```bash
python3 scripts/download.py "PLAYLIST_URL" --output ~/Downloads/playlist
```

**Options:**
- `--playlist-items 1-5`: Download specific items (1-5, or 3,7,10)
- `--playlist-reverse`: Download in reverse order
- `--playlist-end 10`: Stop after 10 videos

**Example:**
```bash
# Download first 5 videos of playlist
python3 scripts/download.py "PLAYLIST_URL" \
  --playlist-items 1-5 \
  --output ~/Downloads/playlist_part
```

## Authentication

### Cookies

Use browser cookies for age-restricted or private videos:

```bash
# Export cookies from browser (using browser extension)
# Then use with yt-dlp:
python3 -m yt_dlp --cookies cookies.txt "URL"
```

**Cookie export methods:**
1. Browser extension: "Get cookies.txt LOCALLY"
2. Netscape cookie format from browser

### Username/Password

For sites requiring login:

```bash
python3 -m yt_dlp \
  --username "USER" \
  --password "PASS" \
  "URL"
```

**Warning:** Avoid using password in command line (visible in process list). Use `--netrc` instead.

### API Keys

For services like YouTube:

```bash
python3 scripts/download.py "URL" --api-key "YOUR_KEY"
```

## Proxy Configuration

### HTTP/HTTPS Proxy

```bash
python3 scripts/download.py "URL" --proxy http://127.0.0.1:8080
```

### SOCKS Proxy

```bash
python3 scripts/download.py "URL" --proxy socks5://127.0.0.1:1080
```

### Environment Variables

```bash
export HTTP_PROXY="http://127.0.0.1:8080"
export HTTPS_PROXY="http://127.0.0.1:8080"
python3 scripts/download.py "URL"
```

## Rate Limiting

### Limit Download Speed

```bash
python3 scripts/download.py "URL" --limit-rate 1M
```

**Formats:**
- `50K` = 50 KB/s
- `1M` = 1 MB/s
- `10M` = 10 MB/s

### Sleep Between Videos (Playlists)

```bash
python3 scripts/download.py "PLAYLIST_URL" --sleep-interval 60
```

Adds 60 second delay between downloads.

## Format Selection

### Custom Format Strings

```bash
python3 scripts/download.py "URL" \
  -f "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best"
```

**Format selectors:**
- `height`: Video height (1080, 720, 480)
- `fps`: Frame rate (30, 60)
- `ext`: File extension (mp4, webm)
- `filesize`: File size (<500M)
- `vcodec`: Video codec (h264, vp9, av01)

**Examples:**

H.264 only (maximum compatibility):
```bash
-f "bestvideo[vcodec^=avc]+bestaudio[ext=m4a]/best[vcodec^=avc]"
```

File size limit (<500MB):
```bash
-f "bestvideo[filesize<500M]+bestaudio/best[filesize<500M]"
```

## Thumbnail and Metadata

### Embed Thumbnail

```bash
python3 scripts/download.py "URL" --embed-thumbnail
```

### Write Metadata

```bash
python3 scripts/download.py "URL" --write-info-json --embed-metadata
```

Saves video metadata to `.info.json` file and embeds into video.

## Subtitle Options

### All Subtitles

```bash
python3 scripts/download.py "URL" --write-subs --all-subs
```

### Auto-generated Subtitles

```bash
python3 scripts/download.py "URL" --write-auto-subs
```

### Subtitle Formats

```bash
python3 scripts/download.py "URL" --sub-format srt
```

Formats: srt, ass, vtt, lrc

## Post-Processing

### Convert to MP3

```bash
python3 scripts/download.py "URL" \
  --extract-audio \
  --audio-format mp3 \
  --audio-quality 0
```

### Trim Video

```bash
python3 scripts/download.py "URL" \
  --download-sections "*1:00-2:00"
```

Downloads from 1:00 to 2:00 only.

### Concatenate Videos

```bash
python3 scripts/download.py "URL1" "URL2" "URL3" \
  --concat-playlist \
  --output merged_video.%(ext)s
```

## Live Streams

Download live streams:

```bash
python3 scripts/download.py "LIVE_STREAM_URL" \
  --wait-for-video
```

**Options:**
- `--wait-for-video`: Wait until stream starts
- `--hls-live-restart`: Start from beginning
- `--download-archive archive.txt`: Skip already downloaded

## Batch Processing

### Download from File

Create `urls.txt` with one URL per line:

```
https://youtube.com/watch?v=xxx1
https://youtube.com/watch?v=xxx2
https://youtube.com/watch?v=xxx3
```

Download all:

```bash
cat urls.txt | xargs -I {} python3 scripts/download.py "{}"
```

### Configuration File

Create `yt-dlp.conf`:

```conf
# Output template
-o ~/Downloads/videos/%(title)s.%(ext)s

# Format selection
-f bestvideo+bestaudio

# Subtitles
--write-subs
--sub-lang zh-Hans,en

# Other options
--no-playlist
--embed-metadata
```

Use config file:

```bash
python3 -m yt_dlp --config-location yt-dlp.conf "URL"
```

## Debugging

### Verbose Output

```bash
python3 scripts/download.py "URL" --verbose
```

### Dump Pages

```bash
python3 scripts/download.py "URL" --dump-pages
```

Saves downloaded pages for debugging.

### Skip Download

```bash
python3 scripts/download.py "URL" --skip-download
```

Processes video without downloading (useful with `--print`).

## Network Options

### Retry Behavior

```bash
python3 scripts/download.py "URL" \
  --retries 10 \
  --fragment-retries 10
```

### Timeout

```bash
python3 scripts/download.py "URL" --socket-timeout 30
```

### User Agent

```bash
python3 scripts/download.py "URL" \
  --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
```

## Archive and Incremental Downloads

Track downloaded videos:

```bash
python3 scripts/download.py "PLAYLIST_URL" \
  --download-archive archive.txt
```

Skips already downloaded videos in subsequent runs.

## Thumbnail Gallery

Download all thumbnails from playlist:

```bash
python3 -m yt_dlp \
  --write-thumbnail \
  --skip-download \
  --output "thumbnail_%(autonumber)s.jpg" \
  "PLAYLIST_URL"
```
