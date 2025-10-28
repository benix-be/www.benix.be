"""
Utilities to expose the meetup context as an iCalendar feed.
"""
from __future__ import annotations

import re
from datetime import date, datetime, time as time_, timedelta
from pathlib import Path
from typing import Any, Iterable, Mapping

from ics import Calendar, Event
from zoneinfo import ZoneInfo

TIMEZONE_NAME = "Europe/Brussels"
try:
    LOCAL_TIMEZONE = ZoneInfo(TIMEZONE_NAME)
except Exception:  # pragma: no cover - tzdata may be missing
    LOCAL_TIMEZONE = None

ORDINAL_SUFFIX = re.compile(r"(\d{1,2})(st|nd|rd|th)")
DEFAULT_DURATION = timedelta(hours=4)


class CalendarExportError(Exception):
    """Raised when the calendar cannot be generated from the provided data."""


def _strip_ordinals(value: str) -> str:
    return ORDINAL_SUFFIX.sub(r"\1", value)


def _normalise_date_string(value: str) -> str:
    cleaned = _strip_ordinals(value)
    return cleaned.replace(",", "")


def _parse_date(value: str) -> date:
    cleaned = _normalise_date_string(value)
    parts = cleaned.split()

    if len(parts) == 4:
        parts = parts[1:]

    if len(parts) != 3:
        raise CalendarExportError(f"Unrecognised date format: {value!r}")

    month, day, year = parts
    try:
        return datetime.strptime(f"{month} {day} {year}", "%B %d %Y").date()
    except ValueError as exc:  # pragma: no cover - unexpected formats
        raise CalendarExportError(f"Failed to parse date {value!r}") from exc


def _parse_time(value: str | None) -> time_ | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError as exc:
        raise CalendarExportError(f"Failed to parse time {value!r}") from exc


def _combine_with_timezone(meetup_date: date, t: time_) -> datetime:
    dt = datetime.combine(meetup_date, t)
    if LOCAL_TIMEZONE:
        dt = dt.replace(tzinfo=LOCAL_TIMEZONE)
    return dt


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _meetup_to_event(meetup: Mapping[str, Any]) -> Event:
    if "date" not in meetup:
        raise CalendarExportError("Meetup entry is missing a date field")

    meetup_date = _parse_date(str(meetup["date"]))
    meetup_time = _parse_time(meetup.get("time"))
    raw_end_time = meetup.get("end_time")
    meetup_end_time = _parse_time(raw_end_time)
    city = str(meetup.get("city") or "").strip()
    program = _clean(meetup.get("program"))
    food = _clean(meetup.get("food"))
    discussion = _clean(meetup.get("discussion"))

    venue_info = meetup.get("venue") or {}
    venue_address = _clean(venue_info.get("address"))
    venue_url = _clean(venue_info.get("url"))
    geolocation = venue_info.get("geolocation") or {}
    latitude = geolocation.get("latitude")
    longitude = geolocation.get("longitude")

    title_suffix = f" – {city}" if city else ""
    event = Event(name=f"BeNix meetup{title_suffix}")

    if meetup_time:
        begin = _combine_with_timezone(meetup_date, meetup_time)
        event.begin = begin
        if meetup_end_time:
            end = _combine_with_timezone(meetup_date, meetup_end_time)
            if end <= begin:
                end += timedelta(days=1)
            event.end = end
        else:
            event.duration = DEFAULT_DURATION
    else:
        event.begin = meetup_date
        event.make_all_day()

    if venue_address:
        event.location = venue_address
    elif city:
        event.location = city

    description_lines = []
    if program:
        description_lines.append(f"Program: {program}")
    if food:
        description_lines.append(f"Food: {food}")
    if venue_address and city and city not in venue_address:
        description_lines.append(f"City: {city}")
    if venue_url:
        description_lines.append(f"Venue website: {venue_url}")
    if latitude is not None and longitude is not None:
        lat_str = _clean(latitude)
        lon_str = _clean(longitude)
        if lat_str and lon_str:
            description_lines.append(
                "Map: "
                f"https://www.openstreetmap.org/?mlat={lat_str}&mlon={lon_str}#map=18/{lat_str}/{lon_str}"
            )
    if raw_end_time:
        description_lines.append(f"Planned end time: {raw_end_time}.")
    if not meetup_time:
        description_lines.append("Exact start time to be confirmed.")
    if discussion:
        description_lines.append(f"Discussion: {discussion}")

    if description_lines:
        event.description = "\n".join(description_lines)

    if discussion:
        event.url = discussion
    elif venue_url:
        event.url = venue_url
    else:
        event.url = "https://www.benix.be/"
    return event


def build_calendar(context: Mapping[str, Any]) -> Calendar:
    calendar = Calendar()
    meetups: Iterable[Mapping[str, Any]] = context.get("next_meetups", []) or []

    for meetup in meetups:
        event = _meetup_to_event(meetup)
        calendar.events.add(event)

    return calendar


def export_calendar(context: Mapping[str, Any], destination: Path | str) -> Path:
    calendar = build_calendar(context)
    dest_path = Path(destination)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    calendar_text = calendar.serialize()
    if not calendar_text.endswith("\n"):
        calendar_text += "\n"
    dest_path.write_text(calendar_text, encoding="utf-8")
    return dest_path


__all__ = ["export_calendar", "build_calendar", "CalendarExportError"]
