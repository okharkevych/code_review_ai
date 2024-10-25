import base64
import os

import httpx
from fastapi import HTTPException


async def fetch_github_repo(github_repo_url: str) -> dict:
    api_url: str = convert_to_api_url(github_repo_url)
    github_token: str = os.getenv(key='GITHUB_TOKEN')
    headers: dict = {'Authorization': f'token {github_token}'}

    file_structure: list = []
    code_contents: dict = {}

    async def fetch_dir_contents(url: str, path_prefix: str = '') -> None:
        async with httpx.AsyncClient() as client:
            response: httpx.Response = await client.get(url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f'Failed to fetch repository at {url}.'
                )

            contents = response.json()

        for item in contents:
            item_path = f'{path_prefix}{item["name"]}'
            if item['type'] == 'dir':
                await fetch_dir_contents(
                    url=item['url'],
                    path_prefix=f'{item_path}/'
                )
            elif item['type'] == 'file':
                file_structure.append(item_path)
                file_content = await fetch_file_contents(file_url=item['url'])
                code_contents[item_path] = file_content

    async def fetch_file_contents(file_url: str) -> str:
        async with httpx.AsyncClient() as client:
            response: httpx.Response = await client.get(
                url=file_url,
                headers=headers
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f'Failed to fetch file at {file_url}.'
                )

            file_data = response.json()
            encoded_content: str = file_data.get('content', '')
            decoded_content: str = base64.b64decode(
                encoded_content
            ).decode('utf-8') if encoded_content else ''

            return decoded_content

    await fetch_dir_contents(url=api_url)

    return {
        'file_structure': file_structure,
        'code_contents': code_contents
    }


def convert_to_api_url(github_repo_url: str) -> str:
    url_parts: list = github_repo_url.rstrip('/').split('/')
    owner: str = url_parts[-2]
    repo: str = url_parts[-1]
    api_url: str = f'https://api.github.com/repos/{owner}/{repo}/contents'

    return api_url
