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
            IoTMeterMappedSelect(
                coordinator,
                entry_id,
                variable="chargeMode",
                name="Charge Mode",
                options={
                    "0": "EcoMode",
                    "1": "FastMode",
                },
                icon="mdi:car-electric",
            ),
            IoTMeterMappedSelect(
                coordinator,
                entry_id,
                variable="btn,PHOTOVOLTAIC",
                name="Photovoltaic",
                options={
                    "0": "Off",
                    "1": "1phase",
                    "2": "3phase",
                },
                icon="mdi:solar-power-variant",
            ),
        ]
    )


class IoTMeterMappedSelect(CoordinatorEntity, SelectEntity):
    """Select entity that maps displayed options to IoTMeter values."""

    def __init__(
        self,
        coordinator,
        entry_id: str,
        variable: str,
        name: str,
        options: dict[str, str],
        icon: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._variable = variable
        self._value_to_option = options
        self._option_to_value = {display: value for value, display in options.items()}
        self._attr_name = f"IOTMETER {name}"
        self._attr_icon = icon
        self._attr_options = list(options.values())
        self._attr_unique_id = (
            f"{entry_id}_{DOMAIN}_{variable.lower().replace(',', '_').replace(' ', '_')}"
        )
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

        return self._value_to_option.get(str(value))

    async def async_select_option(self, option: str) -> None:
        value = self._option_to_value.get(option)
        if value is None:
            return
        await self.coordinator.async_write_setting(self._variable, int(value))
