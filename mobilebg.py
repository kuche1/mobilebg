#! /usr/bin/env python3

# INFO:
#
# check aerodynamics
#   important for highway fuel consumption
#   look for cd
#   (do note that the surface area is also important) 
#   https://www.automobile-catalog.com/#gsc.tab=0

# https://www.mobile.bg/obiava-11756567042078005-honda-civic

## consumption 4.0 <WRONG(?)> it's actially 5.1 - https://www.automobile-catalog.com/car/2013/3140735/skoda_fabia_1_6_tdi_cr_75.html#gsc.tab=0 [cd 0.32]
# https://www.mobile.bg/obiava-11733734734519038-skoda-fabia-1-6-tdi 309_500 км
# https://www.mobile.bg/obiava-11755168140519872-skoda-fabia-1-6tdi 300_000 км
#
## [consumption 4.75 or 5.7 ?] [cd 0.32]
# https://www.mobile.bg/obiava-11755152549224362-kia-rio-1-500-crdi-euro4 [110hp] [mialage 162_000] (4.9 seats)
#
# https://www.mobile.bg/obiava-11722710214333675-honda-civic [mialage 324761]
# https://www.mobile.bg/obiava-11756577470299500-honda-civic-2-2-diesel-140hp [mialage 215_000] [cd 0.32] [consumption 6.6] [140 HP]
#
# https://www.mobile.bg/obiava-11745351279405146-honda-fr-v-2-200i-ctdi-euro4 [mialage 199000]
# https://www.mobile.bg/obiava-11748632810641631-honda-fr-v-2-2-cdti-6mesta-6skorosti-klimatron [mialage 207400]

# https://www.mobile.bg/obiava-11704364264877217-vw-polo-1-9-tdi (NO ima rujda po kalnicite (i moje bi i po mosta - ne se znae)) (Кюстендил)

# https://www.mobile.bg/obiava-11756542187704518-ford-fusion [mialage 160_000] [HP 90] [consumption 5.5] [cd 0.35]
# https://bg.autodata24.com/ford/fusion/fusion/16-tdci-90-hp/details
# https://www.automobile-catalog.com/car/2005/961550/ford_fusion_1_6_tdci_.html#gsc.tab=0

# https://www.mobile.bg/obiava-11754677013905706-honda-civic-2-2d [mialage 183_452] [HP 140] [consumption 6.6]
# https://www.mobile.bg/obiava-11724238603261812-honda-civic-2-2d [mialage 183_680] [HP 140] [consumption 6.6]

# izglejda ok
# https://www.mobile.bg/obiava-11754655705797468-skoda-scala-lizing-340-lv-mesets [consumption 6.4????5.9????] [HP 110]

from argparse import ArgumentParser
from re import L
import requests
from bs4 import BeautifulSoup # pacman -S python-beautifulsoup4 # OR: pacman -S python-beautifulsoup4 python-cchardet python-chardet python-lxml python-html5lib
from dataclasses import dataclass
import requests_cache
from pathlib import Path
from colorama import Fore, Style

PRICE_MIN_BGN = 2_500
PRICE_MAX_BGN = 6_000
PRICE_STEP = 100 # if this is too big, you might miss some of the listings

PRINT_FUEL_CONSUMPTION_EXTRACTION_WARNING = False

