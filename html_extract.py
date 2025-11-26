from concurrent.futures import ProcessPoolExecutor

from bs4 import BeautifulSoup

import config
from car import Car
from net import net_req


def extract_car_links_from_website() -> list[str]:
    car_links = []

    price_max = config.PRICE_MAX_BGN
    price_min = max(price_max - config.PRICE_STEP, config.PRICE_MIN_BGN)

    while True:
        for page_number in range(1, config.MAX_PAGE + 1):
            # if page_number % 10 == 0:
            print(
                f"[{config.PRICE_MIN_BGN:_} < {price_min:_}:{price_max:_} < {config.PRICE_MAX_BGN:_}] extracting links, page {page_number}[/~{config.MAX_PAGE}?]"
            )

            url = config.URL.format(
                page_num=page_number, price_min=price_min, price_max=price_max
            )

            response = net_req(url)
            assert response is not None

            soup = BeautifulSoup(response, config.BS_PARSER)

            # TODO: this is fragile
            # find the "Няма намерени обяви!" message
            if soup.find("div", class_="width980px pageMessageAlert"):
                break

            for elem in soup.find_all("a", class_="title saveSlink"):
                href = elem.get("href")

                # 2025.08.31: this is currently the case - the urls start with `//` rather than `https://`
                if href.startswith("//"):
                    href = config.URL_PROTO + href

                car_links.append(href)

        else:
            print(
                "WARNING: reached last possible page, it is likely that some cars were missed"
            )

        if price_min <= config.PRICE_MIN_BGN:
            break

        price_max = price_min - 1
        price_min = max(price_max - config.PRICE_STEP, config.PRICE_MIN_BGN)

    return car_links


def extract_cars_data_from_links(links: list[str]):
    print("Extracting Car Data...")

    # cars = []

    # for link_idx, link in enumerate(links):
    #     if link_idx % 100 == 0:
    #         print(f'extracting car data, link {link_idx+1}/{len(links)}')

    #     car = extract_car(link)
    #     if car is None:
    #         continue

    #     cars.append(car)

    # # TODO: this might get us IP blocked
    with ProcessPoolExecutor(
        max_workers=config.EXTRACT_CAR_DATA_MAX_WORKERS
    ) as executor:
        cars = list(
            executor.map(extract_car, links)
        )  # the function being called here cannot be a lambda

    cars = [car for car in cars if car is not None]

    print("Car Data Extracted")

    return cars


def extract_car(link: str) -> Car | None:
    return Car.new(link)
