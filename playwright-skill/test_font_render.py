import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import os

# Define the font path directly to be sure
font_path = os.path.expanduser("~/Library/Fonts/PingFang-SC-Regular.ttf")
prop = FontProperties(fname=font_path)

print(f"Testing font: {font_path}")
print(f"Font family from properties: {prop.get_name()}")

try:
    plt.figure(figsize=(6, 4))
    # Title with Chinese characters
    plt.title('中文测试: 苹方字体 (PingFang SC)', fontproperties=prop, size=20)
    plt.text(0.5, 0.5, '你好，世界！\nHello World!', 
             fontproperties=prop, size=24, 
             ha='center', va='center')
    plt.axis('off')
    
    output_file = 'test_pingfang_output.png'
    plt.savefig(output_file)
    print(f"Successfully saved {output_file}")
    
except Exception as e:
    print(f"Error during plotting: {e}")

# Also check if we can find it by family name now that cache is cleared
try:
    from matplotlib.font_manager import fontManager
    # Reload fonts - usually happens automatically but good to be sure
    # In newer matplotlib, this might not be needed or done differently, 
    # but accessing ttflist usually triggers a scan if needed or we rely on the cache rebuild we forced.
    found = False
    for f in fontManager.ttflist:
        if 'PingFang' in f.name:
            print(f"Found registered font: {f.name} at {f.fname}")
            found = True
    
    if not found:
        print("PingFang SC not found in Matplotlib font manager list yet (might need full re-scan).")
        
except Exception as e:
    print(f"Error checking font manager: {e}")

