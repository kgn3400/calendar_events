"""Sensor for Calendar events helper."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.frontend import storage as frontend_store
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, State
from homeassistant.helpers import entity_registry as er, issue_registry as ir, start
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .calendar_handler import CalendarHandler
from .const import (
    CONF_CALENDAR_ENTITY_IDS,
    CONF_MAX_EVENTS,
    CONF_USE_SUMMARY_AS_ENTITY_NAME,
    DOMAIN,
    DOMAIN_NAME,
    LOGGER,
    TRANSLATION_KEY,
    TRANSLATION_KEY_MISSING_ENTITY,
)


# ------------------------------------------------------
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sensor setup."""

    registry = er.async_get(hass)
    calendar_entities = er.async_validate_entity_ids(
        registry, entry.options[CONF_CALENDAR_ENTITY_IDS]
    )

    if len(calendar_entities) > 0:
        calendar_handler: CalendarHandler = CalendarHandler(hass, entry)

        tt: list[BaseCalendarEventSensor] = []

        tt.extend(
            CalendarEventsSensor(hass, entry, calendar_entities, calendar_handler, x)
            for x in range(int(entry.options.get(CONF_MAX_EVENTS, 5)))
        )

        entities: list = [
            CalendarEventSensor(hass, entry, calendar_entities, calendar_handler, tt),
            *tt,
        ]

        async_add_entities(entities)


# ------------------------------------------------------
# ------------------------------------------------------
class BaseCalendarEventSensor:
    """Base sensor class for calendar events."""

    # ------------------------------------------------------------------
    async def async_refresh(self) -> None:
        """Refresh."""


