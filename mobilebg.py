#! /usr/bin/env python3

from argparse import ArgumentParser
import requests
from bs4 import BeautifulSoup # pacman -S python-beautifulsoup4 # OR: pacman -S python-beautifulsoup4 python-cchardet python-chardet python-lxml python-html5lib
from dataclasses import dataclass

URL = 'https://www.mobile.bg/obiavi/avtomobili-dzhipove/namira-se-v-balgariya/p-{page_num}?price={price_min}&price1={price_max}&sort=6&nup=014&pictonly=1'
# `sort=6` - sort by newest
# `pictonly=1` - only show if picture is available

URL_PROTO = URL.split('//')[0]

BS_PARSER = 'html.parser'

@dataclass(kw_only=True)
class Car:
    url: str
    title: str

# TODO: actually cache this (at least for a couple of hours) (maybe use MCT ? btw MCT I think needs to be reworked to exclude that hashing shit, it also needs some safety atomic operations)
def net_req(url: str) -> str:
    response = requests.get(url)
    response.encoding = "cp1251" # otherwise we get gibberish
    assert response.ok
    return response.text

def extract_car_links_from_website(*, number_of_pages_to_extract: int) -> list[str]:
    car_links = []

    for page_number in range(1, number_of_pages_to_extract+1):
        url = URL.format(page_num=page_number, price_min=2_000, price_max=6_000)
        response = net_req(url)
        soup = BeautifulSoup(response, BS_PARSER)

        for elem in soup.find_all("a", class_="title saveSlink"):
            href = elem.get('href')

            # 2025.08.31: this is currently the case - the urls start with `//` rather than `https://`
            if href.startswith('//'):
                href = URL_PROTO + href

            car_links.append(href)

    return car_links

def extract_cars_data_from_links(links: list[str]):
    cars = []

    for link in links:
        car_html = net_req(link)
        soup = BeautifulSoup(car_html, BS_PARSER)

        elem_title = soup.find('div', class_='obTitle')

        title = elem_title.text.strip()
        title = title.split(' Обява: ')[0]

        cars.append(Car(url=link, title=title))

    return cars

def main() -> None:
    car_links = extract_car_links_from_website(number_of_pages_to_extract=1)
    cars = extract_cars_data_from_links(car_links)
    breakpoint()

def parse_cmdline() -> None:
    parser = ArgumentParser("Extract car data")
    _args = parser.parse_args()
    main()

if __name__ == '__main__':
    parse_cmdline()
