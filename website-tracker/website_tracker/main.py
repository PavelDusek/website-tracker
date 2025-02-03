# coding: utf-8
import requests
import toml
import difflib
import re
import os

from pathlib import Path
from icecream import ic
from rich import print


def remove_trash( text: str, params: dict) -> str:
    if 'regex' in params.keys():
        for r in site['regex']:
            #change the html text with regex so that only informative changes are tracked
            text = re.sub(r, "", text)
    return text

def differs(text: str, cache: Path) -> bool:
    store = False
    with open(cache) as f:
        old = f.read()
        if old != new:
            print(f"[green]{sitename}[/green] [red]changed!!![/red]")
            diff = difflib.ndiff(old, new)
            #ic(diff)
            #print(''.join(diff), end="")
            store = True
    return store

if __name__ == "__main__":
    toml_path = Path("sites.toml")
    cache_dir = Path("cache")
    sites = toml.load(toml_path)

    for sitename, site in sites.items():
        store = False
        path = cache_dir / Path(f"{sitename}.html")
        #ic(path)
        oldpath = cache_dir / Path(f"{sitename}_old.html")
        #ic(oldpath)
        req = requests.get(site['url'])
        new = req.text
        new = remove_trash(new, site)

        #ic(new)
        if path.exists():
            store = differs(text = new, cache = path)
        else:
            store = True

        #ic(store)
        if store:
            #storing html in a cache file
            if path.exists():
                os.rename(path, oldpath)
            with open(path, "w") as f:
                f.write(new)
