import logging
from typing import Dict, NewType

import bs4
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# some addtional types defined
BS4ResultSet = NewType("BS4ResultSet", bs4.element.ResultSet)


def retrieve_record(record_url: str) -> str:
    """retrieve record from the url"""
    response = requests.get(record_url)
    response.raise_for_status()
    return response.text


def _parse_attrgroups(attrgroups: BS4ResultSet) -> Dict[str, str]:
    """parse attribute groups and return dict representing attributes"""
    attr_tags = []
    attributes = {}
    for group in attrgroups:
        attr_tags.extend(group.find_all("span"))
    for attr in attr_tags:
        key = attr.find(text=True, recursive=False)
        # sometimes key may be empty. Usually it is first one with search name.
        # will replace it with '_name'
        if key is None:
            key = "_name"
        # also will remove unnecessary symbols: spaces and ':'
        key = key.rstrip(" :")
        value = attr.b.text
        # build attributes dict
        attributes[key] = value
    return attributes


def parse_record(record: str) -> Dict[str, str]:
    """parse record using beautifulsoup4"""
    soup = BeautifulSoup(record, 'html.parser')

    raw = record
    title = soup.title.string
    text = soup.get_text()

    page_container = soup.find("section", class_="page-container")
    body = page_container.find("section", class_="body")

    display_date = body.header.find("p", id="display-date")
    post_date = display_date.time["datetime"]

    posting_title = body.find("h2", class_="postingtitle")
    postingtitletext = posting_title.find("span", class_="postingtitletext")
    titletextonly = postingtitletext.find("span", id="titletextonly").text
    price = postingtitletext.find("span", class_="price").text

    userbody = body.find("section", class_="userbody")

    thumbs = userbody.figure.find("div", id="thumbs")
    thumb_links = [link["href"] for link in thumbs.find_all("a")]

    map_and_attrs = userbody.find("div", class_="mapAndAttrs")

    mapbox = map_and_attrs.find("div", class_="mapbox")
    map = mapbox.find("div", id="map")
    map_attrs = map.attrs
    mapaddress = mapbox.find("div", class_="mapaddress").text

    attrgroups = map_and_attrs.find_all("p", class_="attrgroup")
    attributes = _parse_attrgroups(attrgroups)

    postingbody = userbody.find("section", id="postingbody")
    post_text = postingbody.get_text()

    notices = [notice.text for notice in userbody.find("ul", class_="notices").find_all("li")]

    result = {
        "raw": raw,
        "text": text,
        "title": title,
        "post_date": post_date,
        "titletextonly": titletextonly,
        "price": price,
        "thumb_links": thumb_links,
        "map": {
            "mapaddress": mapaddress,
            "map_attrs": map_attrs,
        },
        "attributes": attributes,
        "post_text": post_text,
        "noticies": notices
    }
    return result


def process_record(url: str) -> Dict[str, str]:
    r = retrieve_record(url)
    parsed_record = parse_record(r)
    parsed_record["url"] = url
    return parsed_record


if __name__ == "__main__":
    record_url = "https://sfbay.craigslist.org/sby/mcy/6299581569.html"

    print(process_record(record_url))
