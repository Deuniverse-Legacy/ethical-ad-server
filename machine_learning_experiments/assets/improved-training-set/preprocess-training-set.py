"""
Build an ML training set from the training data in the specified YAML training set file.

The first time this is run, it can take a while.
It goes out and fetches data from the web.
For future runs, the URLs are cached.
"""
import argparse
import json
import sys
from collections import Counter

import requests
import urllib3
import yaml
from bs4 import BeautifulSoup
from requests_cache import CachedSession
from textacy import preprocessing


MAIN_CONTENT_SELECTORS = (
    "[role='main']",
    "main",
    "body",
)
REMOVE_CONTENT_SELECTORS = (
    "[role=navigation]",
    "[role=search]",
    ".headerlink",
    "nav",
    "footer",
    "div.header",
    # Django Packages specific
    "#myrotatingnav",
)
PREPROCESSOR = preprocessing.make_pipeline(
    preprocessing.normalize.unicode,
    preprocessing.remove.punctuation,
    preprocessing.normalize.whitespace,
    # Removes inline SVGs and *some* malformed HTML
    preprocessing.remove.html_tags,
)


def preprocess_html(html):
    """Preprocesses HTML into text for our model."""
    soup = BeautifulSoup(html, features="html.parser")

    for selector in REMOVE_CONTENT_SELECTORS:
        for nodes in soup.select(selector):
            nodes.decompose()

    for selector in MAIN_CONTENT_SELECTORS:
        results = soup.select(selector, limit=1)

        # If no results, go to the next selector
        # If results are found, use these and stop looking at the selectors
        if results:
            return PREPROCESSOR(results[0].get_text()).lower()

    return ""


def preprocess_training_set(infile):
    """Loop through our training set and fetch the actual URL contents."""
    # Setup the cache so we don't hammer these sites
    session = CachedSession("trainingset-urls-cache")

    new_training_set = []
    seen_urls = set()

    data = yaml.safe_load(infile)
    for dat in data:
        url = dat["url"].strip()

        if url in seen_urls:
            print(f"Duplicate url: {url}")
        seen_urls.add(url)

        try:
            resp = session.get(url, timeout=3)
        except (requests.exceptions.RequestException, urllib3.exceptions.HTTPError):
            print(f"Skipping URL {url} which returned an error...")
            continue

        if resp.ok:
            dat["text"] = preprocess_html(resp.content)
            new_training_set.append(dat)

    return new_training_set


def print_training_set_details(new_training_set):
    topic_counter = Counter()

    for dat in new_training_set:
        topics = dat["topics"]
        if not topics:
            topic_counter["notopic"] += 1
        for topic in topics:
            topic_counter[topic] += 1

    print("Training Set Details")
    print("=" * 80)
    print(f"Total Training Set Items:\t\t{len(new_training_set)}")

    for topic, count in topic_counter.most_common(10):
        print(f"Training Set Items for '{topic}':\t{count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Preprocess the specified YAML training set."
    )
    parser.add_argument(
        "infile",
        nargs="1",
        type=argparse.FileType("r"),
        help="Path to a YAML training set file",
    )

    parser.add_argument(
        "-o",
        "--outfile",
        nargs="?",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Path to write the processed training set.",
    )
    args = parser.parse_args()

    processed_training_set = preprocess_training_set(args.infile)
    print_training_set_details(processed_training_set)

    args.outfile.write(json.dumps(processed_training_set, indent=2))
