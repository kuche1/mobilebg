import time

from requests_cache import CachedSession

import config

# TODO: this sucks
g_session = CachedSession(config.NET_CACHE_LOC)


def net_req(url: str) -> str | None:
    if url.startswith("https://www.mobile.bg/obiavi/"):
        cache_duration = config.NET_CACHE_DURATION_MOBILEBG_SEC
    elif url.startswith("https://www.mobile.bg/obiava-"):
        cache_duration = config.NET_CACHE_DURATION_MOBILEBG_SPECIFIC_CAR_SEC
    elif url.startswith("https://bg.autodata24.com"):
        cache_duration = config.NET_CACHE_DURATION_AUTODATA_SEC
    else:
        raise AssertionError(f"unknown URL: {url}")

    # response = requests.get(url)
    response = g_session.get(url, expire_after=cache_duration)

    if not response.from_cache:
        time.sleep(config.NET_HAD_TO_CONNECT_SLEEP)

    if url.startswith(config.MOBILE_PREFIX):
        response.encoding = "cp1251"  # otherwise we get gibberish

    if response.status_code == 404:
        return None

    assert response.ok
    return response.text
