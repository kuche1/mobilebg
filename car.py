from dataclasses import dataclass

from bs4 import (
    BeautifulSoup,
)  # pacman -S python-beautifulsoup4 # OR: pacman -S python-beautifulsoup4 python-cchardet python-chardet python-lxml python-html5lib
from colorama import Fore, Style

import config
from net import net_req
from util import extract_autodata_float


@dataclass
class Car:
    link_mobile: str
    link_autodata: str

    title: str
    brand: str

    # per 100km
    fuel_consumption_urban: float  # in liters
    fuel_consumption_highway: float  # in liters

    engine_type: str
    gearbox: str
    mialage: float  # in km
    price: float  # in eur
    horsepower: int
    length_mm: float
    date_produced: str
    description: str

    def __str__(self) -> str:
        return f"""{self.title} {Fore.BLUE}{self.link_mobile}{Style.RESET_ALL}
    price: {int(self.price * config.EUR_TO_BGN):_} BGN
    date produced: {self.date_produced}
    fuel consumption: {self.fuel_consumption_urban} / {self.fuel_consumption_highway}
    horsepower: {self.horsepower}
    length: {self.length_mm} mm
    engine type: {self.engine_type}
    gearbox: {self.gearbox}
    brand: {self.brand}
    mialage: {self.mialage:_}"""

    @classmethod
    def new(cls, link_mobile: str) -> "Car | None":
        # print()
        # print(f'dbg: {link_mobile=}')
        # print(f'dbg: {link_autodata=}')

        ##### check blacklisted links

        if link_mobile in config.BLACKLIST_LINK_MOBILE:
            return None

        ##### extract data

        car_html = net_req(link_mobile)
        if car_html is None:
            # has been deleted
            return None

        soup = BeautifulSoup(car_html, config.BS_PARSER)

        elem_info = soup.find("div", class_="contactsBox")

        ### title

        title = cls._extract_title(elem_info)

        ### brand

        brand = cls._extract_brand(title)
        if brand is None:
            return None

        ### ...

        elem_price = elem_info.find("div", class_="Price")
        price = elem_price.text.strip().split("€")[0]
        price = price.strip().replace(" ", "")
        price = float(price)

        elem_params = soup.find("div", class_="borderBox carParams")

        elem_engine = soup.find("div", class_="item dvigatel")
        engine_type = elem_engine.find("div", class_="mpInfo").text

        gearbox = _extract_gearbox(soup)
        if gearbox is None:
            return None

        horsepower = _extract_horsepower(soup)
        if horsepower is None:
            return None

        mialage = _extract_mialage(soup, link_mobile)

        elem_link_autodata = elem_params.find("div", class_="autodata24")
        link_autodata = elem_link_autodata.find("a").get("href")

        ### date produced

        date_produced = cls._extract_date_produced(elem_params)

        ### description

        description = cls._extract_description(soup, link_mobile)

        ##### ...

        autodata_html = net_req(link_autodata)
        assert autodata_html is not None

        soup = BeautifulSoup(autodata_html, config.BS_PARSER)

        # TODO: it is actually possible that we get an invalid link that leads to multiple datasheets that we need to choose from (we need to handle this)
        fuel_consumption_urban = extract_autodata_float(
            soup, "Разход на гориво - градско", " Литра/100 км"
        )
        fuel_consumption_highway = extract_autodata_float(
            soup, "Разход на гориво - извънградско", " Литра/100 км"
        )
        if (fuel_consumption_urban is None) or (fuel_consumption_highway is None):
            if config.PRINT_FUEL_CONSUMPTION_EXTRACTION_WARNING:
                print(f"WARNING: could not extract fuel consumption for: {link_mobile}")
            fuel_consumption_urban = float("inf")  # 0
            fuel_consumption_highway = float("inf")  # 0

        car_length = extract_autodata_float(soup, "Дължина", " ММ")
        if car_length is None:
            car_length = 0

        ##### return

        car = cls(
            link_mobile,
            link_autodata,
            title,
            brand,
            fuel_consumption_urban,
            fuel_consumption_highway,
            engine_type,
            gearbox,
            mialage,
            price,
            horsepower,
            car_length,
            date_produced,
            description,
        )

        if config.BLACKLIST_FNC(car):
            return None

        return car

    @classmethod
    def _extract_title(cls, elem_info) -> str:
        elem_title = elem_info.find("div", class_="obTitle")
        title = elem_title.text.strip()
        title = title.split(" Обява: ")[0]
        return title

    @classmethod
    def _extract_brand(cls, title: str) -> str | None:
        brand = title.lower()

        if "-" in brand:
            brand = brand.split("-")[0]

        brand = brand.split(" ")[0]

        if brand == "vw":
            brand = "volkswagen"

        if config.BRAND_WHITELIST is not None:
            if brand not in config.BRAND_WHITELIST:
                return None

        if brand in config.BRAND_BLACKLIST:
            return None

        return brand

    @classmethod
    def _extract_date_produced(cls, elem_params) -> str:
        date_produced = elem_params.find("div", class_="item proizvodstvo")
        if date_produced is None:
            return "UNKNOWN"

        date_produced = date_produced.find("div", class_="mpInfo").text
        return date_produced

    @classmethod
    def _extract_description(cls, soup, link_mobile: str) -> str:
        elem_desc = soup.find("div", class_="moreInfo")
        if elem_desc is None:
            return "NO-DESCRIPTION"

        elem_desc = elem_desc.find("div", class_="text")
        if elem_desc is None:
            raise AssertionError

        return elem_desc.text.strip()


def _extract_mialage(soup: BeautifulSoup, link_mobile: str) -> float:
    if (
        link_mobile
        == "https://www.mobile.bg/obiava-11762231838386479-toyota-yaris-1300-vvt-i"
    ):
        return 135_589.0

    elem_mialage = soup.find("div", class_="item probeg")
    if elem_mialage is None:
        mialage = float("inf")
    else:
        mialage = elem_mialage.find("div", class_="mpInfo").text  # pyright: ignore[reportOptionalMemberAccess]
        tmp = " км"
        assert mialage.endswith(tmp)
        mialage = mialage.removesuffix(tmp)
        mialage = float(mialage)

    return mialage


def _extract_horsepower(soup: BeautifulSoup) -> int | None:
    elem_horsepower = soup.find("div", class_="item moshtnost")
    if elem_horsepower is None:
        if config.HORSEPOWER_MISSING_OK:
            return -1
        else:
            return None
    else:
        horsepower = elem_horsepower.find("div", class_="mpInfo").text  # pyright: ignore[reportOptionalMemberAccess]
        tmp = " к.с."
        assert horsepower.endswith(tmp)
        horsepower = horsepower.removesuffix(tmp)
        horsepower = int(horsepower)

    if config.HORSEPOWER_MIN is not None:
        if horsepower < config.HORSEPOWER_MIN:
            return None

    return horsepower


def _extract_gearbox(soup: BeautifulSoup) -> str | None:
    elem_gearbox = soup.find("div", class_="item skorosti")
    assert elem_gearbox is not None

    elem_gearbox = elem_gearbox.find("div", class_="mpInfo")
    assert elem_gearbox is not None

    gearabox = elem_gearbox.text
    if gearabox in config.GEARBOX_BLACKLIST:
        return None

    return gearabox
