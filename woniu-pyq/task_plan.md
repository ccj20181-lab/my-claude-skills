# Task Plan: Upgrade woniu-pyq Skill with Realistic Screenshot Generation

## Goal
Upgrade the `woniu-pyq` skill to generate high-quality, realistic WeChat conversation screenshots using APIYi (Nano Banana Pro), strictly following the visual style of the reference image (no left avatar, red highlights, cropped input box).

## Phases
- [x] Phase 1: Analysis & Setup
    - Analyze existing skill structure.
    - Analyze reference image (`/Users/henry/Desktop/上岸4.png`).
    - Research `finance-infographic` skill for APIYi implementation.
- [x] Phase 2: Implementation Design
    - Design detailed image generation prompts.
    - Plan script modifications.
- [x] Phase 3: Coding
    - Update `generate_wechat_screenshot.py`.
    - Integrate APIYi API calls.
    - Implement "Red Box" highlighting logic in the prompt.
- [x] Phase 4: Testing & Verification
    - Generate sample screenshots.
    - Verify visual details (avatar, layout, red boxes).

## Key Questions
1. How does `finance-infographic` handle API authentication and calls?
   - Answer: It uses `APIClient` abstract base class with specific implementations for Google and NanoBanana, handling image/text generation requests and responses including base64 decoding.
2. What specific prompt keywords trigger the "red box" and "no left avatar" style reliably?
   - Answer: Prompt needs to explicitly instruction to "crop out left avatar", "use red rectangular box outline for emphasis", and "no input box at bottom".

## Decisions Made
- [Decision]: Use APIYi Nano Banana Pro as requested.
- [Decision]: Reuse `finance-infographic`'s `.env` configuration logic but adapt the API call code directly into the script for self-containment (or reuse if importable, but copy-paste is safer for independence).
- [Decision]: Update reference image to the new one provided by user (`/Users/henry/Desktop/上岸4.png`).
- [Decision]: Prompt must emphasize "hollow red rectangular box" for positive feedback.

## Errors Encountered
- [Error]: None so far.

## Status
**Completed** - Upgrade finished and verified.
