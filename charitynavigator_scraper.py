import json
import requests
from bs4 import BeautifulSoup
import sys

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
def get_top_charities(cause: str, state: str, limit: int = 10) -> list:
    url = "https://www.charitynavigator.org/search"

    params = {
        "causes": cause,
        "states": state,
        "page": 1,
        "pageSize": limit
    }

    resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "html.parser")

    charities = []

    # 🔑 Anchor on NAME (most stable element)
    name_tags = soup.find_all("h2", class_="tw-font-sofia-pro")

    for name_tag in name_tags[:limit]:
        name = name_tag.get_text(strip=True)

        # Move up to the charity card container
        card = name_tag.find_parent("div", class_="tw-col-span-12")
        if not card:
            continue

        # ---------- LOCATION ----------
        location_tag = card.find("div", class_="tw-mb-0 tw-text-gray-700 tw-text-base")
        if not location_tag:
            continue

        location_text = location_tag.get_text(strip=True)
        if "," not in location_text:
            continue

        city, state_code = [x.strip() for x in location_text.split(",", 1)]

        # ---------- CATEGORIES ----------
        category_tags = card.find_all("a", class_="base_SearchResultTag__mVjvy")
        categories = [c.get_text(strip=True) for c in category_tags]

        charities.append({
            "name": name,
            "city": city,
            "state": state_code,
            "cause": cause,
            "categories": categories
        })

    return charities


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print('py charitynavigator_scraper.py "Education" "CA"')
        return

    cause = sys.argv[1]
    state = sys.argv[2]

    results = get_top_charities(cause, state, limit=10)

    with open("top_10_charities.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("Saved output:")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
