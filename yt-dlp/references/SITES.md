# Site-Specific Tips

Tips and workarounds for specific video platforms.

## YouTube

### Best Quality

YouTube offers up to 8K video:

```bash
python3 scripts/download.py "URL" --quality best
```

### Age-Restricted Videos

Use cookies from browser:

```bash
python3 -m yt_dlp --cookies cookies.txt "URL"
```

### Chapters and Metadata

```bash
python3 scripts/download.py "URL" --write-description --write-info-json
```

### YouTube Shorts

```bash
python3 scripts/download.py "https://youtube.com/shorts/VIDEO_ID"
```

## Bilibili

### High-Quality Videos

Bilibili requires login for high quality (1080P+):

1. Login to Bilibili in browser
2. Export cookies using browser extension
3. Use cookies with yt-dlp:

```bash
python3 -m yt_dlp --cookies bilibili_cookies.txt "URL"
```

### DASH Formats

For DASH streams (highest quality):

```bash
python3 -m yt_dlp --format "bestvideo[ext=mp4]+bestaudio[ext=m4a]" "URL"
```

### Bangumi (Anime)

Some anime content requires membership:

```bash
python3 -m yt_dlp --cookies cookies.txt "BANGUMI_URL"
```

## Twitter/X

### Direct Tweet URLs

Best to use direct tweet URLs:

```
https://twitter.com/user/status/TWEET_ID
```

### GIF Videos

Twitter videos are often tagged as GIFs but are actually MP4:

```bash
python3 scripts/download.py "TWEET_URL"
```

### Mobile URLs

Mobile URLs work better than desktop:

```
https://mobile.twitter.com/user/status/TWEET_ID
```

## TikTok

### Regional Restrictions

Some videos are region-locked. Use proxy:

```bash
python3 scripts/download.py "URL" --proxy socks5://127.0.0.1:1080
```

### Watermark-Free

TikTok downloads include watermark by default. No direct workaround.

### User Profiles

Download all videos from user:

```bash
python3 -m yt_dlp "https://www.tiktok.com/@USERNAME"
```

## Instagram

### Login Required

Most content requires authentication:

```bash
python3 -m yt_dlp --username "USER" --password "PASS" "URL"
```

**Better approach:** Use session cookies:

```bash
python3 -m yt_dlp --cookies instagram_cookies.txt "URL"
```

### Reels and Stories

```bash
# Reels
python3 scripts/download.py "https://www.instagram.com/reels/VIDEO_ID"

# Stories (requires cookies)
python3 -m yt_dlp --cookies cookies.txt "STORY_URL"
```

## 抖音 (Douyin)

### Watermark

Douyin videos include watermark. No official workaround.

### Web URLs

Use web URLs instead of app URLs:

```
https://www.douyin.com/video/VIDEO_ID
```

### Sharing Links

Douyin sharing links work:

```
https://v.douyin.com/SHARE_CODE/
```

yt-dlp will automatically follow redirects.

## 快手 (Kuaishou)

### Quality Selection

```bash
python3 scripts/download.py "URL" --quality best
```

### Login for High Quality

Similar to Bilibili, high-quality content requires cookies:

```bash
python3 -m yt_dlp --cookies kuaishou_cookies.txt "URL"
```

## Vimeo

### Password-Protected Videos

```bash
python3 -m yt_dlp --video-password "PASSWORD" "URL"
```

### Private Videos

Use cookies:

```bash
python3 -m yt_dlp --cookies vimeo_cookies.txt "URL"
```

## Twitch

### VODs (Videos on Demand)

```bash
python3 scripts/download.py "TWITCH_VOD_URL"
```

### Clips

```bash
python3 scripts/download.py "https://clips.twitch.tv/CLIP_SLUG"
```

### Live Streams

Download ongoing stream:

```bash
python3 scripts/download.py "LIVE_STREAM_URL" --wait-for-video
```

### Authentication (OAuth)

For subscribers-only content:

```bash
python3 -m yt_dlp --oauth2-v2 --cookies cookies.txt "URL"
```

## Facebook

### Public Videos

Public videos work without authentication:

```bash
python3 scripts/download.py "FB_VIDEO_URL"
```

### Private Videos

Use cookies:

```bash
python3 -m yt_dlp --cookies fb_cookies.txt "URL"
```

### 4K Videos

Facebook supports 4K. Use:

```bash
python3 scripts/download.py "URL" --quality best
```

## SoundCloud

### High-Quality Audio

```bash
python3 scripts/download.py "URL" --audio-format flac
```

### Entire Playlists

```bash
python3 scripts/download.py "PLAYLIST_URL" --audio-format mp3
```

### Requires Login

Some tracks require authentication:

```bash
python3 -m yt_dlp --username "EMAIL" --password "PASS" "URL"
```

## Spotify

### Requires Spotify API

Spotify downloads require premium account:

```bash
python3 -m yt_dlp \
  --username "EMAIL" \
  --password "PASS" \
  "SPOTIFY_URL"
```

**Note:** Downloading from Spotify may violate ToS.

## Dailymotion

### Age-Restricted

Use cookies:

```bash
python3 -m yt_dlp --cookies dailymotion_cookies.txt "URL"
```

### Quality Selection

```bash
python3 scripts/download.py "URL" --quality 1080p
```

## 通用的故障排除技巧

### Video Not Available

1. **Check URL is correct** - Copy from browser address bar
2. **Check video is public** - Private/deleted videos won't download
3. **Try with cookies** - Age or login restrictions
4. **Update yt-dlp** - `pip install -U yt-dlp`
5. **Check region** - Use proxy if region-locked

### Download Failures

1. **Network issues** - Check connection, try proxy
2. **Corrupted download** - Add `--retries 10`
3. **FFmpeg missing** - Install FFmpeg for merging
4. **Disk space** - Check available space

### Format Issues

1. **Try different format** - `--format mkv`
2. **Use best compatibility** - `--format best`
3. **Install FFmpeg** - Required for format conversion

### Slow Downloads

1. **Limit rate** - `--limit-rate 1M`
2. **Use proxy** - `--proxy http://PROXY`
3. **Reduce quality** - `--quality 720p`
4. **Download audio only** - `--audio-only`
