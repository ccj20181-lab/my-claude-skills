
import akshare as ak
import datetime
import pandas as pd

def test_future_events():
    today = datetime.datetime.now().date()
    # Test fetching data for 3 days and 7 days from now
    offsets = [3, 7]

    for offset in offsets:
        target_date = today + datetime.timedelta(days=offset)
        date_str = target_date.strftime("%Y%m%d")
        print(f"\nFetching economic calendar for {target_date}...")

        try:
            df = ak.news_economic_baidu(date=date_str)
            if df is None or df.empty:
                print(f"No data for {target_date}")
            else:
                print(f"Found {len(df)} events.")
                # Filter for High importance to see if 'big' events are listed
                # Note: Baidu importance is usually numeric 1,2,3 or string
                print("Sample high importance events:")
                for _, row in df.iterrows():
                    # Check importance
                    imp = row.get('重要性', '')
                    event = row.get('事件', '')
                    # Print if likely high importance
                    if str(imp) == '3' or '高' in str(imp):
                        print(f"- {row.get('时间')} {event} (Imp: {imp})")

        except Exception as e:
            print(f"Error fetching {target_date}: {e}")

if __name__ == "__main__":
    test_future_events()
