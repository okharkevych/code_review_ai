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
