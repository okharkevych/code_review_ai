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


@app.post('/review')
async def review_code(request: ReviewRequest):
    database_url: str = os.getenv('DATABASE_URL')
    if database_url:
        return {'message': 'Database functionality TBI.'}

    review_result = await perform_review(request)
    return review_result


async def perform_review(request: ReviewRequest):
    repo_contents = await fetch_github_repo(request.github_repo_url)
    review = await analyze_code(
        repo_contents,
        request.assignment_description,
        request.candidate_level
    )

    return review


async def fetch_github_repo(github_repo_url: str):
    headers = {'Authorization': f'token {os.getenv("GITHUB_TOKEN")}'}
    response = await httpx.get(github_repo_url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail='Failed to fetch repository.'
        )

    return response.json()


async def analyze_code(
    repo_contents,
    assignment_description: str,
    candidate_level: str
):
    gpt_prompt: str = _create_gpt_prompt(
        repo_contents, assignment_description, candidate_level
    )

    openai_api_key: str = os.getenv('OPENAI_API_KEY')
    headers = {'Authorization': f'Bearer {openai_api_key}'}
    response = await httpx.post(
        url='https://api.openai.com/v1/chat/completions',
        headers=headers,
        json={
            'model': 'gpt-4-turbo',
            'messages': [{'role': 'user', 'content': gpt_prompt}],
        }
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail='OpenAI API request failed.'
        )

    review = response.json()

    return _create_review_result(repo_contents, review)


def _create_gpt_prompt(
    repo_contents,
    assignment_description: str,
    candidate_level: str
) -> str:
    raise NotImplementedError


def _create_review_result(repo_contents, review: dict) -> dict:
    raise NotImplementedError
