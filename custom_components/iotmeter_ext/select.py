"""Select entities for IoTMeter writable settings."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up IoTMeter select entities."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    entry_id = config_entry.entry_id

    async_add_entities(
        [
            IoTMeterChargeModeSelect(
                coordinator,
                entry_id,
                "chargeMode",
                "Charge Mode",
            )
        ]
    )


class IoTMeterChargeModeSelect(CoordinatorEntity, SelectEntity):
    """Select entity for chargeMode setting."""

    _attr_options = ["0", "1", "2", "3"]

    def __init__(
        self,
        coordinator,
        entry_id: str,
        variable: str,
        name: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._variable = variable
        self._attr_name = f"IOTMETER {name}"
        self._attr_icon = "mdi:car-electric"
        self._attr_unique_id = f"{entry_id}_{DOMAIN}_{variable.lower()}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=f"IoTMeter {coordinator.ip_address or entry_id}",
            manufacturer="IoTMeter",
            configuration_url=f"http://{coordinator.ip_address}:{coordinator.port}",
        )

    @property
    def current_option(self) -> str | None:
        value = self.coordinator.data.get(self._variable)
        if value is None:
            return None

        text = str(value)
        if text in self.options:
            return text
        return self.options[0]

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_write_setting(self._variable, int(option))
