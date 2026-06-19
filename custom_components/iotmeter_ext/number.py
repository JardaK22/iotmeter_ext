"""Number entities for IoTMeter writable settings."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
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
    """Set up IoTMeter number entities."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    entry_id = config_entry.entry_id

    entities = [
        IoTMeterSettingNumber(
            coordinator,
            entry_id,
            variable="in,PV-GRID-ASSIST-A",
            name="PV Grid Assist",
            icon="mdi:solar-power",
            native_min=0,
            native_max=63,
            native_step=1,
        ),
        IoTMeterEvseCurrentNumber(
            coordinator,
            entry_id,
            read_key="ACTUAL_CONFIG_CURRENT",
            write_variable="inp,EVSE1",
            name="Actual Config Current",
            icon="mdi:current-dc",
            native_min=0,
            native_max=32,
            native_step=1,
        ),
        IoTMeterEvseCurrentNumber(
            coordinator,
            entry_id,
            read_key="ACTUAL_OUTPUT_CURRENT",
            write_variable="ACTUAL_OUTPUT_CURRENT",
            name="Actual Output Current",
            icon="mdi:transmission-tower",
            native_min=0,
            native_max=32,
            native_step=1,
        ),
    ]
    async_add_entities(entities)


class IoTMeterBaseNumber(CoordinatorEntity, NumberEntity):
    """Shared number behavior for IoTMeter writable values."""

    def __init__(
        self,
        coordinator,
        entry_id: str,
        key_for_unique_id: str,
        name: str,
        icon: str,
        native_min: float,
        native_max: float,
        native_step: float,
    ) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_name = f"IOTMETER {name}"
        self._attr_icon = icon
        self._attr_native_min_value = native_min
        self._attr_native_max_value = native_max
        self._attr_native_step = native_step
        self._attr_mode = NumberMode.BOX
        self._attr_unique_id = (
            f"{entry_id}_{DOMAIN}_{key_for_unique_id.lower().replace(',', '_').replace(' ', '_')}"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=f"IoTMeter {coordinator.ip_address or entry_id}",
            manufacturer="IoTMeter",
            configuration_url=f"http://{coordinator.ip_address}:{coordinator.port}",
        )


class IoTMeterSettingNumber(IoTMeterBaseNumber):
    """Number mapped to a direct updateSetting variable."""

    def __init__(
        self,
        coordinator,
        entry_id: str,
        variable: str,
        name: str,
        icon: str,
        native_min: float,
        native_max: float,
        native_step: float,
    ) -> None:
        super().__init__(
            coordinator,
            entry_id,
            key_for_unique_id=variable,
            name=name,
            icon=icon,
            native_min=native_min,
            native_max=native_max,
            native_step=native_step,
        )
        self._variable = variable

    @property
    def native_value(self):
        value = self.coordinator.data.get(self._variable)
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_write_setting(self._variable, int(round(value)))


class IoTMeterEvseCurrentNumber(IoTMeterBaseNumber):
    """Number using EVSE array value for reading and updateSetting for writing."""

    def __init__(
        self,
        coordinator,
        entry_id: str,
        read_key: str,
        write_variable: str,
        name: str,
        icon: str,
        native_min: float,
        native_max: float,
        native_step: float,
    ) -> None:
        super().__init__(
            coordinator,
            entry_id,
            key_for_unique_id=read_key,
            name=name,
            icon=icon,
            native_min=native_min,
            native_max=native_max,
            native_step=native_step,
        )
        self._read_key = read_key
        self._write_variable = write_variable

    @property
    def native_value(self):
        value = self.coordinator.data.get(self._read_key)
        if isinstance(value, list) and value:
            try:
                return float(value[0])
            except (TypeError, ValueError):
                return None

        fallback = self.coordinator.data.get("inp,EVSE1")
        try:
            return float(fallback) if fallback is not None else None
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_write_setting(
            self._write_variable,
            int(round(value)),
        )
