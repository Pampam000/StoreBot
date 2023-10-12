import aiohttp


async def get_location_list(location: str) -> dict:
    async with aiohttp.ClientSession() as session:
        response = await session.get(
            f'https://iqpr.cc/api/v1/locality_list/{location}')

        response = await response.json()
        return response


async def get_locations_with_parent(location: str,
                                    parent_id: str):

    async with aiohttp.ClientSession() as session:
        response = await session.get(
            f'https://iqpr.cc/api/v1/locality_list_by_parent/{location}/{parent_id}')

        return await response.json()