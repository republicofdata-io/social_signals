import wikipedia
from pandas import DataFrame
from datetime import timedelta


class WikipediaSource:
    WIKIPEDIA_COLUMNS = [
        "pageid",
        "title",
        "url",
        "categories",
        "links",
        "references",
        "content",
    ]

    def __init__(
        self,
        *,
        lang: str = "en",
        rate_limit: bool = True,
        min_wait=timedelta(milliseconds=50),
    ):
        """
        Constructor for the WikipediaSource class.

        Parameters:
        - lang: Language code for Wikipedia language edition (default is English 'en').
        - rate_limit: Whether to apply rate limiting to Wikipedia API requests (default is True).
        - min_wait: Minimum time to wait between Wikipedia API requests (default is 50 milliseconds).
        """
        # Initialize an empty DataFrame to store Wikipedia page data
        self.data = DataFrame(columns=self.WIKIPEDIA_COLUMNS)
        # Configure rate limiting and language for Wikipedia API requests
        wikipedia.set_rate_limiting(rate_limit=rate_limit, min_wait=min_wait)
        wikipedia.set_lang(lang)

    def search(self, search_term: str, n_pages: int = 100) -> list[str]:
        """
        Search Wikipedia for page names related to a given search term.

        Parameters:
        - search_term: The search term to query on Wikipedia.
        - n_pages: The number of pages to retrieve (default is 100).

        Returns:
        A list of Wikipedia page names related to the search term.
        """
        # Perform a Wikipedia search and get a list of related page names
        search_results = wikipedia.search(search_term, results=n_pages)

        if len(search_results) == 0:
            print(
                f"0 search results found. Did you mean {wikipedia.suggest(search_term)}?"
            )
        elif (
            search_results[0].lower() == search_term.lower()
        ):  # Prevent ambiguous page name
            search_results = search_results[1:]

        return search_results

    def get_wikipedia_page_data(
        self, page_name: str, auto_suggest: bool = False, show_disambiguation_error=True
    ) -> None:
        """
        Retrieve data for a single Wikipedia page and add it to the DataFrame.

        Parameters:
        - page_name: The name of the Wikipedia page.
        - auto_suggest: Whether to automatically suggest alternative page names (default is False).
        - show_disambiguation_error: Whether to display disambiguation error messages (default is True).
        """
        try:
            page = wikipedia.page(page_name, auto_suggest=auto_suggest)

            # Extract data for each specified column and add it to the DataFrame
            page_data = []
            for col in self.WIKIPEDIA_COLUMNS:
                page_data.append(getattr(page, col))

            self.data.loc[len(self.data)] = page_data
        except wikipedia.exceptions.DisambiguationError as error:
            # Handle disambiguation errors (when the search term is ambiguous)
            print(
                f'Search term "{page_name}" is ambiguous and has multiple pages related to it. Change the search term to something more specific. Skipped.'
            )
            if show_disambiguation_error:
                print(error)

    def get_related_wikipedia_pages_data(self, search_term: str, n_pages: int) -> None:
        """
        Retrieve data from multiple related Wikipedia pages and add them to the DataFrame.

        Parameters:
        - search_term: The search term to query on Wikipedia.
        - n_pages: The number of related pages to retrieve and add to the DataFrame.
        """
        # Get a list of Wikipedia page names related to the search term
        related_pages = self.search(search_term, n_pages)
        
        # Retrieve and add data for each related Wikipedia page to the DataFrame
        for page in related_pages:
            self.get_wikipedia_page_data(page, show_disambiguation_error=False)