def blacklist_fnc(car: "Car") -> bool:

    # will be hard to control on highways
    if car.length_mm <= 3615:
        return True

    # will be bad on highways
    if car.horsepower != 0:
        if car.horsepower < 90: # < 90 || <= 90
            return True

    if car.brand in ['skoda', 'kia', 'toyota', 'opel', 'hyundai', 'dacia', 'honda', 'aixam', 'suzuki', 'nissan', 'mitsubishi', 'volvo', 'daihatsu', 'subaru', 'ssangyong', 'lancia', 'daewoo']:
        # at least ok
        pass

    elif car.brand in ['audi', 'bmw', 'peugeot', 'citroen', 'alfa', 'fiat', 'land', 'jaguar', 'lexus']:
        # too fragile
        return True

    elif car.brand in ['renault', 'mazda']:
        # rust
        return True

    elif car.brand in ['ford']:
        # fords that are 1.6 disel are ok
        pass

    elif car.brand in ['mercedes']:
        # dependes on the mercedes car
        pass

    elif car.brand in ['chevrolet']:
        # hard to find parts
        return True

    elif car.brand in ['seat', 'volkswagen']:
        # ok ONLY if 1.9TDI
        pass

    elif car.brand in ['smart']:
        # the battery is going to die
        return True

    elif car.brand in ['lada']:
        return True

    elif car.brand in ['mini']:
        return True

    elif car.brand in ['jeep']:
        return True

    else:
        # too many brands to filter out
        # raise AssertionError(f'unknown brand: {car.brand}')
        pass

    # ban fords that are not 1.6 disel (so 1.6 TDCi ?)
    if car.link_autodata in ['https://bg.autodata24.com/ford/fiesta/fiesta-v-mk6/14-tdci-68-hp/details']:
        return True

    # ban seats that are not 1.9TDI
    if car.link_autodata in ['https://bg.autodata24.com/seat/altea/altea-freetrack/16-tdi-cr-105-hp-dpf-2wd/details']:
        return True

    # too expensive
    if car.fuel_consumption_urban > 7.0:
        return True

    # only 67HP
    if car.link_autodata == 'https://bg.autodata24.com/toyota/aygo/aygo/10-i-12v-67-hp/details':
        return True

    # horsepower if missing (75)
    if car.link_mobile == 'https://www.mobile.bg/obiava-11749668026765654-toyota-yaris-1-4-d4d':
        return True

    # needs a new engine (that is expensive)
    if car.link_mobile == 'https://www.mobile.bg/obiava-11749994255252093-skoda-fabia':
        return True

    # looks terrible
    if car.link_mobile in ['https://www.mobile.bg/obiava-11738432582242534-vw-new-beetle', 'https://www.mobile.bg/obiava-11750486418014720-vw-new-beetle-1-9-tdi-arte']:
        return True

    # volan ot greshnata strana
    if car.link_mobile == 'https://www.mobile.bg/obiava-11754564673244207-honda-insight':
        return True

    # bez klimatik
    if car.link_mobile == 'https://www.mobile.bg/obiava-11752735199892179-dacia-logan-bez-klimatik':
        return True

    # electric
    if car.link_mobile == 'https://www.mobile.bg/obiava-21749152456089930-kia-niro-ev':
        return True

    return False

MOBILE_PREFIX = 'https://www.mobile.bg/'
URL = MOBILE_PREFIX + 'obiavi/avtomobili-dzhipove/oblast-sofiya/p-{page_num}?price={price_min}&price1={price_max}&sort=6&nup=014&pictonly=1'
# `sort=6` - sort by newest
# `pictonly=1` - only show if picture is available
#
# `namira-se-v-balgariya` - bulgaria
# `oblast-sofiya` - sofia

URL_PROTO = URL.split('//')[0]

MAX_PAGE = 150

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
    mialage: float # in km
    price: float # in eur
    horsepower: int
    length_mm: float

    @classmethod
    def new(cls, link_mobile: str, link_autodata: str, title: str, engine_type:str, mialage: float, price: float, horsepower: int) -> "Car":
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
        assert autodata_html is not None

        soup = BeautifulSoup(autodata_html, BS_PARSER)

        # TODO: it is actually possible that we get an invalid link that leads to multiple datasheets that we need to choose from (we need to handle this)
        fuel_consumption_urban = extract_autodata_float(soup, 'Разход на гориво - градско', ' Литра/100 км')
        fuel_consumption_highway = extract_autodata_float(soup, 'Разход на гориво - извънградско', ' Литра/100 км')
        if (fuel_consumption_urban is None) or (fuel_consumption_highway is None):
            if PRINT_FUEL_CONSUMPTION_EXTRACTION_WARNING:
                print(f'WARNING: could not extract fuel consumption for: {link_mobile}')
            fuel_consumption_urban = 0 # float('inf')
            fuel_consumption_highway = 0 # float('inf')

        car_length = extract_autodata_float(soup, 'Дължина', ' ММ')
        if car_length is None:
            car_length = float('inf')

        return cls(link_mobile, link_autodata, title, brand, fuel_consumption_urban, fuel_consumption_highway, engine_type, mialage, price, horsepower, car_length)

    def __str__(self) -> str:
        return f'''{self.title} {Fore.BLUE}{self.link_mobile}{Style.RESET_ALL}
    fuel consumption: {self.fuel_consumption_urban} / {self.fuel_consumption_highway}
    horsepower: {self.horsepower}
    length: {self.length_mm} mm
    price: {int(self.price * EUR_TO_BGN):_} BGN
    brand: {self.brand}
    mialage: {self.mialage:_}'''

##########
########## network
##########

