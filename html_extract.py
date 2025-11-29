from collections.abc import Generator
from concurrent.futures import Future, ProcessPoolExecutor, as_completed

from bs4 import BeautifulSoup

import config
from car import Car
from net import net_req


def extract_car_links_from_website(
    executor: ProcessPoolExecutor,
) -> Generator[Future[list[str]]]:
    price_max = config.PRICE_MAX_BGN
    price_min = max(price_max - config.PRICE_STEP, config.PRICE_MIN_BGN)

    while True:
        # print(
        #     f"processing price range --> {config.PRICE_MIN_BGN:_} <= [{price_min:_} : {price_max:_}] <= {config.PRICE_MAX_BGN:_}"
        # )

        yield executor.submit(_process_price_range, price_min, price_max)

        if price_min <= config.PRICE_MIN_BGN:
            break

        price_max = price_min - 1
        price_min = max(price_max - config.PRICE_STEP, config.PRICE_MIN_BGN)

    # print()


def extract_car(link: str) -> Car | None:
    return Car.new(link)


def _process_price_range(price_min: int, price_max: int) -> list[str]:
    collected_car_links = []

    for page_number in range(1, config.MAX_PAGE + 1):
        # if page_number % 10 == 0:
        # print(f"processing page {page_number}[/~{config.MAX_PAGE}?]")

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
            assert href is not None
            assert isinstance(href, str)

            # 2025.08.31: this is currently the case - the urls start with `//` rather than `https://`
            if href.startswith("//"):
                href = config.URL_PROTO + href

            collected_car_links.append(href)

    else:
        print(
            "WARNING: reached last possible page, it is likely that some cars were missed"
        )

    return collected_car_links
