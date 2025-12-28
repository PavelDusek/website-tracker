#!/usr/bin/env python3
# coding: utf-8

"""
Tracks changes on a list of websites.
Needs sites.toml file.
"""

import re
import os
import logging
from pathlib import Path

import httpx
import toml
import rich
from bs4 import BeautifulSoup


def remove_trash(text: str, params: dict) -> str:
    """Change the html text with regex so that only informative changes are tracked."""

    if "regex" in params.keys():
        for r in params["regex"]:
            # change the html text with regex so that only informative changes are tracked
            text = re.sub(r, "", text)
    return text


def differs(text: str, cache: Path, sitename: str, url: str) -> bool:
    """Tests if the text differs from the cached versions."""

    texts_differ = False
    with open(cache, encoding="utf-8") as f:
        old = f.read()
        # compare texts ignoring non-printable characters
        old = old.replace(" ", "").replace("\r", "").replace("\n", "")
        text = text.replace(" ", "").replace("\r", "").replace("\n", "")
        if old != text:
            # difference = find_difference(old, text)
            logging.debug(f"{sitename} and cache differs")
            logging.debug(text)
            logging.debug(old)
            rich.print(f"[green]{sitename}[/green] [red]changed!!![/red]")
            rich.print(f"[blue]{url}[/blue]")
            texts_differ = True
    return texts_differ


def find_difference(old: str, new: str) -> list:
    """Finds difference between two texts."""

    difference = []
    for o, n in zip(old, new):
        if o != n:
            difference.append((o, n))
    return difference


def clean_text(text: str) -> str:
    """Removes whitespace characters."""

    clean = []
    for line in text.splitlines():
        if line := line.strip():
            clean.append(line.replace("\t", ""))
    return "\n".join(clean)


def get_site(url: str) -> str:
    """Performs http request and retrieves html."""

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }
    try:
        req = httpx.get(url, headers=headers)
        return req.text
    except httpx.ConnectError as e:
        logging.error(e)
        try:
            logging.warning("Trying to use http request without SSL verification.")
            req = httpx.get(url, verify=False)
            return req.text
        except httpx.ConnectError as e2:
            logging.error(e2)
            logging.error(f"Connection to {url} failed")
            return ""


if __name__ == "__main__":
    work_dir = Path(".")
    toml_path = work_dir / Path("sites.toml")
    cache_dir = work_dir / Path("cache")
    sites = toml.load(toml_path)
    logging.basicConfig(level=logging.WARNING)
    #logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.DEBUG)

    for sitename, site in sites.items():
        goto = site.get("goto", site["url"])
        rich.print(f"Checking [blue]{sitename}[/blue]...")
        store, new = False, ""
        path = cache_dir / Path(f"{sitename}.html")
        logging.debug(path)
        oldpath = cache_dir / Path(f"{sitename}_old.html")
        logging.debug(oldpath)

        new = get_site(site["url"])
        if site.get("strip_html", False):
            soup = BeautifulSoup(new, "html.parser")
            new = soup.find("body").get_text().strip()
            new = clean_text(new)
        new = remove_trash(new, site)
        logging.debug(new)

        if path.exists():
            store = differs(text=new, cache=path, sitename=sitename, url=goto)
        else:
            store = True

        logging.info(store)
        if store:
            logging.info("storing html in a cache file")
            if path.exists():
                os.rename(path, oldpath)
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
    input("")  # wait for any key to quit
