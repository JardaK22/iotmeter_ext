"""Module for IoTMeter integration in Home Assistant."""

import asyncio
from datetime import timedelta
import logging

from homeassistant.helpers.translation import async_get_translations
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .iotmeter_api import IoTMeterAPI, IotMeterAPIError
from .const import DOMAIN
from .sensor import PowerSensor, CurrentSensor, VoltageSensor, PowerFactorSensor

SCAN_INTERVAL = 5

_LOGGER = logging.getLogger(__name__)

class IotMeterDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the IoTMeter API."""

    def __init__(self, hass, ip_address, port, entry):
        """Initialize the data update coordinator."""
        self.ip_address = ip_address
        self.port = port
        self.setting_read: bool = False
        self.async_add_sensor_entities = None
        self.entities = []
        self.number_of_evse: int = 0
        self.is_smartmodul = None
        self.api = IoTMeterAPI(ip_address, port)
        self._entry = entry  # uložíme si celý config entry pro předání entry_id

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    def update_ip_port(self, ip_address, port):
        """Update IP address and port."""
        self.ip_address = ip_address
        self.port = port
        self.api = IoTMeterAPI(ip_address, port)

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            data = await self.api.fetch_all_data(self.is_smartmodul)

            number_of_evse = data.get("NUMBER_OF_EVSE", 0)

            if "TYPE" in data:
                if data["TYPE"] == "2":
                    self.is_smartmodul = True
                elif "inp,EVSE1" in data:
                    self.is_smartmodul = False

            if not self.setting_read or (self.number_of_evse != number_of_evse and self.setting_read):
                self.number_of_evse = number_of_evse
                await self.remove_entities()

            if self.async_add_sensor_entities:
                self.setting_read = True
                await self.add_sensor_entities()

            return data

        except IotMeterAPIError as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err

    async def add_sensor_entities(self):
        """Add sensor entities to Home Assistant."""
        translations = await async_get_translations(
            self.hass,
            self.hass.config.language,
            "entity"
        )

        # Předáváme entry_id ze složky _entry pro tvorbu unikátního ID
        entry_id = self._entry.entry_id

        self.entities = [
            PowerSensor(self, entry_id, "P1", translations, "W", "P1"),
            PowerSensor(self, entry_id, "P2", translations, "W", "P2"),
            PowerSensor(self, entry_id, "P3", translations, "W", "P3"),
            PowerSensor(self, entry_id, "S1", translations, "W", "S1"),
            PowerSensor(self, entry_id, "S2", translations, "W", "S2"),
            PowerSensor(self, entry_id, "S3", translations, "W", "S3"),            
            CurrentSensor(self, entry_id, "I1", translations, "A", "I1"),
            CurrentSensor(self, entry_id, "I2", translations, "A", "I2"),
            CurrentSensor(self, entry_id, "I3", translations, "A", "I3"),            
            VoltageSensor(self, entry_id, "U1", translations, "V", "U1"),
            VoltageSensor(self, entry_id, "U2", translations, "V", "U2"),
            VoltageSensor(self, entry_id, "U3", translations, "V", "U3"),
            PowerFactorSensor(self, entry_id, "F1", translations, " ", "F1"),
            PowerFactorSensor(self, entry_id, "F2", translations, " ", "F2"),
            PowerFactorSensor(self, entry_id, "F3", translations, " ", "F3"),            
        ]

        # Přidáme entity do Home Assistanta
        self.async_add_sensor_entities(self.entities)

    async def remove_entities(self):
        """Remove entities."""
        if self.entities:
            _LOGGER.debug("Removing entities: %s", self.entities)
            for entity in self.entities:
                await entity.async_remove()
            self.entities = []
