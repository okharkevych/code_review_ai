import os

import httpx
import pytest

from app.github_api import convert_to_api_url
from app.github_api import fetch_github_repo


async def check_github_token_validity() -> bool:
    github_token: str = os.getenv('GITHUB_TOKEN')
    headers: dict = {'Authorization': f'token {github_token}'}

    async with httpx.AsyncClient() as client:
        response: httpx.Response = await client.get(
            url='https://api.github.com/rate_limit',
            headers=headers
        )

    return response.status_code == 200


def test_convert_to_api_url(github_repo_url):
    expected_url: str = (
        'https://api.github.com/repos/okharkevych-api-test/api_target/contents'
    )
    actual_url: str = convert_to_api_url(github_repo_url)

    assert actual_url == expected_url


@pytest.mark.asyncio
async def test_github_token_is_valid():
    assert os.getenv('GITHUB_TOKEN') is not None

    is_valid: bool = await check_github_token_validity()
    assert is_valid


@pytest.mark.asyncio
async def test_fetch_github_repo_success_live(github_repo_url):
    repo_contents: dict = await fetch_github_repo(github_repo_url)

    assert len(repo_contents['file_structure']) == 3

    assert repo_contents['file_structure'][0] == '.gitignore'
    assert repo_contents['code_contents']['.gitignore'] == '.env\n'
