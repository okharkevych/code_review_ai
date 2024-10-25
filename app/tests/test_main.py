import pytest
from httpx import Response

from app.main import perform_review, ReviewRequest


@pytest.mark.asyncio
async def test_perform_review(mocker):
    fake_repo_url: str = 'https://github.com/example/repo'
    fake_assignment_description: str = 'Create a script to greet user.'
    fake_candidate_level: str = 'Junior'
    fake_repo_contents: dict = {
        'file_structure': ['file1.py'],
        'code_contents': {'file1.py': 'print("Hello World")'}
    }
    fake_gpt_response_content: str = (
        'Looks good. Minor improvements suggested.'
    )

    request_data = ReviewRequest(
        assignment_description=fake_assignment_description,
        github_repo_url=fake_repo_url,
        candidate_level=fake_candidate_level
    )

    mock_fetch_repo = mocker.patch(
        'app.main.fetch_github_repo', return_value=fake_repo_contents
    )

    mock_response = mocker.Mock(spec=Response)
    mock_response.json.return_value = {
        'choices': [{'message': {'content': fake_gpt_response_content}}]
    }
    mock_response.status_code = 200
    mock_process_prompt = mocker.patch(
        'app.main.process_gpt_prompt', return_value=mock_response
    )

    review = await perform_review(request_data)

    assert review == fake_gpt_response_content
    mock_fetch_repo.assert_called_once_with(github_repo_url=fake_repo_url)
    mock_process_prompt.assert_called_once()