# ------------------------------------------------------
# ------------------------------------------------------
class CalendarEventSensor(SensorEntity, BaseCalendarEventSensor):
    """Sensor class for calendar events."""

    # ------------------------------------------------------
    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        calendar_entities: list[str],
        calendar_handler: CalendarHandler,
        events_sensors: list[BaseCalendarEventSensor],
    ) -> None:
        """Calendar events sensor."""

        self.hass: HomeAssistant = hass
        self.entry: ConfigEntry = entry
        self.calendar_entities: list[str] = calendar_entities
        self.calendar_handler: CalendarHandler = calendar_handler
        self.events_sensors: list[CalendarEventsSensor] = events_sensors

        self.translation_key = TRANSLATION_KEY
        self.language: str = "en"
        self.markdown_text: str = ""
        self.events_json: dict = {}

        self.coordinator: DataUpdateCoordinator = DataUpdateCoordinator(
            self.hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
            update_method=self.async_refresh,
        )

    # ------------------------------------------------------------------
    async def async_refresh(self) -> None:
        """Refresh."""
        self.calendar_handler.language = await self.async_get_language()
        await self.calendar_handler.get_process_calendar_events(self.calendar_entities)

        for event_sensor in self.events_sensors:
            await event_sensor.async_refresh()

        self.markdown_text = self.calendar_handler.create_markdown()
        self.events_json = self.calendar_handler.events

    # ------------------------------------------------------
    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass."""

    # ------------------------------------------------------
    async def async_update(self) -> None:
        """Update the entity. Only used by the generic entity update service."""
        await self.coordinator.async_request_refresh()

    # ------------------------------------------------------
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""

        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

        self.async_on_remove(start.async_at_started(self.hass, self.async_hass_started))

    # ------------------------------------------------------
    async def async_hass_started(self, _event: Event) -> None:
        """Hass started."""

        await self.calendar_handler.get_process_calendar_events(
            self.calendar_entities, True
        )
        self.async_schedule_update_ha_state()
        await self.coordinator.async_refresh()

    # ------------------------------------------------------
    @property
    def native_value(self) -> Any | None:
        """Native value.

        Returns:
            str | None: Native value

        """

        return len(self.calendar_handler.events)

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
        return self.entry.entry_id

    # ------------------------------------------------------
    @property
    def extra_state_attributes(self) -> dict:
        """Extra state attributes.

        Returns:
            dict: Extra state attributes

        """

        attr: dict = {}
        attr["events"] = self.events_json
        attr["markdown_text"] = self.markdown_text
        return attr

    # ------------------------------------------------------
    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    # ------------------------------------------------------
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    # ------------------------------------------------------------------
    def create_issue(
        self,
        translation_key: str,
        translation_placeholders: dict,
    ) -> None:
        """Create issue on."""

        ir.async_create_issue(
            self.hass,
            DOMAIN,
            DOMAIN_NAME + datetime.now().isoformat(),
            issue_domain=DOMAIN,
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key=translation_key,
            translation_placeholders=translation_placeholders,
        )

    # ------------------------------------------------------
    async def async_verify_calendar_entities_exist(self) -> bool:
        """Verify calendar entities exist."""
        res: bool = True

        for index, calendar_entity in reversed(list(enumerate(self.calendar_entities))):
            state: State | None = self.hass.states.get(calendar_entity)

            if state is None:
                self.create_issue(
                    calendar_entity,
                    TRANSLATION_KEY_MISSING_ENTITY,
                    {
                        "entity": calendar_entity,
                        "calendar_events_helper": self.entity_id,
                    },
                )
                del self.calendar_entities[index]
                res = False

        return res

    # ------------------------------------------------------
    async def async_get_language(self) -> str:
        """Get language."""

        self.language = self.hass.config.language

        owner = await self.hass.auth.async_get_owner()

        if owner is not None:
            _, owner_data = await frontend_store.async_user_store(self.hass, owner.id)

            if "language" in owner_data and "language" in owner_data["language"]:
                self.language = owner_data["language"]["language"]

        return self.language


# ------------------------------------------------------
# ------------------------------------------------------
class CalendarEventsSensor(SensorEntity, BaseCalendarEventSensor):
    """Sensor class for calendar events."""

    # ------------------------------------------------------
    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        calendar_entities: list[str],
        calendar_handler: CalendarHandler,
        event_num: int = 0,
    ) -> None:
        """Calendar events sensor."""

        self.hass: HomeAssistant = hass
        self.entry: ConfigEntry = entry
        self.calendar_entities: list[str] = calendar_entities
        self.calendar_handler: CalendarHandler = calendar_handler
        self.event_num = event_num

        self.translation_key = TRANSLATION_KEY

        self.formated_event: str = ""

    # ------------------------------------------------------------------
    async def async_refresh(self) -> None:
        """Refresh."""
        self.formated_event = await self.calendar_handler.async_format_event(
            self.event_num
        )

        if self.entity_id is not None:
            self.async_write_ha_state()

    # ------------------------------------------------------
    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass."""

    # ------------------------------------------------------
    async def async_update(self) -> None:
        """Update the entity. Only used by the generic entity update service."""
        # await self.coordinator.async_request_refresh()

    @property
    def native_value(self) -> Any | None:
        """Native value.

        Returns:
            str | None: Native value

        """

        return self.formated_event

    # ------------------------------------------------------
    @property
    def name(self) -> str:
        """Name.

        Returns:
            str: Name

        """

        if self.entry.options.get(
            CONF_USE_SUMMARY_AS_ENTITY_NAME, False
        ) and self.event_num < len(self.calendar_handler.events):
            return self.calendar_handler.events[self.event_num].summary

        return self.entry.title + "_event_" + str(self.event_num)

    # ------------------------------------------------------
    @property
    def unique_id(self) -> str:
        """Unique id.

        Returns:
            str: Unique  id

        """
        return self.entry.entry_id + "_event_" + str(self.event_num)

    # ------------------------------------------------------
    @property
    def extra_state_attributes(self) -> dict:
        """Extra state attributes.

        Returns:
            dict: Extra state attributes

        """

        attr: dict = {}

        return attr

    # ------------------------------------------------------
    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    # ------------------------------------------------------
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return True
