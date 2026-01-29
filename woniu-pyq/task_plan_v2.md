# Task Plan: Refine Screenshot Generation for 100% Style Match

## Goal
Achieve "pixel-perfect" style replication of the WeChat screenshot reference, changing ONLY the text content. Ensure red box highlighting and layout are identical to reference.

## Phases
- [x] Phase 1: Analysis & Prompt Engineering
    - Review current prompt and identify "loose" instructions.
    - Design a "Strict Template" prompt strategy.
- [x] Phase 2: Implementation
    - Update `generate_wechat_screenshot.py` with the hardened prompt.
    - Ensure "image-to-image" context is maximized.
- [x] Phase 3: Verification
    - Generate a test image.
    - User review.

## Key Constraints
- Left avatar MUST be cropped/invisible.
- Right avatar MUST be Woniu teacher (exact match).
- Layout MUST exclude bottom input bar.
- Red box MUST be applied to positive feedback.
- Font/Color MUST be identical.

## Decisions Made
- Will use "Style Transfer" language in prompt ("Use this image as a strict visual template").

## Status
**Completed** - Generation finished, awaiting user feedback.
