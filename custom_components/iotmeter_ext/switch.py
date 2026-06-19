"""Switch entities for IoTMeter writable settings."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
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
	"""Set up IoTMeter switch entities."""
	coordinator = hass.data[DOMAIN]["coordinator"]
	entry_id = config_entry.entry_id

	entities = [
		IoTMeterSettingSwitch(
			coordinator,
			entry_id,
			"sw,ENABLE CHARGING",
			"Enable Charging",
			"mdi:ev-station",
		),
		IoTMeterSettingSwitch(
			coordinator,
			entry_id,
			"sw,ENABLE BALANCING",
			"Enable Balancing",
			"mdi:scale-balance",
		),
	]
	async_add_entities(entities)


class IoTMeterSettingSwitch(CoordinatorEntity, SwitchEntity):
	"""Writable switch backed by updateSetting."""

	def __init__(
		self,
		coordinator,
		entry_id: str,
		variable: str,
		name: str,
		icon: str,
	) -> None:
		super().__init__(coordinator)
		self._entry_id = entry_id
		self._variable = variable
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

	@property
	def is_on(self) -> bool:
		"""Return switch state from coordinator data."""
		value = self.coordinator.data.get(self._variable)
		return str(value) in {"1", "true", "True"}

	async def async_turn_on(self, **kwargs) -> None:
		"""Turn switch on."""
		await self.coordinator.async_write_setting(self._variable, 1)

	async def async_turn_off(self, **kwargs) -> None:
		"""Turn switch off."""
		await self.coordinator.async_write_setting(self._variable, 0)
