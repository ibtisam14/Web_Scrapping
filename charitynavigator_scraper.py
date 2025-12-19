import json
import requests
from bs4 import BeautifulSoup
import sys
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def get_all_charities(cause: str, state: str) -> list:
    url = "https://www.charitynavigator.org/search"
    page = 1
    all_charities = []

    while True:
        print(f"Fetching page {page}...")

        params = {
            "causes": cause,
            "states": state,
            "page": page,
            "pageSize": 10  
        }

        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.content, "html.parser")

        name_tags = soup.find_all("h2", class_="tw-font-sofia-pro")

        # 🚨 Stop when no more results
        if not name_tags:
            break

        for name_tag in name_tags:
            name = name_tag.get_text(strip=True)

            card = name_tag.find_parent("div", class_="tw-col-span-12")
            if not card:
                continue

            location_tag = card.find("div", class_="tw-mb-0 tw-text-gray-700 tw-text-base")
            if not location_tag:
                continue

            location_text = location_tag.get_text(strip=True)
            if "," not in location_text:
                continue

            city, state_code = [x.strip() for x in location_text.split(",", 1)]

            category_tags = card.find_all("a", class_="base_SearchResultTag__mVjvy")
            categories = [c.get_text(strip=True) for c in category_tags]

            all_charities.append({
                "name": name,
                "city": city,
                "state": state_code,
                "cause": cause,
                "categories": categories
            })

        page += 1
        time.sleep(1)  # polite delay (IMPORTANT)

    return all_charities


def main():
    if len(sys.argv) < 3:
        print('Usage: py charitynavigator_scraper.py "Education" "CA"')
        return

    cause = sys.argv[1]
    state = sys.argv[2]

    results = get_all_charities(cause, state)

    output_file = f"charities_{cause}_{state}.json".replace(" ", "_")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Saved {len(results)} records to {output_file}")


if __name__ == "__main__":
    main()
