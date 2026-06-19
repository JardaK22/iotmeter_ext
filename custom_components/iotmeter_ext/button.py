"""Button entities for IoTMeter writable actions."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
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
    """Set up IoTMeter button entities."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    entry_id = config_entry.entry_id

    async_add_entities(
        [
            IoTMeterSettingButton(
                coordinator,
                entry_id,
                variable="btn,PHOTOVOLTAIC",
                value=1,
                name="Photovoltaic",
                icon="mdi:solar-power-variant",
            )
        ]
    )


class IoTMeterSettingButton(CoordinatorEntity, ButtonEntity):
    """Button that sends a fixed payload to updateSetting."""

    def __init__(
        self,
        coordinator,
        entry_id: str,
        variable: str,
        value: int,
        name: str,
        icon: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._variable = variable
        self._value = value
        self._attr_name = f"IOTMETER {name}"
        self._attr_icon = icon
        self._attr_unique_id = (
            f"{entry_id}_{DOMAIN}_{variable.lower().replace(',', '_').replace(' ', '_')}"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=f"IoTMeter {coordinator.ip_address or entry_id}",
            manufacturer="IoTMeter",
            configuration_url=f"http://{coordinator.ip_address}:{coordinator.port}",
        )

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.async_write_setting(self._variable, self._value)
