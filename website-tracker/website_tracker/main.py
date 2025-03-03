# coding: utf-8
import requests
import toml
import re
import os

from pathlib import Path
from icecream import ic
from rich import print
from bs4 import BeautifulSoup

def remove_trash( text: str, params: dict) -> str:
    if 'regex' in params.keys():
        for r in site['regex']:
            #change the html text with regex so that only informative changes are tracked
            text = re.sub(r, "", text)
    return text

def differs(text: str, cache: Path, url: str) -> bool:
    store = False
    with open(cache) as f:
        old = f.read()
        if old != new:
            difference = find_difference(old, new)
            print(f"[green]{sitename}[/green] [red]changed!!![/red]")
            print(f"[blue]{url}[/blue]")
            #ic(difference)
            store = True
    return store

def find_difference( old: str, new: str) -> list:
    difference = []
    for o, n in zip(old, new):
        if o != n:
            difference.append( (o, n) )
    return difference

def clean_text(text: str) -> str:
    clean = []
    for line in text.splitlines():
        if line := line.strip():
            clean.append( line.replace("\t","") )
    return "\n".join(clean)

if __name__ == "__main__":
    work_dir = Path(".")
    toml_path = work_dir / Path("sites.toml")
    cache_dir = work_dir / Path("cache")
    sites = toml.load(toml_path)

    for sitename, site in sites.items():
        goto = site.get('goto', site['url'])
        print(f"Checking [blue]{sitename}[/blue]...")
        store = False
        path = cache_dir / Path(f"{sitename}.html")
        #ic(path)
        oldpath = cache_dir / Path(f"{sitename}_old.html")
        #ic(oldpath)
        try:
            req = requests.get(site['url'])
        except requests.exceptions.ConnectionError as e:
            ic(e)
            continue
        new = req.text
        if site.get('strip_html', False):
            soup = BeautifulSoup(new, "html.parser")
            new = soup.find("body").get_text().strip()
            new = clean_text(new)
        new = remove_trash(new, site)

        #ic(new)
        if path.exists():
            store = differs(text = new, cache = path, url = goto)
        else:
            store = True

        #ic(store)
        if store:
            #storing html in a cache file
            if path.exists():
                os.rename(path, oldpath)
            with open(path, "w") as f:
                f.write(new)
    input("") #wait for any key to quit
