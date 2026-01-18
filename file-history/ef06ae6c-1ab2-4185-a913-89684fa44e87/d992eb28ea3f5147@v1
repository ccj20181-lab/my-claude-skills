
import akshare as ak
import datetime
import pandas as pd

def test_deep_lookahead():
    today = datetime.datetime.now().date()
    # Check next 7 days sequentially
    print(f"Scanning from {today} for 7 days...")

    found_any = False

    for i in range(1, 8):
        target_date = today + datetime.timedelta(days=i)
        date_str = target_date.strftime("%Y%m%d")

        try:
            df = ak.news_economic_baidu(date=date_str)
            if df is not None and not df.empty:
                # Count high importance events
                # Ensure '重要性' column exists and handle types
                if '重要性' in df.columns:
                    # Convert to numeric, forcing errors to NaN then 0
                    df['importance_num'] = pd.to_numeric(df['重要性'], errors='coerce').fillna(0)
                    high_imp = df[df['importance_num'] >= 3]

                    if not high_imp.empty:
                        print(f"\n[Date: {target_date}] Found {len(high_imp)} High Importance Events:")
                        for _, row in high_imp.iterrows():
                            print(f"  - {row['时间']} {row['地区']} {row['事件']}")
                        found_any = True
                    else:
                        print(f"[Date: {target_date}] Data found but no High importance events.")
                else:
                    print(f"[Date: {target_date}] Data found but '重要性' column missing.")
            else:
                print(f"[Date: {target_date}] No data available.")

        except Exception as e:
            print(f"Error for {target_date}: {e}")

    if not found_any:
        print("\nWarning: No high importance events found in the next 7 days. This might indicate API limitations or a quiet week.")

if __name__ == "__main__":
    test_deep_lookahead()
