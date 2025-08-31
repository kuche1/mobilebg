#! /usr/bin/env python3

from argparse import ArgumentParser
import requests
from bs4 import BeautifulSoup # pacman -S python-beautifulsoup4 # OR: pacman -S python-beautifulsoup4 python-cchardet python-chardet python-lxml python-html5lib
from dataclasses import dataclass
import requests_cache
from pathlib import Path

MOBILE_PREFIX = 'https://www.mobile.bg/'
URL = MOBILE_PREFIX + 'obiavi/avtomobili-dzhipove/namira-se-v-balgariya/p-{page_num}?price={price_min}&price1={price_max}&sort=6&nup=014&pictonly=1'
# `sort=6` - sort by newest
# `pictonly=1` - only show if picture is available

URL_PROTO = URL.split('//')[0]

BS_PARSER = 'html.parser'

NET_CACHE_DURATION_SEC = 60 * 60 * 24
NET_CACHE_LOC = str(Path(__file__).parent / "cache")

##########
########## class
##########

@dataclass
class Car:
    link_mobile: str
    link_autodata: str

    title: str
    fuel_consumption_urban: float # in liters
    fuel_consumption_highway: float # in liters

    @classmethod
    def new(cls, link_mobile: str, link_autodata: str, title: str) -> "Car":
        # print()
        # print(f'dbg: {link_mobile=}')
        # print(f'dbg: {link_autodata=}')

        autodata_html = net_req(link_autodata)
        soup = BeautifulSoup(autodata_html, BS_PARSER)

        fuel_consumption_urban = extract_fuel_consumption(soup, 'Разход на гориво - градско')
        fuel_consumption_highway = extract_fuel_consumption(soup, 'Разход на гориво - извънградско')
        if (fuel_consumption_urban is None) or (fuel_consumption_highway is None):
            print(f'WARNING: could not extract fuel consumption for: {link_mobile}')
            fuel_consumption_urban = float('inf')
            fuel_consumption_highway = float('inf')

        return cls(link_mobile, link_autodata, title, fuel_consumption_urban, fuel_consumption_highway)

##########
########## network
##########

# TODO: actually cache this (at least for a couple of hours) (maybe use MCT ? btw MCT I think needs to be reworked to exclude that hashing shit, it also needs some safety atomic operations)
def net_req(url: str) -> str:
    response = requests.get(url)

    if url.startswith(MOBILE_PREFIX):
        response.encoding = "cp1251" # otherwise we get gibberish

    assert response.ok
    return response.text

##########
########## html extract
##########

def extract_fuel_consumption(soup: BeautifulSoup, prefix: str) -> float | None:
    elem = soup.find('td', string=prefix)
    if elem is None:
        return None
    fuel_consumption = elem.parent.text

    fuel_consumption = fuel_consumption.replace('\n', ' ').replace('\t', ' ')
    while '  ' in fuel_consumption:
        fuel_consumption = fuel_consumption.replace('  ', ' ')
    fuel_consumption = fuel_consumption.strip()

    tmp = prefix + ' '
    assert fuel_consumption.startswith(tmp)
    fuel_consumption = fuel_consumption.removeprefix(tmp)

    tmp = ' Литра/100 км'
    assert fuel_consumption.endswith(tmp)
    fuel_consumption = fuel_consumption.removesuffix(tmp)

    if ' 'in fuel_consumption:
        part1, part2 = fuel_consumption.split(' ')
        
        part1 = float(part1)

        assert part2.startswith('(')
        part2 = part2[1:]

        assert part2.endswith(')')
        part2 = part2[:-1]

        part2 = float(part2)

        fuel_consumption = max(part1, part2)

    fuel_consumption = float(fuel_consumption)

    return fuel_consumption

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

        elem_params = soup.find('div', class_='borderBox carParams')
        # TODO: fill whatever's important

        elem_link_autodata = elem_params.find('div', class_='autodata24')
        link_autodata = elem_link_autodata.find('a').get('href')

        cars.append(Car.new(link, link_autodata, title))

    return cars

##########
########## main
##########

def main() -> None:
    requests_cache.install_cache(NET_CACHE_LOC, expire_after=NET_CACHE_DURATION_SEC)

    car_links = extract_car_links_from_website(number_of_pages_to_extract=1)
    cars = extract_cars_data_from_links(car_links)
    breakpoint()

def parse_cmdline() -> None:
    parser = ArgumentParser("Extract car data")
    _args = parser.parse_args()
    main()

if __name__ == '__main__':
    parse_cmdline()
