import requests
import pandas as pd

class XSource:
    TWEET_COLUMNS = [
        "tweet_id",
        "tweet_created_at",
        "tweet_text",
        "tweet_public_metrics",
        "author_id",
        "author_username",
        "author_description",
        "author_created_at",
        "author_public_metrics"        
    ]
    SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"

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

        query_params = {
            'query': f'{search_term}', 
            'start_time': start_time, 
            'max_results': n_results,
            'tweet.fields': 'created_at,author_id,text,public_metrics',
            'expansions': 'author_id',
            'user.fields': 'id,name,username,description,created_at,public_metrics'
        }

        response = requests.get(self.SEARCH_URL, auth=self.bearer_oauth, params=query_params)

        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        
        json_response = response.json()
        return self._parse_response_to_dataframe(json_response)
    

    def _parse_response_to_dataframe(self, json_response) -> pd.DataFrame:
        data = json_response.get('data', [])
        includes = json_response.get('includes', {}).get('users', [])

        # Create a dictionary for user data for easy lookup
        users_dict = {user['id']: user for user in includes}

        # Extract relevant data and construct a list of dictionaries
        rows = []
        for tweet in data:
            user = users_dict.get(tweet['author_id'], {})
            row = {
                'tweet_id': tweet['id'],
                'tweet_created_at': tweet['created_at'],
                'tweet_text': tweet['text'],
                'tweet_public_metrics': tweet['public_metrics'],
                'author_id': tweet['author_id'],
                'author_username': user.get('username', ''),
                'author_description': user.get('description', ''),
                'author_created_at': user.get('created_at', ''),
                'author_public_metrics': user.get('public_metrics', {})
            }
            rows.append(row)

        # Convert the list of dictionaries into a DataFrame
        df = pd.DataFrame(rows, columns=self.TWEET_COLUMNS)
        return df