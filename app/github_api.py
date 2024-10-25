import os

import httpx
from fastapi import HTTPException


async def fetch_github_repo(github_repo_url: str) -> list[dict]:
    api_url: str = convert_to_api_url(github_repo_url)

    github_token: str = os.getenv('GITHUB_TOKEN')
    headers: dict = {'Authorization': f'token {github_token}'}

    async def fetch_dir_contents(url: str) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response: httpx.Response = await client.get(
                url,
                headers=headers
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail='Failed to fetch repository.'
                )

        contents = response.json()
        all_files = []

        for item in contents:
            if item['type'] == 'dir':
                subdirectory_contents = await fetch_dir_contents(item['url'])
                all_files.extend(subdirectory_contents)
            else:
                all_files.append(item)

        return all_files

    return await fetch_dir_contents(url=api_url)


def convert_to_api_url(github_repo_url: str) -> str:
    url_parts: list = github_repo_url.rstrip('/').split('/')
    owner: str = url_parts[-2]
    repo: str = url_parts[-1]
    api_url: str = f'https://api.github.com/repos/{owner}/{repo}/contents'

    return api_url
