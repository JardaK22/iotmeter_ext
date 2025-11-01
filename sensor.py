"""Module for IoTMeter sensor entities in Home Assistant."""

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_sensor_entities: AddEntitiesCallback,
) -> None:
    """Set up the IoTMeter sensors from a config entry."""
    coordinator = hass.data[DOMAIN]["coordinator"]

    # Store entity creation function in coordinator so it can be called after data refresh
    coordinator.async_add_sensor_entities = async_add_sensor_entities
    hass.data[DOMAIN]["platform"] = async_add_sensor_entities

    _LOGGER.debug("async_add_sensor_entities set in coordinator")
    await coordinator.async_request_refresh()


class TranslatableSensorEntity(CoordinatorEntity, SensorEntity):
    """A sensor entity that can be localized."""

    def __init__(self, coordinator, sensor_type, translations, unit_of_measurement) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type.replace(" ", "_").lower()
        self._translations = translations
        self._attr_name = self.get_localized_name()
        self._attr_native_unit_of_measurement = unit_of_measurement

    def get_localized_name(self):
        """Return the localized name for the sensor."""
        key = f"component.iotmeter.entity.sensor.{self._sensor_type}"
        localized_name = self._translations.get(key)
        return localized_name or self._sensor_type


class VoltageSensor(TranslatableSensorEntity):
    """Senzor pro napětí na jedné fázi (U1, U2, U3)."""

    def __init__(self, coordinator, entry_id, sensor_type, translations, unit_of_measurement, key):
        super().__init__(coordinator, sensor_type, translations, unit_of_measurement)
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

    def __init__(self, coordinator, entry_id, sensor_type, translations, unit_of_measurement, key):
        super().__init__(coordinator, sensor_type, translations, unit_of_measurement)
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
        
        if raw_value is not None:
            # Korekce záporných hodnot u signed 16-bitové hodnoty
            value = raw_value - 65535 if raw_value > 32767 else raw_value
        value = value / 100
        return round(float(value), 2) if value is not None else None

    @property
    def icon(self):
        return "mdi:flash"


class PowerSensor(TranslatableSensorEntity):
    """Representation of the total power sensor."""

    def __init__(self, coordinator, entry_id, sensor_type, translations, unit_of_measurement, key):
        """Initialize the total power sensor."""
        super().__init__(coordinator, sensor_type, translations, unit_of_measurement)
        self.key = key
        self._entry_id = entry_id
        self._attr_name = f"{DOMAIN.upper()} {self.key.upper()}"
        self.total_power: float = 0

    @property
    def unique_id(self):
        return f"{self._entry_id}_{DOMAIN}_{self.key.lower()}"

    @property
    def state(self):
        """Return the state of the sensor."""
        raw_value = self.coordinator.data.get(self.key)
        
        if raw_value is not None:
            # Korekce záporných hodnot u signed 16-bitové hodnoty
            value = raw_value - 65535 if raw_value > 32767 else raw_value

        return round(float(value), 0) if value is not None else None

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:home-lightning-bolt"

class PowerFactorSensor(TranslatableSensorEntity):
    """Senzor pro účiník na jedné fázi (U1, U2, U3)."""

    def __init__(self, coordinator, entry_id, sensor_type, translations, unit_of_measurement, key):
        super().__init__(coordinator, sensor_type, translations, unit_of_measurement)
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