import aiohttp
import asyncio
import json
import logging
from typing import Dict, Any, Optional

_LOGGER = logging.getLogger(__name__)


class IotMeterAPIError(Exception):
    """Custom exception for IotMeter API errors."""
    pass


async def fetch_data(
    session,
    url,
) -> Optional[Dict[str, Any]]:
    """Fetch data from a URL."""
    try:
        async with session.get(
            url,
            timeout=aiohttp.ClientTimeout(total=4),
        ) as response:
            if response.status == 200:
                return await response.json()

            _LOGGER.error(
                "Error fetching %s: HTTP %s",
                url,
                response.status,
            )
            return None
    except asyncio.TimeoutError:
        _LOGGER.error("Timeout fetching %s", url)
        return None
    except aiohttp.ClientError as err:
        _LOGGER.error("Client error fetching %s: %s", url, err)
        return None
    except Exception as err:
        _LOGGER.error("Unexpected error fetching %s: %s", url, err)
        return None


class IoTMeterAPI:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port

    async def fetch_all_data(
        self,
        is_smartmodul=False,
    ) -> Dict[str, Any]:
        """Fetch data from all necessary URLs."""
        base = f"http://{self.ip_address}:{self.port}"
        urls = [
            f"{base}/updateSetting",
            f"{base}/updateData",
        ]

        if is_smartmodul:
            urls.append(f"{base}/updateRamSetting")
        else:
            urls.append(f"{base}/updateEvse")

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
            if (
                len(results) > 2
                and results[2]
                and isinstance(results[2], dict)
            ):
                data.update(results[2])
            elif len(results) > 2:
                endpoint = (
                    "updateRamSetting"
                    if is_smartmodul
                    else "updateEvse"
                )
                _LOGGER.warning(
                    "Failed to fetch %s, continuing with partial data",
                    endpoint,
                )

            return data

    async def update_setting(self, variable: str, value: Any) -> Dict[str, Any]:
        """Write a setting value to IoTMeter updateSetting endpoint."""
        base = f"http://{self.ip_address}:{self.port}"
        url = f"{base}/updateSetting"
        payload = json.dumps({"variable": variable, "value": value})

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=headers,
                    data=payload,
                    timeout=aiohttp.ClientTimeout(total=4),
                ) as response:
                    if response.status != 200:
                        raise IotMeterAPIError(
                            f"Failed to update setting {variable}: HTTP {response.status}"
                        )

                    result = await response.json()
                    if not isinstance(result, dict):
                        raise IotMeterAPIError(
                            f"Unexpected response while updating {variable}"
                        )
                    return result
        except asyncio.TimeoutError as err:
            raise IotMeterAPIError(
                f"Timeout updating setting {variable}"
            ) from err
        except aiohttp.ClientError as err:
            raise IotMeterAPIError(
                f"Client error updating setting {variable}: {err}"
            ) from err
