"""Sensor for Caendar events helper."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import partial

from arrow.locales import get_locale
from babel.dates import format_date, format_time, format_timedelta, get_datetime_format

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from .const import (
    CONF_DAYS_AHEAD,
    CONF_MAX_EVENTS,
    CONF_REMOVE_RECURRING_EVENTS,
    CONF_SHOW_END_DATE,
    CONF_SHOW_EVENT_AS_TIME_TO,
    CONF_SHOW_SUMMARY,
    LOGGER,
)


# ------------------------------------------------------
# ------------------------------------------------------
@dataclass
class CalendarEvent:
    """Calendar event."""

    def __init__(
        self,
        calendar: str,
        start: str,
        end: str,
        summary: str,
        description: str,
        location: str,
        start_time_formatted: str = "",
        end_time_formatted: str = "",
    ) -> None:
        "Init."

        self.calendar: str = calendar
        self.start: str = start
        self.end: str = end
        self.summary: str = summary
        self.description: str = description
        self.location: str = location
        self.start_time_formatted: str = start_time_formatted
        self.end_time_formatted: str = end_time_formatted


# ------------------------------------------------------
# ------------------------------------------------------
class CalendarHandler:
    """Calendar handler."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Init."""

        self.hass: HomeAssistant = hass
        self.entry: ConfigEntry = entry
        self.events: list[CalendarEvent] = []
        self.language: str = "en"

    # ------------------------------------------------------
    async def get_process_calendar_events(self, calendar_entities: list[str]) -> None:
        """Process calendar events."""

        self.events = []

        try:
            tmp_events: dict = await self.hass.services.async_call(
                "calendar",
                "get_events",
                service_data={
                    ATTR_ENTITY_ID: calendar_entities,
                    "end_date_time": (
                        datetime.now()
                        + timedelta(days=self.entry.options.get(CONF_DAYS_AHEAD, 30))
                    ).isoformat(),
                    "start_date_time": datetime.now().isoformat(),
                },
                blocking=True,
                return_response=True,
            )
        # except (ServiceValidationError, ServiceNotFound, vol.Invalid) as err:
        except Exception as err:  # noqa: BLE001
            LOGGER.error(err)
            return

        for key in tmp_events:
            for event in tmp_events[key]["events"]:
                self.events.append(
                    CalendarEvent(
                        key,
                        event["start"],
                        event["end"],
                        event.get("summary", ""),
                        event.get("description", ""),
                        event.get("location", ""),
                    )
                )

        if self.entry.options.get(CONF_REMOVE_RECURRING_EVENTS, True):
            self.remove_recurring_events()

        self.events.sort(key=lambda x: x.start)
        self.events = self.events[: int(self.entry.options.get(CONF_MAX_EVENTS, 5))]

    # ------------------------------------------------------
    def remove_recurring_events(self) -> None:
        """Remove recurring events."""

        index: int = 0

        while index < (len(self.events) - 1):
            for index2, _ in reversed(list(enumerate(self.events))):
                if index2 <= index:
                    break
                if (
                    self.events[index].calendar == self.events[index2].calendar
                    and self.events[index].summary == self.events[index2].summary
                    and self.events[index].description
                    == self.events[index2].description
                    and datetime.fromisoformat(self.events[index].start).time()
                    == datetime.fromisoformat(self.events[index2].start).time()
                    and datetime.fromisoformat(self.events[index].end).time()
                    == datetime.fromisoformat(self.events[index2].end).time()
                ):
                    del self.events[index2]
            index += 1

    # ------------------------------------------------------
    async def async_format_datetime(self, date_time: datetime) -> str | None:
        """Format datetime."""
        dt_format = await self.hass.async_add_executor_job(
            get_datetime_format, "medium", self.language
        )

        time_str: str = await self.hass.async_add_executor_job(
            partial(
                format_time,
                time=date_time,
                format="short",
                locale=self.language,
            )
        )
        date_str: str = await self.hass.async_add_executor_job(
            partial(
                format_date,
                date=date_time,
                format="medium",
                locale=self.language,
            )
        )

        return dt_format.format(time_str, date_str)

    # ------------------------------------------------------
    async def async_format_event(self, event_num: int) -> str | None:
        """Format event."""

        if event_num < len(self.events):
            tmp_event = self.events[event_num]
            start_date: datetime = datetime.fromisoformat(tmp_event.start)
            start_date_next: datetime = start_date + timedelta(days=1)
            end_date: datetime = datetime.fromisoformat(tmp_event.end)

            day_event: bool = False

            if (
                start_date_next == end_date
                and start_date.hour == 0
                and start_date.minute == 0
                and end_date.hour == 0
                and end_date.minute == 0
            ):
                day_event = True

            diff: timedelta = start_date - datetime.now(start_date.tzinfo)

            if day_event and diff.total_seconds() < 0:
                time_str: str = (
                    get_locale(self.language).timeframes.get("now", "now").capitalize()
                )

            elif self.entry.options.get(CONF_SHOW_EVENT_AS_TIME_TO, False):
                time_str: str = await self.hass.async_add_executor_job(
                    partial(
                        format_timedelta,
                        delta=diff,
                        add_direction=True,
                        locale=self.language,
                    )
                )

            else:
                time_str = await self.async_format_datetime(start_date)
                tmp_event.start_time_formatted = time_str
                tmp_event.end_time_formatted = await self.async_format_datetime(
                    end_date
                )
                if self.entry.options.get(CONF_SHOW_END_DATE, False):
                    time_str = time_str + " - " + tmp_event.end_time_formatted

            if self.entry.options.get(CONF_SHOW_SUMMARY, False):
                time_str = time_str + " - " + tmp_event.summary
            return time_str

        return None
