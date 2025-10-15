#! /usr/bin/env python3

# INFO:
#
# check aerodynamics
#   important for highway fuel consumption
#   look for cd
#   (do note that the surface area is also important) 
#   https://www.automobile-catalog.com/#gsc.tab=0
#
# check car complaints by year
#   https://www.carcomplaints.com/Honda/Civic/

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

# https://www.mobile.bg/obiava-11724238603261812-honda-civic-2-2d [mialage 183_680] [HP 140] [consumption 6.6]

# izglejda ok
# https://www.mobile.bg/obiava-11754655705797468-skoda-scala-lizing-340-lv-mesets [consumption 6.4????5.9????] [HP 110]

# looks good
# https://www.mobile.bg/obiava-11737477063769512-toyota-verso-2-0d-4d-navi-panorama [consumption 5.9/4.4] [HP 125] [mialage 111_111]

# https://www.mobile.bg/obiava-11756831150112606-honda-civic-2-2-i-ctdi-sport [consumption 6.6] [HP 140] [mialage 183_680] [hatchback]

# https://www.mobile.bg/obiava-11754762069158225-opel-meriva [milage 92_000] [HP 101] [price 7_800]

# https://www.mobile.bg/obiava-11735582531025771-suzuki-swift-lpg-1-3-i-92000km [mialage 92_000] [hp 92] [gas]

# https://www.mobile.bg/obiava-21757710139304843-suzuki-ignis-1-3-4x4-92000km

# https://www.mobile.bg/obiava-11756366448461410-kia-ceed-petrol-lpg [fabric gas] [mialage 131_071]

# https://www.mobile.bg/obiava-11749902203208164-nissan-note

# sidenote: [fabric gas] + [mialage <150_000] + [hp >90]

from argparse import ArgumentParser
from bs4 import BeautifulSoup # pacman -S python-beautifulsoup4 # OR: pacman -S python-beautifulsoup4 python-cchardet python-chardet python-lxml python-html5lib
from dataclasses import dataclass
from requests_cache import CachedSession
from pathlib import Path
from colorama import Fore, Style
from concurrent.futures import ProcessPoolExecutor

PRICE_MIN_BGN = 3_400 # TODO: reduce to 3_000
PRICE_MAX_BGN = 8_000 # TODO: reduce to 6_000
PRICE_STEP = 100 # if this is too big, you might miss some of the listings

PRINT_FUEL_CONSUMPTION_EXTRACTION_WARNING = False

NET_CACHE_LOC = str(Path(__file__).parent / "cache")
NET_CACHE_DURATION_MOBILEBG_SEC = 60 * 60 * 10 # 10h
NET_CACHE_DURATION_MOBILEBG_SPECIFIC_CAR_SEC = 60 * 60 * 24 * 30 # 1 month
NET_CACHE_DURATION_AUTODATA_SEC = 60 * 60 * 24 * 30 # 1 month

WHITELIST_BRAND: list | None = \
None
# [
#     # 'honda',
#     'toyota'
# ]

BLACKLIST_BRAND: list = [
    # too fragile
    'audi', 'bmw', 'peugeot', 'citroen', 'alfa', 'fiat', 'land', 'jaguar', 'lexus',

    # rust
    'renault', 'mazda',

    # hard to find parts
    'chevrolet',

    # the battery is going to die
    'smart',

    'lada',

    'mini',

    'jeep',
]

