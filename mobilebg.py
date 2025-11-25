#! /usr/bin/env python3

##########
########## TODAY
##########

# ...

##########
########## 2025.09.01
##########

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

from stuff import extract_car_links_from_website, extract_cars_data_from_links

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


if __name__ == "__main__":
    parse_cmdline()
