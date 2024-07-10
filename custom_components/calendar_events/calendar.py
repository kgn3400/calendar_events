"""Calendars events."""

from __future__ import annotations

import datetime

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .calendar_handler import CalendarHandler
from .const import DOMAIN


# ------------------------------------------------------
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AffaldDK Waste calendard items based on a config entry."""

    async_add_entities([EventsCalendar(hass, config_entry)])


# ------------------------------------------------------
# ------------------------------------------------------
class EventsCalendar(CalendarEntity):
    """Define a events calendar."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize a Calendar events."""

        self.hass: HomeAssistant = hass
        self.entry: ConfigEntry = entry

        self.coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
            "coordinator"
        ]
        self.calendar_handler: CalendarHandler = hass.data[DOMAIN][entry.entry_id][
            "calendar_handler"
        ]

    # ------------------------------------------------------
    @property
    def name(self) -> str:
        """Name.

        Returns:
            str: Name

        """

        return self.entry.title

    # ------------------------------------------------------
    @property
    def unique_id(self) -> str:
        """Unique id.

        Returns:
            str: Unique  id

        """
        return self.entry.entry_id + "calendar"

    # ------------------------------------------------------
    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""

        if len(self.calendar_handler.events) == 0:
            return None

        event = self.calendar_handler.events[0]

        if event.all_day:
            return CalendarEvent(
                summary=event.summary,
                description=event.description,
                location=event.location,
                start=datetime.date.fromisoformat(event.start),
                end=datetime.date.fromisoformat(event.end),
            )

        return CalendarEvent(
            summary=event.summary,
            description=event.description,
            location=event.location,
            start=datetime.datetime.fromisoformat(event.start),
            end=datetime.datetime.fromisoformat(event.end),
        )

        return None

    # ------------------------------------------------------
    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""

        events: list[CalendarEvent] = []

        for tmp_event in self.calendar_handler.events:
            if start_date > datetime.datetime.fromisoformat(tmp_event.start).replace(
                tzinfo=start_date.tzinfo
            ):
                continue
            if end_date < datetime.datetime.fromisoformat(tmp_event.end).replace(
                tzinfo=start_date.tzinfo
            ):
                continue

            if tmp_event.all_day:
                events.append(
                    CalendarEvent(
                        summary=tmp_event.summary,
                        description=tmp_event.description,
                        location=tmp_event.location,
                        start=datetime.date.fromisoformat(tmp_event.start),
                        end=datetime.date.fromisoformat(tmp_event.end),
                    )
                )
            else:
                events.append(
                    CalendarEvent(
                        summary=tmp_event.summary,
                        description=tmp_event.description,
                        location=tmp_event.location,
                        start=datetime.datetime.fromisoformat(tmp_event.start).replace(
                            tzinfo=start_date.tzinfo
                        ),
                        end=datetime.datetime.fromisoformat(tmp_event.end).replace(
                            tzinfo=start_date.tzinfo
                        ),
                    )
                )
        return events

    # ------------------------------------------------------
    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
