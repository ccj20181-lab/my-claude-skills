import json
import os

def convert():
    if not os.path.exists('raw_search.json'):
        print("raw_search.json not found")
        return

    with open('raw_search.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_feeds = []
    if "feeds" in data:
        all_feeds = data["feeds"]
    else:
        for keyword, feeds in data.items():
            if isinstance(feeds, list):
                all_feeds.extend(feeds)

    users = {}
    for feed in all_feeds:
        if isinstance(feed, str): continue
        note_card = feed.get("noteCard", {})
        user = note_card.get("user", {})
        user_id = user.get("userId")

        if not user_id: continue

        if user_id not in users:
            users[user_id] = {
                "userId": user_id,
                "nickname": user.get("nickname", ""),
                "avatar": user.get("avatar", ""),
                "feeds": []
            }

        interact = note_card.get("interactInfo", {})
        simple_feed = {
            "id": feed.get("id"),
            "xsecToken": feed.get("xsecToken"),
            "type": note_card.get("type", "normal"),
            "title": note_card.get("displayTitle", ""),
            "cover": note_card.get("cover", {}),
            "likedCount": interact.get("likedCount", 0),
            "collectedCount": interact.get("collectedCount", 0),
            "commentCount": interact.get("commentCount", 0),
            "sharedCount": interact.get("sharedCount", 0),
        }
        users[user_id]["feeds"].append(simple_feed)

    output = {
        "users": users,
        "metadata": {"keywords": ["理财"]}
    }

    with open('raw_data_with_users.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("Converted raw_search.json to raw_data_with_users.json successfully!")

if __name__ == "__main__":
    convert()
