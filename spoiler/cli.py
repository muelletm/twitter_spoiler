import itertools
import json
import os
from pathlib import Path
from typing import Iterable
from uuid import uuid4

import typer

from spoiler.preprocess import get_spoiler_text, normalize
from spoiler.tweets import Output, Tweet, get_tweets

app = typer.Typer()


def _iterate_data(data_path: Path) -> Iterable[Tweet]:
    for path in data_path.glob("*.jsonl"):
        with path.open("tr") as reader:
            for line in reader:
                tweet = Tweet(**json.loads(line))
                yield tweet


@app.command()
def tweets(
    lang: str, n_tweets: int = 100, data_path: Path = Path("data", "tweets")
):
    output = Output(max_id=None)
    for tweet in _iterate_data(data_path):
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
            path = data_path.joinpath(str(uuid4())).with_suffix(".jsonl")
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("tw") as writer:
                for t in tweets:
                    writer.write(t.json())
                    writer.write("\n")
    finally:
        print(f"Last id: {output.max_id}")
        print(f"Tweets scraped: {output.n_tweets_scraped}")


@app.command()
def preprocess(data_path: Path = Path("data", "tweets")):
    with data_path.joinpath("spoilers.txt").open("tw") as writer:
        for tweet in itertools.islice(_iterate_data(data_path), 1_000_000):
            text = tweet.text
            text = normalize(text)
            for spoiler_text in get_spoiler_text(text):
                writer.write(spoiler_text)
                writer.write("\n")


if __name__ == "__main__":
    app()
