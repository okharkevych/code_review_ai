import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.github_api import fetch_github_repo

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
    repo_contents: list[dict] = await fetch_github_repo(
        request.github_repo_url
    )
    review: dict = await analyze_code(
        repo_contents,
        request.assignment_description,
        request.candidate_level
    )

    return review


async def analyze_code(
    repo_contents,
    assignment_description: str,
    candidate_level: str
) -> dict:
    gpt_prompt: str = create_gpt_prompt(
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

    return create_review_result(repo_contents, review)


def create_gpt_prompt(
    repo_contents,
    assignment_description: str,
    candidate_level: str
) -> str:
    raise NotImplementedError


def create_review_result(repo_contents, review: dict) -> dict:
    raise NotImplementedError
