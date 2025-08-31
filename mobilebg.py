#! /usr/bin/env python3

from argparse import ArgumentParser
import requests
from bs4 import BeautifulSoup # pacman -S python-beautifulsoup4 # OR: pacman -S python-beautifulsoup4 python-cchardet python-chardet python-lxml python-html5lib
from dataclasses import dataclass
import requests_cache
from pathlib import Path
from colorama import Fore, Style

NUMBER_OF_PAGES_TO_PARSE = 110
PRICE_MIN = 2_000
PRICE_MAX = 6_000

# TODO: double-check
BLACKLIST_BRAND = [
    'audi',
    'bmw',
]

BLACKLIST_FUEL_CONSUMPTION_URBAN = 10.0

# ebasi
# BRANDS_PREFIX_NAME = {
#     'audi ': 'audi',
#     'fiat ': 'fiat',
#     'mercedes-': 'mercedes',
#     'seat ': 'seat',
#     'chevrolet ': 'chevrolet',
#     'vw ': 'volkswagen',
#     'Hyundai ': 'Hyundai',
#     'Citroen ': 'Citroen',
#     'Toyota ': 'Toyota',
#     'Dacia ': 'Dacia',
#     'Opel ': 'Opel',
#     'Mazda ': 'Mazda',
#     'BMW ': 'BMW',
#     'Honda ': 'Honda',
#     'Aixam ': 'Aixam',
#     'Renault ': 'Renault',
#     'Suzuki ': 'Suzuki',
#     'Nissan ': 'Nissan',
#     'Mitsubishi ': 'Mitsubishi',
#     'Volvo ': 'Volvo',
#     'Daihatsu ': 'Daihatsu',
#     'Ford ': 'Ford',
#     'Kia ': 'Kia',
# }

MOBILE_PREFIX = 'https://www.mobile.bg/'
URL = MOBILE_PREFIX + 'obiavi/avtomobili-dzhipove/namira-se-v-balgariya/p-{page_num}?price={price_min}&price1={price_max}&sort=6&nup=014&pictonly=1'
# `sort=6` - sort by newest
# `pictonly=1` - only show if picture is available

URL_PROTO = URL.split('//')[0]

BS_PARSER = 'html.parser'

NET_CACHE_DURATION_SEC = 60 * 60 * 24 # 24h
NET_CACHE_LOC = str(Path(__file__).parent / "cache")

EUR_TO_BGN = 1.95583

##########
########## class
##########

@dataclass
class Car:
    link_mobile: str
    link_autodata: str

    title: str
    brand: str

    # per 100km
    fuel_consumption_urban: float # in liters
    fuel_consumption_highway: float # in liters

    engine_type: str

    # in km
    mialage: float

    # in eur
    price: float

    @classmethod
    def new(cls, link_mobile: str, link_autodata: str, title: str, engine_type:str, mialage: float, price: float) -> "Car":
        # print()
        # print(f'dbg: {link_mobile=}')
        # print(f'dbg: {link_autodata=}')

        ##### brand

        # for prefix, name in BRANDS_PREFIX_NAME.items():
        #     if title.lower().startswith(prefix.lower()):
        #         brand = name.lower()
        #         break
        # else:
        #     raise ValueError(f'cannot determine car brand: {title}')

        brand = title.lower()

        if '-' in brand:
            brand = brand.split('-')[0]

        brand = brand.split(' ')[0]

        if brand == 'vw':
            brand = 'volkswagen'

        ##### ...

        autodata_html = net_req(link_autodata)
        soup = BeautifulSoup(autodata_html, BS_PARSER)

        # TODO: it is actually possible that we get an invalid link that leads to multiple datasheets that we need to choose from (we need to handle this)
        fuel_consumption_urban = extract_fuel_consumption(soup, 'Разход на гориво - градско')
        fuel_consumption_highway = extract_fuel_consumption(soup, 'Разход на гориво - извънградско')
        if (fuel_consumption_urban is None) or (fuel_consumption_highway is None):
            print(f'WARNING: could not extract fuel consumption for: {link_mobile}')
            fuel_consumption_urban = float('inf')
            fuel_consumption_highway = float('inf')

        return cls(link_mobile, link_autodata, title, brand, fuel_consumption_urban, fuel_consumption_highway, engine_type, mialage, price)

    def __str__(self) -> str:
        return f'''{self.title} {Fore.BLUE}{self.link_mobile}{Style.RESET_ALL}
    fuel consumption: {self.fuel_consumption_urban} / {self.fuel_consumption_highway}
    price: {self.price * EUR_TO_BGN} BGN
    brand: {self.brand}
    mialage: {self.mialage}'''

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

    if fuel_consumption == prefix:
        # the column exists, but the data is empty
        return None

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
        print(f'extracting links, page {page_number}/{number_of_pages_to_extract}')

        url = URL.format(page_num=page_number, price_min=PRICE_MIN, price_max=PRICE_MAX)
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

    for link_idx, link in enumerate(links):
        print(f'extracting car data, link {link_idx+1}/{len(links)}')

        car_html = net_req(link)
        soup = BeautifulSoup(car_html, BS_PARSER)

        elem_info = soup.find('div', class_='contactsBox')

        elem_title = elem_info.find('div', class_='obTitle')
        title = elem_title.text.strip()
        title = title.split(' Обява: ')[0]

        elem_price = elem_info.find('div', class_='Price')
        price = elem_price.text.strip().split('€')[0]
        price = price.strip().replace(' ', '')
        price = float(price)

        elem_params = soup.find('div', class_='borderBox carParams')

        elem_engine = soup.find('div', class_='item dvigatel')
        engine_type = elem_engine.find('div', class_='mpInfo').text

        elem_mialage = soup.find('div', class_='item probeg')
        if elem_mialage is None:
            mialage = float('inf')
        else:
            mialage = elem_mialage.find('div', class_='mpInfo').text
            tmp = ' км'
            assert mialage.endswith(tmp)
            mialage = mialage.removesuffix(tmp)
            mialage = float(mialage)

        elem_link_autodata = elem_params.find('div', class_='autodata24')
        link_autodata = elem_link_autodata.find('a').get('href')

        car = Car.new(link, link_autodata, title, engine_type, mialage, price)

        if car.brand in BLACKLIST_BRAND:
            continue

        if car.fuel_consumption_urban > BLACKLIST_FUEL_CONSUMPTION_URBAN:
            continue

        cars.append(car)

    return cars

##########
########## main
##########

def main() -> None:
    requests_cache.install_cache(NET_CACHE_LOC, expire_after=NET_CACHE_DURATION_SEC)

    car_links = extract_car_links_from_website(number_of_pages_to_extract=NUMBER_OF_PAGES_TO_PARSE)
    cars = extract_cars_data_from_links(car_links)
    cars.sort(key=lambda car: car.fuel_consumption_urban, reverse=True)

    for car in cars:
        print()
        print(car)

def parse_cmdline() -> None:
    parser = ArgumentParser("Extract car data")
    _args = parser.parse_args()
    main()

if __name__ == '__main__':
    parse_cmdline()
