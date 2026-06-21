"""Module for IoTMeter sensor entities in Home Assistant."""

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def _decode_signed_16(raw_value: int | float) -> float:
    """Convert a raw 16-bit value to signed form."""
    return raw_value - 65536 if raw_value > 32767 else raw_value


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_sensor_entities: AddEntitiesCallback,
) -> None:
    """Set up the IoTMeter sensors from a config entry."""
    coordinator = hass.data[DOMAIN]["coordinator"]

    # Store entity creation function in coordinator so it can be called
    # after data refresh
    coordinator.async_add_sensor_entities = async_add_sensor_entities
    hass.data[DOMAIN]["platform"] = async_add_sensor_entities

    _LOGGER.debug("async_add_sensor_entities set in coordinator")
    await coordinator.async_request_refresh()


class TranslatableSensorEntity(CoordinatorEntity, SensorEntity):
    """A sensor entity that can be localized."""

    def __init__(
        self,
        coordinator,
        sensor_type,
        translations,
        unit_of_measurement,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type.replace(" ", "_").lower()
        self._translations = translations
        self._attr_name = self.get_localized_name()
        self._attr_native_unit_of_measurement = unit_of_measurement
        # Attach all entities to the same device using the config entry ID
        try:
            entry_id = getattr(coordinator, "_entry").entry_id
        except Exception:
            entry_id = None

        ip = getattr(coordinator, "ip_address", None)
        port = getattr(coordinator, "port", None)

        if entry_id:
            config_url = f"http://{ip}:{port}" if ip and port else None
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, entry_id)},
                name=(
                    f"IoTMeter {ip or entry_id}"
                ),
                manufacturer="IoTMeter",
                configuration_url=config_url,
            )

    def get_localized_name(self):
        """Return the localized name for the sensor."""
        # translations file provides keys under "entity.sensor.<key>"
        key = f"entity.sensor.{self._sensor_type}"
        localized_name = self._translations.get(key)
        return localized_name or self._sensor_type


class VoltageSensor(TranslatableSensorEntity):
    """Senzor pro napětí na jedné fázi (U1, U2, U3)."""

    def __init__(
        self,
        coordinator,
        entry_id,
        sensor_type,
        translations,
        unit_of_measurement,
        key,
    ):
        super().__init__(
            coordinator,
            sensor_type,
            translations,
            unit_of_measurement,
        )
        self.key = key
        self._entry_id = entry_id
        self._attr_name = f"{DOMAIN.upper()} {self.key.upper()}"

    @property
    def unique_id(self):
        return f"{self._entry_id}_{DOMAIN}_{self.key.lower()}"

    @property
    def state(self):
        """Vrací napětí dané fáze ve voltech."""
        value = self.coordinator.data.get(self.key)
        return round(float(value), 0) if value is not None else None

    @property
    def icon(self):
        return "mdi:flash"


class CurrentSensor(TranslatableSensorEntity):
    """Senzor pro proud na jedné fázi (U1, U2, U3)."""

    def __init__(
        self,
        coordinator,
        entry_id,
        sensor_type,
        translations,
        unit_of_measurement,
        key,
    ):
        super().__init__(
            coordinator,
            sensor_type,
            translations,
            unit_of_measurement,
        )
        self.key = key
        self._entry_id = entry_id
        self._attr_name = f"{DOMAIN.upper()} {self.key.upper()}"

    @property
    def unique_id(self):
        return f"{self._entry_id}_{DOMAIN}_{self.key.lower()}"

    @property
    def state(self):
        """Return the state of the sensor."""
        raw_value = self.coordinator.data.get(self.key)

        if raw_value is None:
            return None

        value = _decode_signed_16(raw_value) / 100
        return round(float(-value), 2)

    @property
    def icon(self):
        return "mdi:flash"


class PowerSensor(TranslatableSensorEntity):
    """Representation of the total power sensor."""

    def __init__(
        self,
        coordinator,
        entry_id,
        sensor_type,
        translations,
        unit_of_measurement,
        key,
    ):
        """Initialize the total power sensor."""
        super().__init__(
            coordinator,
            sensor_type,
            translations,
            unit_of_measurement,
        )
        self.key = key
        self._entry_id = entry_id
        self._attr_name = f"{DOMAIN.upper()} {self.key.upper()}"
        self.total_power: float = 0
        self._attr_suggested_display_precision = 0

    @property
    def unique_id(self):
        return f"{self._entry_id}_{DOMAIN}_{self.key.lower()}"

    @property
    def state(self):
        """Return the state of the sensor."""
        raw_value = self.coordinator.data.get(self.key)

        if raw_value is None:
            return None

        value = _decode_signed_16(raw_value)
        return round(float(-value), 0)

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:home-lightning-bolt"


