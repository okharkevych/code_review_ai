import os

import httpx
import pytest

from app.main import process_gpt_prompt


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


@pytest.mark.asyncio
async def test_process_gpt_prompt_reply_to_simple_prompt_received():
    response: httpx.Response = await process_gpt_prompt(
        gpt_prompt='This is a test prompt. Just reply "Yes".'
    )
    response_json: dict = response.json()
    gpt_reply_content: str = response_json['choices'][0]['message']['content']

    assert response.status_code == 200
    assert gpt_reply_content == 'Yes.'
