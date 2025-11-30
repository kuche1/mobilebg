from pathlib import Path

##########
########## car filter
##########

PRICE_MIN_BGN = 3_600
PRICE_MAX_BGN = 9_000
PRICE_STEP = 800  # if this is too big, you might miss some of the listings

ENGINE_TYPE_BLACKLIST = ["Дизелов"]

HORSEPOWER_MISSING_OK = True
HORSEPOWER_MIN: int | None = None  # 75

GEARBOX_BLACKLIST = ["Автоматична", "Полуавтоматична"]

BRAND_WHITELIST: list[str] | None = [
    # 'honda',
    "toyota"
]

BRAND_BLACKLIST: list[str] = [
    # too fragile
    "audi",
    "bmw",
    "peugeot",
    "citroen",
    "alfa",
    "fiat",
    "land",
    "jaguar",
    "lexus",
    # rust
    "renault",
    "mazda",
    # hard to find parts
    "chevrolet",
    # the battery is going to die
    "smart",
    "lada",
    "mini",
    "jeep",
]


def BLACKLIST_FNC(car: "Car") -> bool:
    if "yaris".lower() not in car.title.lower():
        return True

    if (
        car.link_mobile
        in [
            "https://www.mobile.bg/obiava-11759826296862845-toyota-yaris-69000-km",  # chervena
            "https://www.mobile.bg/obiava-11749410734098519-toyota-yaris",  # advertising po kolata koito trqbva da se preboqdisa
        ]
    ):
        return True

    if car.title in [
        "Toyota Land cruiser",
        "Toyota Yaris 1.0",
        "Toyota Yaris / 1.0I / EURO 4 / ",
        "Toyota Yaris 1.0VVT-i/KLIMA",
        "Toyota Yaris 1.0 EVRO 5B",
        "Toyota Yaris 1.0 - 69 к.с.",
        "Toyota Yaris 1.0i, обслужена, каско, климатик, перфектна",
        "Toyota Yaris 1.0VVT-i EURO 5 ЛИЗИНГ",
        "Toyota Yaris 1.0i NAVI/KAMERA EURO 5",
        "Toyota Yaris P1 1.0 Expo",
        "Toyota Yaris 1.0 VVT-I ",
    ]:
        return True

    ##### only show if we have areason to believe it is 1.3/1.5/1.8
    for liters in ["3", "5", "8"]:
        if (liters in car.title) or (liters in car.description):
            break
    else:
        return True

    return False


BLACKLIST_LINK_MOBILE: list[str] = [
    "https://www.mobile.bg/obiava-11730218705875847-infiniti-q-q60s",  # broken
    "https://www.mobile.bg/obiava-11756972387827865-vw-caddy",  # ugly minivan taxi
    "https://www.mobile.bg/obiava-11718829730982754-opel-ampera",  # not a car
    "https://www.mobile.bg/obiava-11687274566657694-moskvich-412",  # old
    "https://www.mobile.bg/obiava-11755276385116294-ford-connect",  # ugly
    "https://www.mobile.bg/obiava-21718230985416582-nissan-qashqai-2-0-16v-avtomat-panorama-nov-vnos-ot-italiya",  # kroken
    "https://www.mobile.bg/obiava-21749152456089930-kia-niro-ev",  # electric
    "https://www.mobile.bg/obiava-11752735199892179-dacia-logan-bez-klimatik",  # no air conditioner
    "https://www.mobile.bg/obiava-11754564673244207-honda-insight",  # wheel wrong side
    "https://www.mobile.bg/obiava-11752502309169199-vw-caddy",  # ugly fat taxi
    "https://www.mobile.bg/obiava-21756716964221395-kia-sportage-2-0",  # uses too much fuel
    "https://www.mobile.bg/obiava-11714283168788667-seat-altea-1-6-xl-benzin-metan-cng",  # uses too much fuel
    "https://www.mobile.bg/obiava-11733769187894687-seat-altea-benzin",  # fuel hungry
    "https://www.mobile.bg/obiava-21755144538268887-uaz-452",  # old truck
    "https://www.mobile.bg/obiava-21744189208414026-ssangyong-actyon-2300-tsena-do-31-viii",  # fuel hungry
    "https://www.mobile.bg/obiava-11718539174391899-opel-senator",  # broken
    "https://www.mobile.bg/obiava-11756819601829750-toyota-corolla-hybrid",  # taxi
    "https://www.mobile.bg/obiava-11749980271197050-volga-24",  # old
    "https://www.mobile.bg/obiava-11752418981164740-hyundai-i30",  # taxi
    "https://www.mobile.bg/obiava-11724360561495950-mercedes-benz-115-200d",  # old
    "https://www.mobile.bg/obiava-21743146556646997-uaz-2206",  # old military
    "https://www.mobile.bg/obiava-11718987545311023-mg-mgf-1-8-mpi",  # no roof
    "https://www.mobile.bg/obiava-11666104139552976-trabant-601",  # old
    "https://www.mobile.bg/obiava-11756221955881897-toyota-corolla",  # taxi
    "https://www.mobile.bg/obiava-21756123833296131-uaz-469",  # old military
    "https://www.mobile.bg/obiava-21755605551199987-honda-cr-v",  # wheel wrong side
    "https://www.mobile.bg/obiava-11711957700169281-kia-ceed-gaz-barter",  # taxi
    "https://www.mobile.bg/obiava-11762941916083194-toyota-corolla",  # broken
    "https://www.mobile.bg/obiava-11755950568112190-toyota-iq-vvti-avtomat",  # 2 seats
    "https://www.mobile.bg/obiava-11762695831642034-toyota-corolla-verso",  # wrong wheel
    "https://www.mobile.bg/obiava-11763765782152542-toyota-iq-registrirana",  # 2 seats
    "https://www.mobile.bg/obiava-11763533567609435-toyota-corolla",  # "shum v motora"
    "https://www.mobile.bg/obiava-11762276613213029-toyota-yaris-1-8vvti-ts-133-ks",  # Намира се в гр. Долна баня
]


