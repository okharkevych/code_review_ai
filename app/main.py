import os
from typing import Literal

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel, HttpUrl, constr

from app.github_api import fetch_github_repo
from app.open_ai_api import process_gpt_prompt, create_code_review_prompt

load_dotenv()

app = FastAPI()


class ReviewRequest(BaseModel):
    assignment_description: constr(min_length=1)
    github_repo_url: HttpUrl
    candidate_level: Literal['Junior', 'Middle', 'Senior']


@app.post(path='/review')
async def review_code(request: ReviewRequest) -> str:
    database_url: str = os.getenv(key='DATABASE_URL')
    if database_url:
        raise HTTPException(
            status_code=501,
            detail='Database functionality TBI.'
        )

    review: str = await perform_review(request)
    return review


async def perform_review(request: ReviewRequest) -> str:
    repo_contents: dict = await fetch_github_repo(
        request.github_repo_url
    )
    gpt_response: httpx.Response = await process_gpt_prompt(
        gpt_prompt=create_code_review_prompt(
            repo_contents,
            request.assignment_description,
            request.candidate_level
        )
    )
    gpt_response_json: dict = gpt_response.json()
    review: str = gpt_response_json['choices'][0]['message']['content']

    return review
