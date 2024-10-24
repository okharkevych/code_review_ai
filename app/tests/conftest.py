import pytest
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def github_repo_url() -> str:
    return 'https://github.com/okharkevych-api-test/api_target'
