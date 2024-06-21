"""Config flow for Calendar events integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.selector import (
    BooleanSelector,
    LanguageSelector,
    LanguageSelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_CALENDAR_ENTITY_IDS,
    CONF_DAYS_AHEAD,
    CONF_FORMAT_LANUAGE,
    CONF_MAX_EVENTS,
    CONF_MD_HEADER_TEMPLATE,
    CONF_MD_ITEM_TEMPLATE,
    CONF_REMOVE_RECURRING_EVENTS,
    CONF_SHOW_END_DATE,
    CONF_SHOW_EVENT_AS_TIME_TO,
    CONF_SHOW_SUMMARY,
    CONF_USE_SUMMARY_AS_ENTITY_NAME,
    DOMAIN,
)

# ------------------------------------------------------------------
default_md_header_template = (
    "### <font color= dodgerblue> <ha-icon icon='mdi:calendar-blank-outline'></ha-icon></font>  Kalenderbegivenheder <br>",
)
default_md_item_template = "- <font color= dodgerblue> <ha-icon icon='mdi:calendar-clock-outline'></ha-icon></font> __{{ summary }}__ <br>_{{ formatted_event_time }}_<br>"


# ------------------------------------------------------------------
async def _validate_input(
    hass: HomeAssistant,
    user_input: dict[str, Any],
    errors: dict[str, str],
) -> bool:
    """Validate the user input allows us to connect."""
    if CONF_CALENDAR_ENTITY_IDS not in user_input:
        errors[CONF_CALENDAR_ENTITY_IDS] = "missing_selection"
        return False

    if len(user_input[CONF_CALENDAR_ENTITY_IDS]) == 0:
        errors[CONF_CALENDAR_ENTITY_IDS] = "missing_selection"
        return False

    return True


# ------------------------------------------------------------------
async def _validate_input_format(
    hass: HomeAssistant,
    user_input: dict[str, Any],
    errors: dict[str, str],
) -> bool:
    """Validate the user input allows us to connect."""

    return True


# ------------------------------------------------------------------
async def _create_form(
    hass: HomeAssistant,
    user_input: dict[str, Any] | None = None,
    step: str = "",
) -> vol.Schema:
    """Create a form for step/option."""

    if user_input is None:
        user_input = {}

    CONFIG_NAME = {
        vol.Required(
            CONF_NAME,
            default=user_input.get(CONF_NAME, ""),
        ): selector.TextSelector(),
    }

    CONFIG_OPTIONS = {
        vol.Required(
            CONF_DAYS_AHEAD,
            default=user_input.get(CONF_DAYS_AHEAD, 15),
        ): NumberSelector(
            NumberSelectorConfig(
                min=1,
                max=999,
                step="any",
                mode=NumberSelectorMode.BOX,
            )
        ),
        vol.Required(
            CONF_MAX_EVENTS,
            default=user_input.get(CONF_MAX_EVENTS, 5),
        ): NumberSelector(
            NumberSelectorConfig(
                min=1,
                max=20,
                step="any",
                mode=NumberSelectorMode.BOX,
            )
        ),
        vol.Required(
            CONF_REMOVE_RECURRING_EVENTS,
            default=user_input.get(CONF_REMOVE_RECURRING_EVENTS, True),
        ): BooleanSelector(),
    }

    CONFIG_OPTIONS_ENTITIES = {
        vol.Required(
            CONF_CALENDAR_ENTITY_IDS,
            default=user_input.get(CONF_CALENDAR_ENTITY_IDS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="calendar", multiple=True),
        ),
    }

    CONFIG_OPTIONS_FORMAT = {
        vol.Required(
            CONF_SHOW_EVENT_AS_TIME_TO,
            default=user_input.get(CONF_SHOW_EVENT_AS_TIME_TO, False),
        ): BooleanSelector(),
        vol.Required(
            CONF_SHOW_END_DATE,
            default=user_input.get(CONF_SHOW_END_DATE, False),
        ): BooleanSelector(),
        vol.Required(
            CONF_SHOW_SUMMARY,
            default=user_input.get(CONF_SHOW_SUMMARY, True),
        ): BooleanSelector(),
        vol.Required(
            CONF_USE_SUMMARY_AS_ENTITY_NAME,
            default=user_input.get(CONF_USE_SUMMARY_AS_ENTITY_NAME, False),
        ): BooleanSelector(),
        vol.Required(
            CONF_FORMAT_LANUAGE,
            default=user_input.get(CONF_FORMAT_LANUAGE, hass.config.language),
        ): LanguageSelector(LanguageSelectorConfig()),
        vol.Optional(
            CONF_MD_HEADER_TEMPLATE,
            default=user_input.get(
                CONF_MD_HEADER_TEMPLATE,
                default_md_header_template,
            ),
        ): TextSelector(TextSelectorConfig(multiline=True, type=TextSelectorType.TEXT)),
        vol.Optional(
            CONF_MD_ITEM_TEMPLATE,
            default=user_input.get(
                CONF_MD_ITEM_TEMPLATE,
                default_md_item_template,
            ),
        ): TextSelector(TextSelectorConfig(multiline=True, type=TextSelectorType.TEXT)),
    }

    match step:
        case "init":
            return vol.Schema(
                {
                    **CONFIG_OPTIONS,
                    **CONFIG_OPTIONS_ENTITIES,
                }
            )
        case "user_format" | "init_format":
            return vol.Schema(
                {
                    **CONFIG_OPTIONS_FORMAT,
                }
            )

        case "user" | _:
            return vol.Schema(
                {
                    **CONFIG_NAME,
                    **CONFIG_OPTIONS,
                    **CONFIG_OPTIONS_ENTITIES,
                }
            )


# ------------------------------------------------------------------
# ------------------------------------------------------------------
class ConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1
    tmp_user_input: dict[str, Any] | None

    # ------------------------------------------------------------------
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if await _validate_input(self.hass, user_input, errors):
                self.tmp_user_input = user_input
                return self.async_show_form(
                    step_id="user_format",
                    data_schema=await _create_form(
                        self.hass,
                        user_input,
                        "user_format",
                    ),
                    errors=errors,
                    last_step=True,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=await _create_form(
                self.hass,
                user_input,
                "user",
            ),
            errors=errors,
            last_step=False,
        )

    # ------------------------------------------------------------------
    async def async_step_user_format(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial menu step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if await _validate_input_format(self.hass, user_input, errors):
                user_input |= self.tmp_user_input

                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                    options=user_input,
                )
        else:
            user_input = self.tmp_user_input.copy()

        return self.async_show_form(
            step_id="user_format",
            data_schema=await _create_form(
                self.hass,
                user_input,
                "user_format",
            ),
            errors=errors,
            last_step=True,
        )

    # ------------------------------------------------------------------
    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlow:
        """Get the options flow."""
        return OptionsFlowHandler(config_entry)


# ------------------------------------------------------------------
# ------------------------------------------------------------------
class OptionsFlowHandler(OptionsFlow):
    """Handle options flow."""

    def __init__(
        self,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize options flow."""

        self.config_entry = config_entry

        self.tmp_user_input: dict[str, Any] = self.config_entry.options.copy()

    # ------------------------------------------------------------------
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if await _validate_input(self, user_input, errors):
                self.tmp_user_input |= user_input

                return self.async_show_form(
                    step_id="init_format",
                    data_schema=await _create_form(
                        self.hass,
                        self.tmp_user_input,
                        "init_format",
                    ),
                    errors=errors,
                    last_step=True,
                )
        else:
            user_input = self.tmp_user_input.copy()

        return self.async_show_form(
            step_id="init",
            data_schema=await _create_form(
                self.hass,
                user_input,
                "init",
            ),
            errors=errors,
            last_step=False,
        )

    # ------------------------------------------------------------------
    async def async_step_init_format(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if await _validate_input_format(self, user_input, errors):
                self.tmp_user_input |= user_input

                return self.async_create_entry(
                    data=self.tmp_user_input,
                )
        else:
            user_input = self.tmp_user_input.copy()

        return self.async_show_form(
            step_id="init_format",
            data_schema=await _create_form(
                self.hass,
                user_input,
                "init_format",
            ),
            errors=errors,
            last_step=True,
        )
