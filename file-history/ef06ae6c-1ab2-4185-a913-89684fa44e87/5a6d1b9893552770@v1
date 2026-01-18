# Implementation Plan - Financial Calendar Cloud Workflow

## User Request
Implement a "Financial Calendar Automatic Reminder" workflow that runs on the cloud (GitHub Actions).
- **Features**: Remind about earnings reports, economic data, and policy meetings.
- **Timing**: 1 day in advance or on the day.
- **Notification**: WeChat (via PushPlus).

## Current State
- Existing project: `/Users/henry/Documents/daily-tech-digest/`
- Existing workflows: `daily-finance-digest.yml`
- Existing scripts: `finance_digest.py`, `send_pushplus.py`

## Proposed Approach

### 1. New Python Script: `scripts/financial_calendar.py`
This script will be responsible for:
- Fetching financial calendar data.
  - **Data Source Strategy**:
    - We will use `akshare` (a popular Python financial data library) to fetch the economic calendar. It wraps sources like Jin10, which provides reliable data on economic events (GDP, CPI, Rate Decisions) and earnings.
    - Specifically, we will use `akshare.economic_calendar` or similar functions.
- Filtering events for "Tomorrow" (Advance reminder) and "Today" (Immediate reminder).
- Formatting the notification message.
- Sending the notification using `scripts/send_pushplus.py` logic. We will refactor `send_pushplus.py` slightly to allow importing its send function, or duplicate the minimal logic if preferred to avoid breaking changes.

### 2. New GitHub Action Workflow: `.github/workflows/financial-calendar.yml`
- Schedule: Run daily at 18:00 UTC (02:00 Beijing) or closer to morning?
  - User said: "Timing: 1 day in advance or on the day."
  - If we run at 22:30 UTC (06:30 Beijing), we can show "Today's Events" and "Tomorrow's Key Events". This aligns with the existing digest.
- Steps:
  - Checkout code.
  - Setup Python.
  - Install dependencies (including `akshare`).
  - Run `scripts/financial_calendar.py`.
  - (Optional) Commit any updated data cache if we choose to store history.

### 4. Advanced Feature: Weekly "Super Event" Scanner
- **Requirement**: The user pointed out that we need to track major fixed-schedule events (like Fed meetings, Non-farm payrolls) further in advance, not just T+1.
- **Strategy**:
  - In `scripts/financial_calendar.py`, add a function `scan_weekly_super_events()`.
  - **Lookahead**: Scan the next 7 days (or up to next Sunday).
  - **Filter**: Use a strict keyword list to identify "Super Events" that justify an early reminder.
    - Keywords: "利率决议" (Interest Rate Decision), "非农" (Non-farm), "GDP", "CPI" (maybe too frequent, keep to high importance), "失业率" (Unemployment Rate).
  - **Output**: Add a new section "🌟 **未来一周重磅前瞻**" to the daily notification if any such events are found.
  - **Robustness**: Add retry logic for the `akshare` calls to handle potential timeouts (observed in testing).

## Detailed Implementation Steps

1.  **Modify `requirements.txt`**: Add `akshare>=1.0.0` (or recent version). (Done)
2.  **Refactor `scripts/send_pushplus.py`**:
    - Ensure `send_pushplus_notification` is importable and reusable. (Done)
3.  **Update `scripts/financial_calendar.py`**:
    - Add `fetch_data_with_retry` helper.
    - Implement `fetch_future_events(start_date, days)` to scan a date range.
    - Implement keyword-based filtering for "Super Events".
    - Update the message formatting to include the new "Future Lookahead" section.
4.  **Create Workflow**: `.github/workflows/financial-calendar.yml`. (Done)

## Verification Plan
- **Local Test**: Run `python scripts/financial_calendar.py` locally.
- **Lookahead Test**: Temporarily mock the date or use the test script to verify it catches a known future event (e.g., search for a date known to have data).
- **Notification Check**: Verify the PushPlus message includes the new section.
