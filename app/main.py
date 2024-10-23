import os

from dotenv import load_dotenv
from fastapi import FastAPI
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
