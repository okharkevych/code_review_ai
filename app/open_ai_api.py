import os

import httpx
from fastapi import HTTPException


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
