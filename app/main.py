import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

app = FastAPI()


class ReviewRequest(BaseModel):
    assignment_description: str
    github_repo_url: str
    candidate_level: str


@app.post(path='/review')
async def review_code(request: ReviewRequest) -> dict:
    database_url: str = os.getenv(key='DATABASE_URL')
    if database_url:
        return {'message': 'Database functionality TBI.'}

    review_result: dict = await perform_review(request)
    return review_result


async def perform_review(request: ReviewRequest) -> dict:
    repo_contents: dict = await fetch_github_repo(request.github_repo_url)
    review: dict = await analyze_code(
        repo_contents,
        request.assignment_description,
        request.candidate_level
    )

    return review


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


async def analyze_code(
    repo_contents,
    assignment_description: str,
    candidate_level: str
) -> dict:
    gpt_prompt: str = _create_gpt_prompt(
        repo_contents, assignment_description, candidate_level
    )

    openai_api_key: str = os.getenv('OPENAI_API_KEY')
    headers: dict = {'Authorization': f'Bearer {openai_api_key}'}
    gpt_model: str = 'gpt-4-turbo'

    async with httpx.AsyncClient() as client:
        response: httpx.Response = await client.post(
            url='https://api.openai.com/v1/chat/completions',
            headers=headers,
            json={
                'model': gpt_model,
                'messages': [{'role': 'user', 'content': gpt_prompt}],
            }
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail='OpenAI API request failed.'
        )

    review: dict = response.json()

    return _create_review_result(repo_contents, review)


def _create_gpt_prompt(
    repo_contents,
    assignment_description: str,
    candidate_level: str
) -> str:
    raise NotImplementedError


def _create_review_result(repo_contents, review: dict) -> dict:
    raise NotImplementedError
