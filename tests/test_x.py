import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from social_signals.x.source import XSource
import json


@pytest.fixture
def source():
    return XSource(x_bearer_token = None)


MOCK_RESPONSE = {
    "data": [
        {
            "author_id": "2503088778",
            "created_at": "2023-12-04T19:38:19.000Z",
            "edit_history_tweet_ids": [
                "1731759856669884702"
            ],
            "id": "1731759856669884702",
            "public_metrics": {
                "bookmark_count": 0,
                "impression_count": 60,
                "like_count": 1,
                "quote_count": 0,
                "reply_count": 0,
                "retweet_count": 0
            },
            "text": "Some of the protesters in Te Papaioea #Protest https://t.co/b5Di7V69uw"
        },
    ],
    "includes": {
        "users": [
            {
                "created_at": "2011-03-03T00:54:44.000Z",
                "description": "My heart belongs to Mick Jagger\u2661\u2661\u2661 #MickLuv #TeamJoePerry #JakeOwen #BK\ud83c\udfb8 #Tyler\ud83d\udc95 #FGL\ud83d\ude0e #empath AGAINST TV VIOLENCE!!! NOT on Twitter debate team!",
                "id": "259999787",
                "name": "dawna28",
                "public_metrics": {
                    "followers_count": 764,
                    "following_count": 1109,
                    "like_count": 40998,
                    "listed_count": 38,
                    "tweet_count": 100358
                },
                "username": "dawna28"
            },
            {
                "created_at": "2014-05-18T02:21:24.000Z",
                "description": "Ng\u0101ti Kahungunu, Husband, Father, Analyst, Gamer, Science Enthusiast, Fan Theorist \ud83c\uddf3\ud83c\uddff\ud83d\ude80",
                "id": "2503088778",
                "name": "Ash Gardiner",
                "public_metrics": {
                    "followers_count": 1942,
                    "following_count": 4947,
                    "like_count": 92058,
                    "listed_count": 14,
                    "tweet_count": 11403
                },
                "username": "WhiteStarPrime"
            }
        ]
    },
    "meta": {
        "newest_id": "1731765844638625829",
        "next_token": "b26v89c19zqg8o3fr5kdnfwu972a0gd1ykoztpznr2vlp",
        "oldest_id": "1731748114456059973",
        "result_count": 10
    }
}


@patch('requests.get')
def test_search(mock_get, source):
    # Set up the mock to return a predefined response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_RESPONSE
    mock_get.return_value = mock_response

    search_term = "protest"
    yesterday = datetime.now() - timedelta(days=1)
    start_time = yesterday.strftime('%Y-%m-%dT00:00:00Z')
    n_results = 5

    tweets = source.search(search_term, start_time, n_results)

    # Assertions
    mock_get.assert_called_once()
    assert tweets is not None
    assert len(tweets) == len(MOCK_RESPONSE['data'])