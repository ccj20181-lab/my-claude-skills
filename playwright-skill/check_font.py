from fontTools.ttLib import TTFont
import os

font_path = os.path.expanduser("~/Library/Fonts/Microsoft Yahei.ttf")

if not os.path.exists(font_path):
    print(f"File not found: {font_path}")
else:
    try:
        font = TTFont(font_path)
        print(f"Checking font: {font_path}")
        # Name ID 1 is Font Family Name
        found = False
        for record in font['name'].names:
            if record.nameID == 1:
                try:
                    name = record.toUnicode()
                    print(f"Family Name: {name}")
                    found = True
                except:
                    pass
        if not found:
            print("No Family Name (ID 1) found.")
    except Exception as e:
        print(f"Error reading font: {e}")
