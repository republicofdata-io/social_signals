import pytest
from social_signals.wikipedia.source import WikipediaSource


@pytest.fixture
def source():
    return WikipediaSource()


def test_search(source):
    search_term = "python"
    n_pages = 5

    page_names = source.search(search_term, n_pages)

    assert len(page_names) > 0
    assert all(isinstance(page_name, str) for page_name in page_names)


def test_get_wikipedia_page_data(source):
    page_name = "Python (programming language)"

    source.get_wikipedia_page_data(page_name)

    assert not source.data.empty
    assert len(source.data) == 1
    assert list(source.data.columns) == WikipediaSource.WIKIPEDIA_COLUMNS
    assert all(source.data.iloc[0].notnull())


def test_get_related_wikipedia_pages_data(source):
    search_term = "python"
    n_pages = 5

    source.get_related_wikipedia_pages_data(search_term, n_pages)

    assert not source.data.empty
    assert list(source.data.columns) == WikipediaSource.WIKIPEDIA_COLUMNS
