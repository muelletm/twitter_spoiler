import json
import os
from pathlib import Path
from uuid import uuid4

import typer

from spoiler.tweets import Output, Tweet, get_tweets

app = typer.Typer()


@app.command()
def tweets(lang: str, n_tweets: int = 100):

    output = Output(max_id=None)
    for path in Path("data", "tweets").glob("*.jsonl"):
        with path.open("tr") as reader:
            for line in reader:
                tweet = Tweet(**json.loads(line))
                output.max_id = (
                    min(output.max_id, tweet.id)
                    if output.max_id is not None
                    else tweet.id
                )
                output.n_tweets_scraped += 1

    print(f"Last id: {output.max_id}")
    print(f"Tweets scraped: {output.n_tweets_scraped}")

    bearer_token = os.environ["BEARER_TOKEN"]
    try:
        for tweets in get_tweets(
            bearer_token, n_tweets, lang_code=lang, output=output
        ):
            path = Path("data", "tweets", str(uuid4())).with_suffix(".jsonl")
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("tw") as writer:
                for t in tweets:
                    writer.write(t.json())
                    writer.write("\n")
    finally:
        print(f"Last id: {output.max_id}")
        print(f"Tweets scraped: {output.n_tweets_scraped}")


if __name__ == "__main__":
    app()
