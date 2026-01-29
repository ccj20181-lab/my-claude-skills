# Notes: Upgrade Implementation Design

## Prompt Design for Realistic Screenshots
To match the new reference style (`上岸4.png`), the prompt needs to be very specific about:

1.  **Layout**:
    *   **NO Left Avatar**: The left side (student side) MUST NOT show an avatar. It should look like the avatar is cropped out off-screen to the left.
    *   **Right Avatar**: Woniu teacher's avatar must be visible on the right.
    *   **Cropped Input**: The bottom input bar should be cropped out/not visible.
2.  **Visual Style**:
    *   **Red Box**: Specific instruction to draw a "red rectangular outline" around key positive feedback messages from the student.
    *   **Font/Bubble**: Standard WeChat style.
3.  **Content**:
    *   Extract content from the markdown.
    *   Identify which messages are "positive feedback" to apply the red box.

## Script Modifications (`generate_wechat_screenshot.py`)

1.  **API Integration**:
    *   Integrate `NanoBananaClient` logic directly into the script (simplify from `finance-infographic` structure).
    *   Ensure `get_api_config` prioritizes Nano Banana.
2.  **Reference Image Handling**:
    *   Switch to using `wechat_reference.png` (the new image).
    *   Ensure it's passed correctly to the API.
3.  **Prompt Construction**:
    *   Update `build_prompt` function.
    *   Add logic to parse "red box" requirements (maybe add a marker in the chat content or auto-detect positive lengthier messages).
    *   *Decision*: For now, let's instruct the model to "highlight the longest/most positive student message with a red box" or manually mark it in the content if needed.
    *   *Better approach*: Let the model decide based on "positive feedback" or "success news".

## APIYi Configuration
- The script already attempts to load `.env` from `finance-infographic`.
- Ensure it reads `NANO_BANANA_API_KEY` and `NANO_BANANA_API_URL`.

## Red Box Logic
The user mentioned "对于特别正面的语句，还会用红色的方框框住".
- In the prompt, I will add: "Identify the most enthusiastic or important positive feedback message from the student (white bubble) and draw a hollow red rectangular box around it to highlight it, exactly like the reference image."

## Plan
1.  Update `generate_wechat_screenshot.py` with the new prompt and API logic.
2.  Test with a sample.
