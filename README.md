# twitter_spoiler

Spoiler detection on twitter

# Installation

```bash
conda create -n spoiler python=3.8
conda activate spoiler
```

# Usage

```bash
export BEARER_TOKEN="..."
python -m spoiler.cli es --n-tweets=100
```