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

p = argparse.ArgumentParser()
p.add_argument("title")
p.add_argument("-d", help="directory to save photos", default=".")
args = p.parse_args()
photos_path = Path(args.d) / "photos"
photos_path.mkdir(exist_ok=True, parents=True)

session = requests.Session()

title = args.title
base_url =  "https://farmhill-learning.org/gallery/" + quote(title)

html = session.get(base_url).text
soup = BeautifulSoup(html, "html.parser")
images = soup.select(".webpage-content img")

counter = 1

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

::: {style="display: grid;grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));grid-gap: 1em;"}

{% for photo in photos %}
![]({{photo}}){group="my-gallery"}
{% endfor %}
:::

"""

def make_index(path, title, photos):
    t = jinja2.Template(template)
    text = t.render(title=title, photos=photos)
    path.write_text(text)
    print("created", path)

def download(url):
    global counter
    url = urljoin(base_url, url)
    filename = url.split("/")[-1]
    suffix = Path(filename).suffix.lower()
    path = photos_path / f"{counter:03d}{suffix}"
    counter += 1
    print(f"{url} -> {path}")

    r  = session.get(url)
    path.write_bytes(r.content)

for img in images:
    download(img['src'])

photos = [f"photos/{i:03d}.jpg" for i in range(1, counter)]
path = photos_path.parent / "index.qmd"
make_index(path, title, photos)