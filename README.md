# twitter_spoiler

Code for scraping spoiler examples from Twitter.

# Installation

```bash
conda create -n spoiler python=3.8
conda activate spoiler
```

# Usage

The following command attempts to get 100 Spanish tweets containing "spoiler:".
To this end it will scrape tweets contianing "spoiler".
This will create outputs in `./data/tweets`.
This requires a [bearer token](https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens).

```bash
export BEARER_TOKEN="..."
python -m spoiler.cli tweets es --n-tweets=100
```

From these we can then extract a list of spoiler texts:

```bash
export BEARER_TOKEN="..."
python -m spoiler.cli preprocess
```
