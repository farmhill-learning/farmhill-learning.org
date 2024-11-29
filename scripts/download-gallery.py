"""Script to download a gallary from Farmhill website running on Frappe.

The takes the title of the gallery as argument and downloads all the photos
in it and saves them as a gallery in the new website.

USAGE:

    python scripts/download-gallery.py -d gallery/golden-showers-2023 "Golden showers!"

"""
from bs4 import BeautifulSoup
import argparse
import requests
from pathlib import Path
from urllib.parse import urljoin, unquote, quote
import jinja2
from urllib.parse import urljoin
import re

p = argparse.ArgumentParser()
p.add_argument("title")
p.add_argument("-d", help="directory to save photos", default=".")

api_key_filename = Path(__file__).parent.parent / "frappe-api-key.txt"
api_key = open(api_key_filename).read().strip()

template = """\
---
title: {{title}}
bread-crumbs: true
filters:
    - lightbox
lightbox: auto
# date: Oct 2024
date-format: "MMM YYYY"
image: photos/001.jpg
---

{{ description }}

::: {style="display: grid;grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));grid-gap: 1em;"}

{% for photo in photos %}
![]({{photo}}){group="my-gallery"}
{% endfor %}
:::

"""

class GalleryDownloader:
    def __init__(self, title, path):
        self.title = title
        self.path = path
        self.counter = 1

        self.base_url =  "https://farmhill-learning.frappe.cloud/gallery/" + quote(title)

        self.photos_path = Path(path) / "photos"
        self.photos_path.mkdir(exist_ok=True, parents=True)

        self.session = requests.Session()

    def make_index(self, path, title, description, photos):
        t = jinja2.Template(template)
        text = t.render(title=title, description=description, photos=photos)
        path.write_text(text)
        print("created", path)

    def download_url(self, url):
        url = urljoin(self.base_url, url)
        filename = url.split("/")[-1]
        suffix = Path(filename).suffix.lower()
        path = self.photos_path / f"{self.counter:03d}{suffix}"
        self.counter += 1
        print(f"{url} -> {path}")

        r  = self.session.get(url)
        path.write_bytes(r.content)

    def download(self):
        html = self.session.get(self.base_url).text
        soup = BeautifulSoup(html, "html.parser")
        images = soup.select(".webpage-content img")

        for img in images:
            self.download_url(img['src'])

        photos = [f"photos/{i:03d}.jpg" for i in range(1, self.counter)]
        path = self.photos_path.parent / "index.qmd"
        self.make_index(path, self.title, "", photos)

class NewDownloader:
    def __init__(self):
        self.api = API(api_key)

    def download_all(self, path):
        docs = self.api.get_docs("Gallery")
        for doc in docs:
            self.download_gallery(path, doc)

    def download_photo(self, url, gallery_dir, index):
        print("download_photo", url, repr(gallery_dir), index)
        url = urljoin(BASE_URL, url)
        filename = url.split("/")[-1]
        suffix = Path(filename).suffix.lower()
        filename = f"photos/{index:03d}{suffix}"
        path = gallery_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"{url} -> {path}")
        r  = self.api.session.get(url)
        path.write_bytes(r.content)
        return filename

    def download_gallery(self, path, doc):
        print(doc)
        title = doc['name']
        description = doc['description'] or ""
        date = doc['creation'][:4]
        name = re.sub(r"[^a-z]+", "-", title.lower()).strip("-") + "-" + date
        p = Path(path) / name
        photo_links = [v for k, v in doc.items() if k.startswith("image_") and v]

        photos = [
            self.download_photo(url, p, i)
            for i, url in enumerate(photo_links, start=1)]

        index_path = p / "index.qmd"
        self.make_index(index_path, title, description, photos)

    def make_index(self, path, title, description, photos):
        t = jinja2.Template(template)
        text = t.render(title=title, description=description, photos=photos)
        path.write_text(text)
        print("created", path)

BASE_URL = "https://farmhill-learning.frappe.cloud/"

class API:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {"Authorization": f"Token {api_key}"}
        self.session = requests.Session()

    def get(self, url, **kwargs):
        url = urljoin(BASE_URL, url)
        kwargs['headers'] = self.headers
        return self.session.get(url, **kwargs)

    def whoami(self):
        return self.get("/api/method/frappe.auth.get_logged_user").json()

    def get_docs(self, doctype, limit=100):
        params = {"fields": '["*"]', "limit_page_length": limit}
        d = api.get(f"/api/resource/{doctype}", params=params).json()
        return d['data']

api = API(api_key=api_key)

def main():
    # args = p.parse_args()
    # d = GalleryDownloader(args.title, args.d)
    # d.download()
    d = NewDownloader()
    d.download_all("gallery2")

if __name__ == "__main__":
    main()
