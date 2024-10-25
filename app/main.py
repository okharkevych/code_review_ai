import os

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from app.github_api import fetch_github_repo
from app.open_ai_api import analyze_code

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
