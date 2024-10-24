import os

import httpx
import pytest


async def check_openai_key_validity() -> bool:
    openai_api_key: str = os.getenv('OPENAI_API_KEY')
    headers: dict = {'Authorization': f'Bearer {openai_api_key}'}

    async with httpx.AsyncClient() as client:
        response: httpx.Response = await client.get(
            url='https://api.openai.com/v1/models',
            headers=headers
        )

    return response.status_code == 200


@pytest.mark.asyncio
async def test_openai_api_key_is_valid():
    assert os.getenv('OPENAI_API_KEY') is not None

    is_valid: bool = await check_openai_key_validity()
    assert is_valid
