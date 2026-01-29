
import os
from PIL import Image

output_dir = os.path.expanduser("~/.claude/skills/woniu-pyq/output")
# Find the most recent hybrid image
files = [f for f in os.listdir(output_dir) if f.startswith("wechat_chat_hybrid_") and f.endswith(".png")]
files.sort()
latest_file = os.path.join(output_dir, files[-1])

print(f"Analyzing file: {latest_file}")

img = Image.open(latest_file)
print(f"Format: {img.format}")
print(f"Mode: {img.mode}")
print(f"Size: {img.size}")

width, height = img.size

# Sample pixels
print("\nPixel Sampling:")
# Top left
print(f"Top-Left (0,0): {img.getpixel((0,0))}")
# Center
print(f"Center ({width//2}, {height//2}): {img.getpixel((width//2, height//2))}")
# Bottom Center
print(f"Bottom-Center ({width//2}, {height-10}): {img.getpixel((width//2, height-10))}")

# Check for large black areas
black_count = 0
total_pixels = 0
# Sample a grid
step = 50
for y in range(0, height, step):
    for x in range(0, width, step):
        p = img.getpixel((x, y))
        total_pixels += 1
        # Check for pure black or near black
        if isinstance(p, tuple):
            if sum(p) < 10: # Very dark
                black_count += 1
        elif p < 10:
             black_count += 1

print(f"\nBlack pixel ratio (approx): {black_count/total_pixels:.2%}")

