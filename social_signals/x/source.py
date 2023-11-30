import requests
import json

class XSource:
    TWEET_COLUMNS = [
        "tweet_id",
        "tweet_created_at",
        "tweet_text",
        "tweet_public_metrics",
        "author_id",
        "author_description",
        "author_username",
        "author_description",
        "author_created_at",
        "author_public_metrics"        
    ]

    def __init__(
        self,
        *,
        x_bearer_token: str
    ):
        """
        Constructor for the XSource class.

        Parameters:
        - x_bearer_token: The bearer token for the X API.
        """
        self.x_bearer_token =x_bearer_token
    

    def bearer_oauth(self, r):
        """
        Method required by bearer token authentication.
        """

        r.headers["Authorization"] = f"Bearer {self.x_bearer_token}"
        r.headers["User-Agent"] = "v2RecentSearchPython"
        return r


    def search(self, search_term: str, start_time: str, n_results: int = 10) -> list[str]:
        """
        Get recent tweets based on a search term.

        Parameters:
        - search_term: The search term to use for the X API query.
        - start_date: The start date for the X API query.
        - n_results: The maximum number of results to return (default is 10).

        Returns:
        A list of recent tweets related to the search term.
        """
        search_url = "https://api.twitter.com/2/tweets/search/recent"

        query_params = {
            'query': f'{search_term}', 
            'start_time': start_time, 
            'max_results': n_results,
            'tweet.fields': 'created_at,author_id,text,public_metrics',
            'expansions': 'author_id',
            'user.fields': 'id,name,username,description,created_at,public_metrics'
        }

        response = requests.get(search_url, auth=self.bearer_oauth, params=query_params)

        print(response.status_code)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        
        return response.json()