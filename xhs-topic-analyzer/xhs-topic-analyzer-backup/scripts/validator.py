import json
import os
import sys

def validate_data(file_path):
    """
    Strict validation of data file
    """
    print(f"[Validator] Checking file: {file_path} ...")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"[ERROR] File not found: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise ValueError(f"[ERROR] JSON decode failed: {file_path}")

    # Compatibility
    if isinstance(data, dict) and "feeds" in data:
        items = data["feeds"]
    elif isinstance(data, list):
        items = data
    else:
        raise ValueError("[ERROR] Data structure invalid: Must be List or Dict with 'feeds'")

    if not items:
        raise ValueError("[ERROR] Empty data: No items found")

    # Sample check
    valid_count = 0
    for idx, item in enumerate(items[:5]):
        # Handle nested structure
        if "noteCard" in item:
            card = item["noteCard"]
            title = card.get("displayTitle", "")
            likes = card.get("interactInfo", {}).get("likedCount", 0)
            fans = card.get("user", {}).get("fans", 0) # 检查 fans
        else:
            title = item.get("title", "")
            likes = item.get("likes", 0)
            fans = item.get("fans", 0)

        if title and likes is not None:
            # 弱校验通过
            pass
        else:
            print(f"[Warning] Item {idx+1} missing key fields (Title/Likes)")

        if not fans:
             print(f"[Warning] Item {idx+1} missing FANS count. Profile enrichment needed?")
        else:
             valid_count += 1

    if valid_count == 0:
        print("[ERROR] Poor data quality: No items have 'fans' data. Did you run profile enrichment?")
        # 暂时抛出异常，强制要求有粉丝数据
        raise ValueError("[ERROR] Data validation failed: Missing FANS data.")

    print(f"[SUCCESS] Validation passed! Valid items (with fans): {valid_count}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validator.py <data_file>")
        sys.exit(1)

    try:
        validate_data(sys.argv[1])
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        sys.exit(1)