# def BLACKLIST_FNC(car: "Car") -> bool:
#     if "yaris" not in car.title.lower():
#         return True

#     return False


# def BLACKLIST_FNC(car: "Car") -> bool:
#     # TODO: remove
#     #
#     # if '1.9' not in car.title.lower():
#     #     return True
#     #
#     # # if not car.title.lower().startswith('honda civic'):
#     # if not car.title.lower().startswith('toyota corolla'):
#     #     return True
#     #
#     if True:  # gas
#         if (
#             (car.engine_type.lower() != "газ")
#             and ("gas" not in car.description.lower())
#             and ("газ" not in car.description.lower())
#             and ("газ" not in car.title.lower())
#         ):  # TODO: and what if it is gas BUT it's only specified as engine type ?
#             return True

#         if "фабр" not in car.description.lower():
#             return True

#     # # will be hard to control on highways
#     # if car.length_mm != 0:
#     #     if (car.length_mm <= 3615):
#     #         return True

#     # will be bad on highways
#     if car.horsepower != 0:
#         if car.horsepower < 80:  # < 90: # < 90 || <= 90
#             return True

#     if car.brand in [
#         "skoda",
#         "kia",
#         "toyota",
#         "opel",
#         "hyundai",
#         "dacia",
#         "honda",
#         "aixam",
#         "suzuki",
#         "nissan",
#         "mitsubishi",
#         "volvo",
#         "daihatsu",
#         "subaru",
#         "ssangyong",
#         "lancia",
#         "daewoo",
#     ]:
#         # at least ok
#         pass

#     elif car.brand in ["ford"]:
#         # fords that are 1.6 disel are ok
#         pass

#     elif car.brand in ["mercedes"]:
#         # dependes on the mercedes car
#         pass

#     elif car.brand in ["seat", "volkswagen"]:
#         # ok ONLY if 1.9TDI
#         pass

#     else:
#         # too many brands to filter out
#         # raise AssertionError(f'unknown brand: {car.brand}')
#         pass

#     # # ban fords that are not 1.6 disel (so 1.6 TDCi ?)
#     # if car.link_autodata in ['https://bg.autodata24.com/ford/fiesta/fiesta-v-mk6/14-tdci-68-hp/details']:
#     #     return True

#     # # ban seats that are not 1.9TDI
#     # if car.link_autodata in ['https://bg.autodata24.com/seat/altea/altea-freetrack/16-tdi-cr-105-hp-dpf-2wd/details']:
#     #     return True

#     # # too expensive
#     # if car.fuel_consumption_urban > 7.0:
#     #     return True

#     # # only 67HP
#     # if car.link_autodata == 'https://bg.autodata24.com/toyota/aygo/aygo/10-i-12v-67-hp/details':
#     #     return True

#     # horsepower if missing (75)
#     if (
#         car.link_mobile
#         == "https://www.mobile.bg/obiava-11749668026765654-toyota-yaris-1-4-d4d"
#     ):
#         return True

#     # needs a new engine (that is expensive)
#     if car.link_mobile == "https://www.mobile.bg/obiava-11749994255252093-skoda-fabia":
#         return True

#     # looks terrible
#     if car.link_mobile in [
#         "https://www.mobile.bg/obiava-11738432582242534-vw-new-beetle",
#         "https://www.mobile.bg/obiava-11750486418014720-vw-new-beetle-1-9-tdi-arte",
#     ]:
#         return True

#     return False

##########
########## some other shit
##########

CAR_DEALERSHIP_OK = True
# this is not accurate - it treats some non-dealers as dealers

NET_CACHE_LOC = str(Path(__file__).parent / "cache")
NET_CACHE_DURATION_MOBILEBG_SEC = 60 * 60 * 10  # 10h
NET_CACHE_DURATION_MOBILEBG_SPECIFIC_CAR_SEC = 60 * 60 * 24 * 30  # 1 month
NET_CACHE_DURATION_AUTODATA_SEC = 60 * 60 * 24 * 30  # 1 month
NET_HAD_TO_CONNECT_SLEEP = 0.8  # 0.4 is too little IN MULTITHREADED CONTEXT

MOBILE_PREFIX = "https://www.mobile.bg/"
URL = (
    MOBILE_PREFIX
    + "obiavi/avtomobili-dzhipove/oblast-sofiya/p-{page_num}?price={price_min}&price1={price_max}&sort=6&nup=014&pictonly=1"
)
# `sort=6` - sort by newest
# `pictonly=1` - only show if picture is available
#
# `namira-se-v-balgariya` - bulgaria
# `oblast-sofiya` - sofia

if not CAR_DEALERSHIP_OK:
    URL += "&privonly=1"

URL_PROTO = URL.split("//")[0]

MAX_PAGE = 150
# for some reason the website only allows for up to 150 pages

BS_PARSER = "html.parser"

EUR_TO_BGN = 1.95583

PRINT_FUEL_CONSUMPTION_EXTRACTION_WARNING = False
