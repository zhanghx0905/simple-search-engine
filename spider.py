import json
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from email.utils import parsedate
from itertools import count
from urllib.parse import urljoin

from requests_html import HTMLSession

from utils import DATA_PATH, extract_keywords, load_json, save_json

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.41"
}
ROOT = "https://www.cse.ust.hk/~kwtleung/COMP4321/testpage.htm"


@dataclass
class Page:
    id: int
    url: str
    title: str
    body: str
    last_mod_time: str
    size: str
    keywords: list[tuple[str, int]] = field(default_factory=list)
    children_url: list[str] = field(default_factory=list)
    children_id: list[int] = field(default_factory=list)
    parents_url: list[str] = field(default_factory=list)
    parents_id: list[int] = field(default_factory=list)


def load_data(path: str):
    try:
        data = load_json(path)
        print(f"Loaded data at {path}")
        return [Page(**item) for item in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def is_not_newer(a: str, b: str):
    """return True if timestamp a is not newer than b"""
    da = parsedate(a)[:6]
    db = parsedate(b)[:6]
    return da <= db



def run_spider(path: str = DATA_PATH) -> tuple[list[Page], bool]:
    """
    Run spider and return a list of Page
    """
    session = HTMLSession()
    counter = count()
    db = load_data(path)
    visited: dict[str, Page] = {item.url: item for item in db}
    unvisited = [ROOT]
    updated = False
    while unvisited:
        url = unvisited.pop()
        r = session.get(url, headers=HEADERS)
        last_mod_time = r.headers.get("Last-Modified", r.headers["Date"])
        if url in visited and is_not_newer(last_mod_time, visited[url].last_mod_time):
            continue
        print(f"page {url} added")
        updated = True  # page updated, should commit to files

        title = r.html.find("head > title", first=True).text
        body = r.html.find("body", first=True).text
        keywords = extract_keywords(title, body)
        size = r.headers["Content-Length"]
        children = set(urljoin(url, l) for l in r.html.links)
        page = Page(
            id=next(counter),
            url=url,
            title=title,
            body=body,
            size=size,
            last_mod_time=last_mod_time,
            keywords=keywords,
            children_url=list(children),
        )
        visited[url] = page
        unvisited.extend(children)

    parents_url_set: dict[str, set[str]] = defaultdict(set)
    for purl, page in visited.items():
        for curl in page.children_url:
            child = visited[curl]
            page.children_id.append(child.id)
            parents_url_set[curl].add(purl)
    for curl, parents_url in parents_url_set.items():
        child = visited[curl]
        child.parents_url = list(parents_url)
        child.parents_id = [visited[purl].id for purl in parents_url]
    if updated:
        save_json(path, list(map(asdict, visited.values())), indent=2)
    return list(visited.values()), updated


if __name__ == "__main__":
    run_spider()