class PowerFactorSensor(TranslatableSensorEntity):
    """Senzor pro účiník na jedné fázi (U1, U2, U3)."""

    def __init__(
        self,
        coordinator,
        entry_id,
        sensor_type,
        translations,
        unit_of_measurement,
        key,
    ):
        super().__init__(
            coordinator,
            sensor_type,
            translations,
            unit_of_measurement,
        )
        self.key = key
        self._entry_id = entry_id
        self._attr_name = f"{DOMAIN.upper()} {self.key.upper()}"

    @property
    def unique_id(self):
        return f"{self._entry_id}_{DOMAIN}_{self.key.lower()}"

    @property
    def state(self):
        """Vrací účiník dané fáze."""
        value = self.coordinator.data.get(self.key)
        return round(float(value), 0) if value is not None else None

    @property
    def icon(self):
        return "mdi:flash"


# ==================== NOVÉ EVSE SENZORY ====================

class EVSEStateSensor(TranslatableSensorEntity):
    """Senzor pro stav EVSE nabíječky."""

    STATE_MAP = {
        0: "Stav_0",
        1: "Odpojeno",
        2: "Zapojeno",
        3: "Nabíjí",
        4: "Stav_4",
        5: "Stav_5",
    }

    def __init__(
        self,
        coordinator,
        entry_id,
        sensor_type,
        translations,
        evse_index=0,
    ):
        super().__init__(coordinator, sensor_type, translations, None)
        self._entry_id = entry_id
        self._evse_index = evse_index
        self._attr_name = f"{DOMAIN.upper()} EVSE {evse_index} State"

    @property
    def unique_id(self):
        return f"{self._entry_id}_{DOMAIN}_evse_{self._evse_index}_state"

    @property
    def state(self):
        """Vrací textový stav EVSE."""
        ev_state_array = self.coordinator.data.get("EV_STATE", [])
        if ev_state_array and len(ev_state_array) > self._evse_index:
            state_value = ev_state_array[self._evse_index]
            return self.STATE_MAP.get(state_value, f"Unknown_{state_value}")
        return None

    @property
    def icon(self):
        return "mdi:ev-station"


class EVSECurrentSensor(TranslatableSensorEntity):
    """Senzor pro proud EVSE nabíječky."""

    def __init__(
        self,
        coordinator,
        entry_id,
        sensor_type,
        translations,
        key,
        evse_index=0,
    ):
        super().__init__(
            coordinator,
            sensor_type,
            translations,
            "A",
        )
        self.key = key
        self._entry_id = entry_id
        self._evse_index = evse_index
        display = key.replace("_", " ").title()
        self._attr_name = (
            f"{DOMAIN.upper()} EVSE {evse_index} {display}"
        )

    @property
    def unique_id(self):
        return (
            f"{self._entry_id}_{DOMAIN}_evse_"
            f"{self._evse_index}_{self.key.lower()}"
        )

    @property
    def state(self):
        """Vrací proud EVSE v ampérech."""
        current_array = self.coordinator.data.get(self.key, [])
        if current_array and len(current_array) > self._evse_index:
            return current_array[self._evse_index]
        return None

    @property
    def icon(self):
        return "mdi:current-ac"


class EVSEErrorSensor(TranslatableSensorEntity):
    """Senzor pro chybu komunikace EVSE."""

    ERROR_MAP = {
        0: "OK",
        1: "Error_1",
        2: "Error_2",
        3: "Error_3",
        4: "Error_4",
        5: "Error_5",
    }

    def __init__(
        self,
        coordinator,
        entry_id,
        sensor_type,
        translations,
        evse_index=0,
    ):
        super().__init__(coordinator, sensor_type, translations, None)
        self._entry_id = entry_id
        self._evse_index = evse_index
        self._attr_name = f"{DOMAIN.upper()} EVSE {evse_index} Comm Error"

    @property
    def unique_id(self):
        return f"{self._entry_id}_{DOMAIN}_evse_{self._evse_index}_comm_error"

    @property
    def state(self):
        """Vrací stav chyby komunikace."""
        error_array = self.coordinator.data.get("EV_COMM_ERR", [])
        if error_array and len(error_array) > self._evse_index:
            error_value = error_array[self._evse_index]
            return self.ERROR_MAP.get(error_value, f"Error_{error_value}")
        return None

    @property
    def icon(self):
        error_array = self.coordinator.data.get("EV_COMM_ERR", [])
        if error_array and len(error_array) > self._evse_index:
            if error_array[self._evse_index] == 0:
                return "mdi:check-circle"
            return "mdi:alert-circle"
        return "mdi:help-circle"
