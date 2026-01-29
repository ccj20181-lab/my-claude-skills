
import os
from PIL import Image

def extract_avatar():
    base_dir = os.path.expanduser("~/.claude/skills/woniu-pyq")
    ref_path = os.path.join(base_dir, "references", "wechat_reference.png")
    output_path = os.path.join(base_dir, "assets", "avatar_woniu.png")

    if not os.path.exists(ref_path):
        print(f"Reference image not found: {ref_path}")
        return

    img = Image.open(ref_path)
    width, height = img.size
    print(f"Image size: {width}x{height}")

    # Estimate avatar position (standard WeChat right avatar)
    # Usually around 80-90% of width, and looks like a square
    # Let's try to crop a region and see.
    # Or better, let's look for the green bubbles and find the avatar next to them.

    # For now, I'll crop a region that likely contains the avatar based on typical layout
    # Assuming the first message is from the user (right side)
    # We might need to adjust these coordinates.
    # Standard WeChat avatar size is roughly 120x120 pixels on 1080p, but this is 4K maybe?
    # Let's just crop the top right area where an avatar usually is for the first message.

    # Actually, let's just create a script that crops the rightmost non-white/non-gray object near a green bubble.
    # But to be safe and simple, I will crop the top-most right avatar.
    # I'll crop a generous box from the right side and let the user check, or I can refine.
    # Wait, the plan says "Extract Woniu Avatar from the reference image".

    # Let's try to find the green color #95EC69
    green_color = (149, 236, 105) # #95EC69

    pixels = img.load()
    first_green_y = -1
    last_green_y = -1
    right_most_green_x = -1

    # Scan for green color to find bubbles
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y][:3]
            # Approximate match
            if abs(r - 149) < 10 and abs(g - 236) < 10 and abs(b - 105) < 10:
                if first_green_y == -1: first_green_y = y
                last_green_y = y
                if x > right_most_green_x:
                    right_most_green_x = x

    if first_green_y != -1:
        print(f"Found green bubble. Rightmost X: {right_most_green_x}, First Y: {first_green_y}")
        # Avatar should be to the right of this X.
        # Avatar usually starts slightly above the bubble or aligned.
        # And it's a square.

        # Let's guess the avatar center is to the right.
        avatar_left = right_most_green_x + 10 # padding
        # Find where the image data starts (non-background)
        # Background is #F7F7F7 or similar

        # Simple heuristic: Crop a square at the right edge at the same height as the green bubble.
        # Usually about 10-20px margin from right.

        # Let's just take a 130x130 box from the right margin aligned with the top of the green bubble.
        # Note: Green bubble usually has a triangle pointing to the avatar.

        # Refined guess:
        # Avatar is usually about 120x120 (on ~1000px wide screens).
        # Let's crop based on the green bubble's top Y.

        # Let's scan from right_most_green_x + gap to the right edge.
        # And from first_green_y roughly.

        # Actually, let's just output the whole image first to check size? No, too big.
        # I'll assume standard layout logic:
        # Avatar Top is roughly aligned with Bubble Top.
        # Avatar is to the right of the bubble.

        # Let's define the scan area for the avatar:
        scan_x_start = right_most_green_x + 5
        scan_y_start = first_green_y

        # Find the bounding box of non-background pixels in this area
        bg_color = pixels[width-5, first_green_y] # Sample background from right edge? No, right edge might be margin.

        # Let's assume background is roughly (247, 247, 247) #F7F7F7

        min_x, min_y, max_x, max_y = width, height, 0, 0
        found = False

        for y in range(max(0, first_green_y - 20), min(height, last_green_y + 100)):
            for x in range(scan_x_start, width):
                r, g, b = pixels[x, y][:3]
                # Check if not background
                if abs(r - 247) > 10 or abs(g - 247) > 10 or abs(b - 247) > 10:
                    if x < min_x: min_x = x
                    if y < min_y: min_y = y
                    if x > max_x: max_x = x
                    if y > max_y: max_y = y
                    found = True

        if found:
            print(f"Found content column at: {min_x}, {min_y}, {max_x}, {max_y}")

            # The previous logic captured the whole column. We just want the top avatar.
            # Avatars are square. Let's use the width to determine the height.
            width_px = max_x - min_x

            # Ensure we don't go out of bounds or take too little
            if width_px > 50:
                 # Crop a square from the top
                avatar_height = width_px # Square
                # Actually, often there is a tiny bit of vertical padding or alignment diff.
                # Let's check if the pixels strictly form a square block at the top.

                # But simply cropping the square at the top (min_y) with size (width_px) is a very safe bet for a clean avatar
                # if min_x/max_x correctly identified the horizontal bounds.

                avatar = img.crop((min_x, min_y, max_x + 1, min_y + width_px + 1))
                avatar.save(output_path)
                print(f"Saved avatar (square crop) to {output_path}. Size: {width_px}x{width_px}")
            else:
                print("Width too small, something went wrong.")
        else:
            print("Could not detect avatar automatically.")

    else:
        print("No green bubbles found.")

if __name__ == "__main__":
    extract_avatar()
