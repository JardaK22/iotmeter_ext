import aiohttp
import asyncio
from typing import Dict, Any


class IotMeterAPIError(Exception):
    """Custom exception for IotMeter API errors."""
    pass


async def fetch_data(session, url):
    """Fetch data from a URL."""
    async with session.get(url) as response:
        return await response.json()


class IoTMeterAPI:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port

    async def fetch_all_data(self, is_smartmodul=None) -> Dict[str, Any]:
        """Fetch data from all necessary URLs."""
        urls = [
            f"http://{self.ip_address}:{self.port}/updateSetting",
            f"http://{self.ip_address}:{self.port}/updateData",
        ]

        if is_smartmodul is not None:
            if is_smartmodul:
                urls.append(f"http://{self.ip_address}:{self.port}/updateRamSetting")
            else:
                urls.append(f"http://{self.ip_address}:{self.port}/updateEvse")

        async with aiohttp.ClientSession() as session:
            tasks = [fetch_data(session, url) for url in urls]
            results = await asyncio.gather(*tasks)

            data = results[0]
            data.update(results[1])
            if is_smartmodul is not None:
                data.update(results[2])

            return data
