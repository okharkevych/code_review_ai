from app.github_api import convert_to_api_url


def test_convert_to_api_url(github_repo_url):
    expected_url: str = (
        'https://api.github.com/repos/okharkevych-api-test/api_target/contents'
    )
    actual_url: str = convert_to_api_url(github_repo_url)

    assert actual_url == expected_url
