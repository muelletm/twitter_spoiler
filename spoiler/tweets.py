import time
from datetime import datetime
from typing import Iterable, List, Optional

import tweepy
from pydantic import BaseModel
from tqdm import tqdm


class Tweet(BaseModel):
    id: int
    created_at: datetime
    text: str


class Output(BaseModel):
    max_id: Optional[int]
    n_tweets_scraped: int = 0


def get_limits(limits):
    result = {}
    for res in limits["resources"].values():
        for m, limit in res.items():
            if limit["limit"] == limit["remaining"]:
                continue
            limit = limit.copy()
            limit["reset"] = datetime.fromtimestamp(limit["reset"])
            result[m] = limit
    return result


def _wait_for_rate_limit(api: tweepy.API):
    limits = api.rate_limit_status()
    for method, limit in get_limits(limits).items():
        now = datetime.now()
        seconds_to_wait = (limit["reset"] - now).total_seconds()
        if seconds_to_wait > 0:
            print(now, f"Waiting for method {method} ({seconds_to_wait}s)")
            time.sleep(seconds_to_wait)


def get_tweets(
    bearer_token: str, n_tweets: int, lang_code: str, output: Output
) -> Iterable[List[Tweet]]:

    auth = tweepy.OAuth2BearerHandler(bearer_token)
    api = tweepy.API(auth)

    n_tweets_scraped = 0

    with tqdm(total=n_tweets) as pbar:

        while n_tweets_scraped < n_tweets:

            # Get recent tweets containing "spoiler" but exclude retweets and quotes.
            try:
                results = api.search_tweets(
                    '"spoiler" -filter:retweets -filter:quote',
                    lang=lang_code,
                    include_entities=False,
                    result_type="recent",
                    count=100,
                    max_id=None if output.max_id is None else output.max_id - 1,
                )
            except tweepy.errors.TooManyRequests:
                _wait_for_rate_limit(api)
                continue

            if not results:
                break

            tweets = []
            for r in results:
                # These fields are set for quotes and retweets.
                # Since we filtered them we don't expect them to be present.
                assert "quoted_status" not in r._json
                assert "retweeted_status" not in r._json

                tweets.append(
                    Tweet(id=r.id, created_at=r.created_at, text=r.text)
                )

            # Next round we are going to look for tweets newer than the ones we get this time.
            output.max_id = min(t.id for t in tweets)
            yield tweets

            n_new_tweets = len(
                [t for t in tweets if "spoiler:" in t.text.lower()]
            )
            n_tweets_scraped += n_new_tweets

            output.n_tweets_scraped += len(tweets)

            pbar.update(n_new_tweets)
            pbar.set_description(f"last batch: {len(tweets)}")
