import aiohttp
import asyncio
import logging
from typing import Dict, Any, Optional

_LOGGER = logging.getLogger(__name__)


class IotMeterAPIError(Exception):
    """Custom exception for IotMeter API errors."""
    pass


async def fetch_data(session, url) -> Optional[Dict[str, Any]]:
    """Fetch data from a URL."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=4)) as response:
            if response.status == 200:
                return await response.json()
            else:
                _LOGGER.error(f"Error fetching {url}: HTTP {response.status}")
                return None
    except asyncio.TimeoutError:
        _LOGGER.error(f"Timeout fetching {url}")
        return None
    except aiohttp.ClientError as err:
        _LOGGER.error(f"Client error fetching {url}: {err}")
        return None
    except Exception as err:
        _LOGGER.error(f"Unexpected error fetching {url}: {err}")
        return None


class IoTMeterAPI:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port

    async def fetch_all_data(self, is_smartmodul=False) -> Dict[str, Any]:
        """Fetch data from all necessary URLs."""
        urls = [
            f"http://{self.ip_address}:{self.port}/updateSetting",
            f"http://{self.ip_address}:{self.port}/updateData",
        ]

        if is_smartmodul:
            urls.append(f"http://{self.ip_address}:{self.port}/updateRamSetting")
        else:
            urls.append(f"http://{self.ip_address}:{self.port}/updateEvse")

        async with aiohttp.ClientSession() as session:
            tasks = [fetch_data(session, url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Zkontrolujeme, zda jsou výsledky validní
            data = {}
            
            if results[0] and isinstance(results[0], dict):
                data.update(results[0])
            else:
                _LOGGER.error("Failed to fetch updateSetting data")
                raise IotMeterAPIError("Failed to fetch updateSetting data")
            
            if results[1] and isinstance(results[1], dict):
                data.update(results[1])
            else:
                _LOGGER.error("Failed to fetch updateData")
                raise IotMeterAPIError("Failed to fetch updateData")
            
            # Třetí endpoint je volitelný (EVSE nebo RamSetting)
            if len(results) > 2 and results[2] and isinstance(results[2], dict):
                data.update(results[2])
            elif len(results) > 2:
                _LOGGER.warning(f"Failed to fetch {'updateRamSetting' if is_smartmodul else 'updateEvse'}, continuing with partial data")

            return data