# Whiteboard Video Generator

Turn Markdown scripts into hand-drawn whiteboard videos using Remotion and Gemini AI.

## Description
This skill provides a complete workflow to generate professional "whiteboard animation" style videos from simple Markdown scripts. It handles script parsing, asset analysis, AI image generation (using Gemini), and Remotion component generation.

## Usage
```
/whiteboard-video-gen <command> [args]
```

### Commands
- `scaffold`: Create a new Remotion project structure for whiteboard videos in the current directory.
- `generate <videoId>`: Run the full generation pipeline for a specific video ID.
  - `--skip-assets`: Skip the AI image generation step.
  - `--force`: Force overwrite existing files.

## Workflow
1.  **Write Script**: Create `content/scripts/<videoId>.md`.
2.  **Generate**: Run `/whiteboard-video-gen generate <videoId>`.
3.  **Preview**: Run `npm start` to see your video.

## Configuration
Requires `APIYI_API_KEY` or `NANO_BANANA_API_KEY` environment variable for image generation.