def blacklist_fnc(car: "Car") -> bool:
    # TODO: remove
    #
    # if '1.9' not in car.title.lower():
    #     return True
    #
    # # if not car.title.lower().startswith('honda civic'):
    # if not car.title.lower().startswith('toyota corolla'):
    #     return True
    #
    if True: # gas
        if (
            (car.engine_type.lower() != 'газ')
            and
            ('gas' not in car.description.lower())
            and
            ('газ' not in car.description.lower())
            and
            ('газ' not in car.title.lower())
        ): # TODO: and what if it is gas BUT it's only specified as engine type ?
            return True

        if 'фабр' not in car.description.lower():
            return True

    # # will be hard to control on highways
    # if car.length_mm != 0:
    #     if (car.length_mm <= 3615):
    #         return True

    # will be bad on highways
    if car.horsepower != 0:
        if car.horsepower < 90: # < 90 || <= 90
            return True

    if car.brand in ['skoda', 'kia', 'toyota', 'opel', 'hyundai', 'dacia', 'honda', 'aixam', 'suzuki', 'nissan', 'mitsubishi', 'volvo', 'daihatsu', 'subaru', 'ssangyong', 'lancia', 'daewoo']:
        # at least ok
        pass

    elif car.brand in ['ford']:
        # fords that are 1.6 disel are ok
        pass

    elif car.brand in ['mercedes']:
        # dependes on the mercedes car
        pass

    elif car.brand in ['seat', 'volkswagen']:
        # ok ONLY if 1.9TDI
        pass

    else:
        # too many brands to filter out
        # raise AssertionError(f'unknown brand: {car.brand}')
        pass

    # # ban fords that are not 1.6 disel (so 1.6 TDCi ?)
    # if car.link_autodata in ['https://bg.autodata24.com/ford/fiesta/fiesta-v-mk6/14-tdci-68-hp/details']:
    #     return True

    # # ban seats that are not 1.9TDI
    # if car.link_autodata in ['https://bg.autodata24.com/seat/altea/altea-freetrack/16-tdi-cr-105-hp-dpf-2wd/details']:
    #     return True

    # # too expensive
    # if car.fuel_consumption_urban > 7.0:
    #     return True

    # # only 67HP
    # if car.link_autodata == 'https://bg.autodata24.com/toyota/aygo/aygo/10-i-12v-67-hp/details':
    #     return True

    # horsepower if missing (75)
    if car.link_mobile == 'https://www.mobile.bg/obiava-11749668026765654-toyota-yaris-1-4-d4d':
        return True

    # needs a new engine (that is expensive)
    if car.link_mobile == 'https://www.mobile.bg/obiava-11749994255252093-skoda-fabia':
        return True

    # looks terrible
    if car.link_mobile in ['https://www.mobile.bg/obiava-11738432582242534-vw-new-beetle', 'https://www.mobile.bg/obiava-11750486418014720-vw-new-beetle-1-9-tdi-arte']:
        return True

    if car.link_mobile in [
        'https://www.mobile.bg/obiava-11730218705875847-infiniti-q-q60s', # broken
        'https://www.mobile.bg/obiava-11756972387827865-vw-caddy', # ugly minivan taxi
        'https://www.mobile.bg/obiava-11718829730982754-opel-ampera', # not a car
        'https://www.mobile.bg/obiava-11687274566657694-moskvich-412', # old
        'https://www.mobile.bg/obiava-11755276385116294-ford-connect', # ugly
        'https://www.mobile.bg/obiava-21718230985416582-nissan-qashqai-2-0-16v-avtomat-panorama-nov-vnos-ot-italiya', # kroken
        'https://www.mobile.bg/obiava-21749152456089930-kia-niro-ev', # electric
        'https://www.mobile.bg/obiava-11752735199892179-dacia-logan-bez-klimatik', # no air conditioner
        'https://www.mobile.bg/obiava-11754564673244207-honda-insight', # wheel wrong side
        'https://www.mobile.bg/obiava-11752502309169199-vw-caddy', # ugly fat taxi
        'https://www.mobile.bg/obiava-21756716964221395-kia-sportage-2-0', # uses too much fuel
        'https://www.mobile.bg/obiava-11714283168788667-seat-altea-1-6-xl-benzin-metan-cng', # uses too much fuel
        'https://www.mobile.bg/obiava-11733769187894687-seat-altea-benzin', # fuel hungry
        'https://www.mobile.bg/obiava-21755144538268887-uaz-452', # old truck
        'https://www.mobile.bg/obiava-21744189208414026-ssangyong-actyon-2300-tsena-do-31-viii', # fuel hungry
        'https://www.mobile.bg/obiava-11718539174391899-opel-senator', # broken
        'https://www.mobile.bg/obiava-11756819601829750-toyota-corolla-hybrid', # taxi
        'https://www.mobile.bg/obiava-11749980271197050-volga-24', # old
        'https://www.mobile.bg/obiava-11752418981164740-hyundai-i30', # taxi
        'https://www.mobile.bg/obiava-11724360561495950-mercedes-benz-115-200d', # old
        'https://www.mobile.bg/obiava-21743146556646997-uaz-2206', # old military
        'https://www.mobile.bg/obiava-11718987545311023-mg-mgf-1-8-mpi', # no roof
        'https://www.mobile.bg/obiava-11666104139552976-trabant-601', # old
        'https://www.mobile.bg/obiava-11756221955881897-toyota-corolla', # taxi
        'https://www.mobile.bg/obiava-21756123833296131-uaz-469', # old military
        'https://www.mobile.bg/obiava-21755605551199987-honda-cr-v', # wheel wrong side
        'https://www.mobile.bg/obiava-11711957700169281-kia-ceed-gaz-barter', # taxi
    ]:
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
    date_produced: str
    description: str

    def __str__(self) -> str:
        return f'''{self.title} {Fore.BLUE}{self.link_mobile}{Style.RESET_ALL}
    price: {int(self.price * EUR_TO_BGN):_} BGN
    date produced: {self.date_produced}
    fuel consumption: {self.fuel_consumption_urban} / {self.fuel_consumption_highway}
    horsepower: {self.horsepower}
    length: {self.length_mm} mm
    engine type: {self.engine_type}
    brand: {self.brand}
    mialage: {self.mialage:_}'''

    @classmethod
    def new(cls, link_mobile: str) -> "Car | None":
        # print()
        # print(f'dbg: {link_mobile=}')
        # print(f'dbg: {link_autodata=}')

        ##### extract data

        car_html = net_req(link_mobile)
        if car_html is None:
            # has been deleted
            return None

        soup = BeautifulSoup(car_html, BS_PARSER)

        elem_info = soup.find('div', class_='contactsBox')

        ### title

        title = cls._extract_title(elem_info)

        ### brand

        brand = cls._extract_brand(title)
        if brand is None:
            return None

        ### ...

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

        ### date produced

        date_produced = cls._extract_date_produced(elem_params)

        ### description

        description = cls._extract_description(soup, link_mobile)

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
            car_length = 0

        ##### return

        car = cls(link_mobile, link_autodata, title, brand, fuel_consumption_urban, fuel_consumption_highway, engine_type, mialage, price, horsepower, car_length, date_produced, description)

        if blacklist_fnc(car):
            return None

        return car

    @classmethod
    def _extract_title(cls, elem_info) -> str:
        elem_title = elem_info.find('div', class_='obTitle')
        title = elem_title.text.strip()
        title = title.split(' Обява: ')[0]
        return title

    @classmethod
    def _extract_brand(cls, title: str) -> str | None:
        brand = title.lower()

        if '-' in brand:
            brand = brand.split('-')[0]

        brand = brand.split(' ')[0]

        if brand == 'vw':
            brand = 'volkswagen'

        if WHITELIST_BRAND is not None:
            if brand not in WHITELIST_BRAND:
                return None

        if brand in BLACKLIST_BRAND:
            return None
        
        return brand

    @classmethod
    def _extract_date_produced(cls, elem_params) -> str:
        date_produced = elem_params.find('div', class_='item proizvodstvo')
        if date_produced is None:
            return 'UNKNOWN'

        date_produced = date_produced.find('div', class_='mpInfo').text
        return date_produced

    @classmethod
    def _extract_description(cls, soup, link_mobile: str) -> str:
        elem_desc = soup.find('div', class_='moreInfo')
        if elem_desc is None:
            return 'NO-DESCRIPTION'

        elem_desc = elem_desc.find('div', class_='text')
        if elem_desc is None:
            raise AssertionError

        return elem_desc.text.strip()

