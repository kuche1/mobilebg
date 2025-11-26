from bs4 import BeautifulSoup


def extract_autodata_float(
    soup: BeautifulSoup, prefix: str, suffix: str
) -> float | None:
    elem = soup.find("td", string=prefix)
    if elem is None:
        return None
    value = elem.parent.text

    value = value.replace("\n", " ").replace("\t", " ")
    while "  " in value:
        value = value.replace("  ", " ")
    value = value.strip()

    if value == prefix:
        # the column exists, but the data is empty
        return None

    tmp = prefix + " "
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

    if "(" in value:
        part1, part2 = value.split("(")

        part1 = part1.removesuffix(" ")
        part2 = part2.removesuffix(")")

        part1 = float(part1)
        part2 = float(part2)
        value = max(part1, part2)

    elif "-" in value:
        part1, part2 = value.split("-")

        part1 = float(part1)
        part2 = float(part2)
        value = max(part1, part2)

    else:
        value = float(value)

    return value
