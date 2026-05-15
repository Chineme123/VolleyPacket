import csv
import requests
from datetime import datetime, timedelta

from app import config


def fetch_delivery_events(start_date: str = None, end_date: str = None, limit: int = 2500) -> list[dict]:
    if not config.BREVO_API_KEY:
        return []

    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    headers = {
        "accept": "application/json",
        "api-key": config.BREVO_API_KEY,
    }

    all_events = []
    offset = 0

    while True:
        params = {
            "limit": min(limit, 2500),
            "offset": offset,
            "startDate": start_date,
            "endDate": end_date,
            "event": "delivered",
        }
        resp = requests.get(config.BREVO_EVENTS_URL, headers=headers, params=params, timeout=30)
        if resp.status_code != 200:
            break

        data = resp.json()
        events = data.get("events", [])
        if not events:
            break

        all_events.extend(events)
        offset += len(events)

        if offset >= limit or len(events) < 2500:
            break

    # Also fetch "sent" events
    offset = 0
    while True:
        params = {
            "limit": min(limit, 2500),
            "offset": offset,
            "startDate": start_date,
            "endDate": end_date,
            "event": "requests",
        }
        resp = requests.get(config.BREVO_EVENTS_URL, headers=headers, params=params, timeout=30)
        if resp.status_code != 200:
            break

        data = resp.json()
        events = data.get("events", [])
        if not events:
            break

        all_events.extend(events)
        offset += len(events)

        if offset >= limit or len(events) < 2500:
            break

    return all_events


def get_successful_emails(start_date: str = None, end_date: str = None) -> set[str]:
    events = fetch_delivery_events(start_date, end_date)
    successful = set()
    for event in events:
        email = event.get("email", "").strip().lower()
        if email:
            successful.add(email)
    return successful


def parse_brevo_csv(file_path: str) -> set[str]:
    successful = set()
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            status = row.get("st_text", "").strip().lower()
            if status in ("sent", "delivered"):
                email = row.get("email", "").strip().lower()
                if email:
                    successful.add(email)
    return successful