##########
########## network
##########

# TODO: this sucks
g_session = CachedSession(NET_CACHE_LOC)

def net_req(url: str) -> str | None:
    if url.startswith('https://www.mobile.bg/obiavi/'):
        cache_duration = NET_CACHE_DURATION_MOBILEBG_SEC
    elif url.startswith('https://www.mobile.bg/obiava-'):
        cache_duration = NET_CACHE_DURATION_MOBILEBG_SPECIFIC_CAR_SEC
    elif url.startswith('https://bg.autodata24.com'):
        cache_duration = NET_CACHE_DURATION_AUTODATA_SEC
    else:
        raise AssertionError(f'unknown URL: {url}')

    # response = requests.get(url)
    response = g_session.get(url, expire_after=cache_duration)

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
    # cars = []
    
    # for link_idx, link in enumerate(links):
    #     if link_idx % 100 == 0:
    #         print(f'extracting car data, link {link_idx+1}/{len(links)}')
    
    #     car = extract_car(link)
    #     if car is None:
    #         continue
    
    #     cars.append(car)

    # # TODO: this might get us IP blocked
    with ProcessPoolExecutor() as executor:
        cars = list(executor.map(extract_car, links)) # the function being called here cannot be a lambda

    cars = [car for car in cars if car is not None]

    return cars

def extract_car(link: str) -> Car | None:
    return Car.new(link)

##########
########## main
##########

def main() -> None:
    car_links = extract_car_links_from_website()
    # for some reason the website only allows for up to 150 pages

    cars = extract_cars_data_from_links(car_links)
    # cars.sort(key=lambda car: car.fuel_consumption_urban, reverse=True)
    # cars.sort(key=lambda car: car.mialage, reverse=True)
    cars.sort(key=lambda car: (-car.mialage, car.price))

    for car in cars:
        print()
        print(car)

def parse_cmdline() -> None:
    parser = ArgumentParser("Extract car data")
    _args = parser.parse_args()
    main()

if __name__ == '__main__':
    parse_cmdline()
