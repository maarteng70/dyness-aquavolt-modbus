"""Config flow for Dyness Aquavolt Modbus integration."""
import asyncio
import logging
import socket

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.modbus import async_get_temporary_unit
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.translation import async_get_translations
from modbus_connection import ModbusTcpParams

from .const import (
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVALS,
    DEFAULT_UNIT_ID,
    DOMAIN,
    SUPPORTED_VERSIONS,
)
_LOGGER = logging.getLogger(__name__)

CONF_UNIT_ID = "unit_id"

SCHEMA_HOST_BASE = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_UNIT_ID, default=DEFAULT_UNIT_ID): vol.Coerce(int),
    }
)

SCHEMA_POLLING = vol.Schema(
    {
        vol.Required("high"): vol.All(vol.Coerce(int), vol.Clamp(min=1, max=3600)),
        vol.Required("medium"): vol.All(vol.Coerce(int), vol.Clamp(min=1, max=3600)),
        vol.Required("low"): vol.All(vol.Coerce(int), vol.Clamp(min=1, max=3600)),
    }
)


class DynessConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for the Dyness Aquavolt Modbus integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step where the user inputs connection details."""
        errors = {}

        language = self.context.get("language", "en")
        translations = await async_get_translations(
            self.hass,
            language,
            category="config",
            integrations=[DOMAIN]
        )

        if user_input is not None:
            host = user_input.get(CONF_HOST)
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            unit_id = user_input.get(CONF_UNIT_ID, DEFAULT_UNIT_ID)

            if not (1 <= port <= 65535):
                errors["base"] = "invalid_port"
            elif not (1 <= unit_id <= 255):
                errors["base"] = "invalid_unit_id"

            if errors:
                return self.async_show_form(
                    step_id="user",
                    data_schema=self.add_suggested_values_to_schema(
                        SCHEMA_HOST_BASE, user_input
                    ),
                    errors=errors,
                )

            try:
                socket.gethostbyname(host)
            except (socket.gaierror, TypeError):
                errors["base"] = "invalid_host"
            else:
                for entry in self._async_current_entries():
                    if (
                        entry.data.get(CONF_HOST) == host
                        and entry.data.get(CONF_PORT) == port
                        and entry.data.get(CONF_UNIT_ID) == unit_id
                    ):
                        return self.async_abort(reason="already_configured")

                errors["base"] = await async_test_modbus_connection(
                    self.hass, host, port, unit_id
                )

                if not errors["base"]:
                    title = translations.get(
                        "config.step.user.title", "Dyness Aquavolt Modbus"
                    )
                    data = {
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_UNIT_ID: unit_id,
                    }
                    return self.async_create_entry(title=title, data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                SCHEMA_HOST_BASE, user_input or {}
            ),
            errors=errors,
            description_placeholders={},
        )

    async def async_step_reauth(self, data=None):
        """Re-authentication step."""
        errors = {}
        language = self.context.get("language", self.hass.config.language)
        translations = await async_get_translations(
            self.hass, language, category="config", integrations=[DOMAIN]
        )

        if data is not None:
            entry = (
                self._async_current_entries()[0]
                if self._async_current_entries()
                else None
            )
            if entry:
                try:
                    new_data = dict(entry.data)
                    await self.hass.config_entries.async_update_entry(
                        entry, data=new_data
                    )
                    return self.async_create_entry(
                        title=entry.title or DOMAIN, data={}
                    )
                except Exception as exc:
                    _LOGGER.error("Failed to update config entry during reauth: %s", exc)
                    errors["base"] = "unknown"

        return self.async_show_form(
            step_id="reauth",
            data_schema=vol.Schema({}),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return DynessOptionsFlow(config_entry)


class DynessOptionsFlow(config_entries.OptionsFlow):
    """Handle Dyness Aquavolt Modbus options flow."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options flow by delegating to a menu step."""
        return await self.async_step_menu()

    async def async_step_menu(self, user_input=None):
        """Show the options menu."""
        return self.async_show_menu(
            step_id="menu",
            menu_options=["connection", "polling"],
        )

    async def async_step_polling(self, user_input=None):
        """Configure polling scan intervals."""
        errors = {}
        config = self._config_entry
        legacy_options = config.options or {}
        normalized_options = dict(legacy_options)
        if "high" not in normalized_options and "medium" in normalized_options:
            normalized_options["high"] = normalized_options["medium"]
        if "low" not in normalized_options and "very_low" in normalized_options:
            normalized_options["low"] = normalized_options["very_low"]

        defaults = {
            key: normalized_options.get(
                key, config.data.get(key, DEFAULT_SCAN_INTERVALS[key])
            )
            for key in ("high", "medium", "low")
        }

        lowest = min((user_input or defaults).values())

        if user_input is not None:
            coordinator = self.hass.data.get(DOMAIN, {}).get(config.entry_id)
            if coordinator:
                coordinator._update_scan_intervals(user_input)

            self.hass.config_entries.async_update_entry(
                config,
                options={
                    **{
                        key: value
                        for key, value in config.options.items()
                        if key not in {"medium", "very_low"}
                    },
                    **user_input,
                },
            )
            return await self.async_step_menu()

        return self.async_show_form(
            step_id="polling",
            data_schema=self.add_suggested_values_to_schema(
                SCHEMA_POLLING, defaults
            ),
            errors=errors,
            description_placeholders={"lowest": str(lowest)},
            last_step=True,
        )

    async def async_step_connection(self, user_input=None):
        """Configure host, port and unit id."""
        errors = {}
        config = self._config_entry
        defaults = {
            CONF_HOST: config.data.get(CONF_HOST, ""),
            CONF_PORT: config.data.get(CONF_PORT, DEFAULT_PORT),
            CONF_UNIT_ID: config.options.get(
                CONF_UNIT_ID, config.data.get(CONF_UNIT_ID, DEFAULT_UNIT_ID)
            ),
        }

        if user_input is not None:
            host = user_input.get(CONF_HOST)
            port = user_input.get(CONF_PORT)
            unit_id = user_input.get(CONF_UNIT_ID)

            if not (1 <= int(port) <= 65535):
                errors["base"] = "invalid_port"
            elif not (1 <= int(unit_id) <= 255):
                errors["base"] = "invalid_unit_id"

            if not errors:
                error = await async_test_modbus_connection(
                    self.hass, host, int(port), int(unit_id)
                )
                if error:
                    errors["base"] = error
                else:
                    new_data = dict(config.data)
                    new_data[CONF_HOST] = host
                    new_data[CONF_PORT] = int(port)
                    new_data[CONF_UNIT_ID] = int(unit_id)
                    self.hass.config_entries.async_update_entry(
                        config, data=new_data
                    )
                    self.hass.config_entries.async_schedule_reload(config.entry_id)
                    return await self.async_step_menu()

        return self.async_show_form(
            step_id="connection",
            data_schema=self.add_suggested_values_to_schema(
                SCHEMA_HOST_BASE, defaults
            ),
            errors=errors,
            last_step=True,
        )


async def async_test_modbus_connection(
    hass, host: str, port: int, unit_id: int = 1
):
    """Test Modbus connection."""
    _LOGGER.debug("Testing Modbus connection to %s:%d with unit %d", host, port, unit_id)
    try:
        async with async_get_temporary_unit(
            hass,
            ModbusTcpParams(host=host, port=int(port)),
            int(unit_id),
        ) as unit:
            result = await unit.read_holding_registers(address=170, count=1)
            if not result:
                _LOGGER.debug("No response when reading register for unit_id test")
                return "unit_id_no_response"
            _LOGGER.debug("Unit ID %d test succeeded", unit_id)
            return None
    except asyncio.TimeoutError:
        _LOGGER.debug("Timeout testing unit_id %d", unit_id)
        return "unit_id_no_response"
    except Exception as exc:
        _LOGGER.debug("Exception during Modbus connection test: %s", exc)
        return "cannot_connect"
