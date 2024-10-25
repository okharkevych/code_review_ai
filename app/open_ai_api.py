import os

import httpx
from fastapi import HTTPException


async def process_gpt_prompt(gpt_prompt: str) -> httpx.Response:
    openai_api_key: str = os.getenv(key='OPENAI_API_KEY')
    headers: dict = {'Authorization': f'Bearer {openai_api_key}'}

    gpt_model: str = os.getenv(key='GPT_MODEL', default='gpt-4-turbo')
    payload: dict = {
        'model': gpt_model,
        'messages': [{'role': 'user', 'content': gpt_prompt}]
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response: httpx.Response = await client.post(
            url='https://api.openai.com/v1/chat/completions',
            json=payload,
            headers=headers,
        )

    if response.status_code != 200:
        response_json: dict = response.json()
        error_message: str = response_json['error']['message']
        raise HTTPException(
            status_code=response.status_code,
            detail=error_message
        )

    return response


def create_code_review_prompt(
    repo_contents: dict,
    assignment_description: str,
    candidate_level: str
) -> str:
    file_structure: list = repo_contents['file_structure']
    code_contents: dict = repo_contents['code_contents']

    prompt = (
        f'You are reviewing code for a coding assignment. '
        f'The candidate is at a {candidate_level} level.\n\n'

        f'Assignment Description:\n{assignment_description}\n\n'

        f'The repository contains the following files:\n{file_structure}\n\n'

        f'The files code contents are as follows:\n{code_contents}\n\n'

        f'Analyze the project file structure and code based on the following '
        f'criteria:\n'
        f'- Code readability and structure\n'
        f'- Code quality and adherence to common software engineering best '
        f'practices\n'
        f'- Formatting consistency\n'
        f'- Efficiency and performance\n'
        f'- Proper error handling\n'
        f'- Correctness of the implementation in relation to the assignment '
        f'description\n'
        f'- Potential improvements and suggestions\n'
        f'- Any issues or downsides in the code\n\n'

        f'Provide your review in the following format:\n'
        f'Found Files:\neach repository file path on the new line\n\n'
        f'Downsides/Comments:\ndownsides found in the project and/or '
        f'general improvement suggestions based on the candidate level.\n\n'
        f'Rating:\ncode rating on the scale from 1 to 5, taking into account '
        f'the candidate\'s level\n\n'
        f'Conclusion:\nbrief summary and final thoughts on the candidate\'s'
        f'current strong and weak sides, as well as the candidate\'s potential'
    )

    return prompt
