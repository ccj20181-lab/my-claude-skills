from fontTools.ttLib import TTFont
import os

font_path = os.path.expanduser("~/Library/Fonts/PingFang-SC-Regular.ttf")

if not os.path.exists(font_path):
    print(f"File not found: {font_path}")
else:
    try:
        font = TTFont(font_path)
        print(f"Checking font: {font_path}")
        # Name ID 1 is Font Family Name, ID 4 is Full Name, ID 6 is Postscript Name
        for record in font['name'].names:
            if record.nameID in [1, 4, 6]:
                try:
                    name = record.toUnicode()
                    id_name = {1: "Family Name", 4: "Full Name", 6: "Postscript Name"}[record.nameID]
                    print(f"{id_name}: {name}")
                except:
                    pass
    except Exception as e:
        print(f"Error reading font: {e}")