def net_req(url: str) -> str | None:
    response = requests.get(url)

    if url.startswith(MOBILE_PREFIX):
        response.encoding = "cp1251" # otherwise we get gibberish

    if response.status_code == 404:
        return None

    assert response.ok
    return response.text

##########
########## html extract
##########

def extract_autodata_float(soup: BeautifulSoup, prefix: str, suffix: str) -> float | None:
    elem = soup.find('td', string=prefix)
    if elem is None:
        return None
    value = elem.parent.text

    value = value.replace('\n', ' ').replace('\t', ' ')
    while '  ' in value:
        value = value.replace('  ', ' ')
    value = value.strip()

    if value == prefix:
        # the column exists, but the data is empty
        return None

    tmp = prefix + ' '
    assert value.startswith(tmp)
    value = value.removeprefix(tmp)

    assert value.endswith(suffix)
    value = value.removesuffix(suffix)

    # if ' ' in value:
    #     part1, part2 = value.split(' ')
        
    #     part1 = float(part1)

    #     assert part2.startswith('(')
    #     part2 = part2[1:]

    #     assert part2.endswith(')')
    #     part2 = part2[:-1]

    #     part2 = float(part2)

    #     value = max(part1, part2)

    if '(' in value:
        part1, part2 = value.split('(')

        part1 = part1.removesuffix(' ')
        part2 = part2.removesuffix(')')

        part1 = float(part1)
        part2 = float(part2)
        value = max(part1, part2)

    elif '-' in value:
        part1, part2 = value.split('-')

        part1 = float(part1)
        part2 = float(part2)
        value = max(part1, part2)

    else:
        value = float(value)

    return value

def extract_car_links_from_website() -> list[str]:
    car_links = []

    price_max = PRICE_MAX_BGN
    price_min = max(price_max - PRICE_STEP, PRICE_MIN_BGN)

    while True:

        for page_number in range(1, MAX_PAGE+1):
            if page_number % 10 == 0:
                print(f'[{PRICE_MIN_BGN} < {price_min}-{price_max} < {PRICE_MAX_BGN}] extracting links, page {page_number}[/~{MAX_PAGE}?]')

            url = URL.format(page_num=page_number, price_min=price_min, price_max=price_max)

            response = net_req(url)
            assert response is not None

            soup = BeautifulSoup(response, BS_PARSER)

            # TODO: this is fragile
            # find the "Няма намерени обяви!" message
            if soup.find('div', class_='width980px pageMessageAlert'):
                break

            for elem in soup.find_all("a", class_="title saveSlink"):
                href = elem.get('href')

                # 2025.08.31: this is currently the case - the urls start with `//` rather than `https://`
                if href.startswith('//'):
                    href = URL_PROTO + href

                car_links.append(href)
        else:
            print("WARNING: reached last possible page, it is likely that some cars were missed")

        if price_min <= PRICE_MIN_BGN:
            break

        price_max = price_min - 1
        price_min = max(price_max - PRICE_STEP, PRICE_MIN_BGN)

    return car_links

def extract_cars_data_from_links(links: list[str]):
    cars = []

    for link_idx, link in enumerate(links):
        if link_idx % 100 == 0:
            print(f'extracting car data, link {link_idx+1}/{len(links)}')

        car_html = net_req(link)
        if car_html is None:
            # has been deleted
            continue

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

        elem_horsepower = soup.find('div', class_='item moshtnost')
        if elem_horsepower is None:
            horsepower = 0
        else:
            horsepower = elem_horsepower.find('div', class_='mpInfo').text
            tmp = ' к.с.'
            assert horsepower.endswith(tmp)
            horsepower = horsepower.removesuffix(tmp)
            horsepower = int(horsepower)

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

        car = Car.new(link, link_autodata, title, engine_type, mialage, price, horsepower)

        if blacklist_fnc(car):
            continue

        cars.append(car)

    return cars

##########
########## main
##########

def main() -> None:
    requests_cache.install_cache(NET_CACHE_LOC, expire_after=NET_CACHE_DURATION_SEC)

    car_links = extract_car_links_from_website()
    # for some reason the website only allows for up to 150 pages

    cars = extract_cars_data_from_links(car_links)
    # cars.sort(key=lambda car: car.fuel_consumption_urban, reverse=True)
    cars.sort(key=lambda car: car.mialage, reverse=True)

    for car in cars:
        print()
        print(car)

def parse_cmdline() -> None:
    parser = ArgumentParser("Extract car data")
    _args = parser.parse_args()
    main()

if __name__ == '__main__':
    parse_cmdline()
