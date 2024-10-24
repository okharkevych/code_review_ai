import os

import httpx
import pytest
from dotenv import load_dotenv

from app.main import fetch_github_repo

load_dotenv()


async def check_github_token_validity() -> bool:
    github_token: str = os.getenv('GITHUB_TOKEN')
    headers: dict = {'Authorization': f'token {github_token}'}

    async with httpx.AsyncClient() as client:
        response: httpx.Response = await client.get(
            url='https://api.github.com/rate_limit',
            headers=headers
        )

    return response.status_code == 200


@pytest.mark.asyncio
async def test_check_github_token_validity():
    assert os.getenv('GITHUB_TOKEN') is not None

    is_valid: bool = await check_github_token_validity()
    assert is_valid


@pytest.mark.asyncio
async def test_fetch_github_repo_success_live(github_repo_url):
    repo_contents: list[dict] = await fetch_github_repo(github_repo_url)

    assert len(repo_contents) == 15
    assert repo_contents[0]['name'] == '.gitignore'