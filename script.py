import requests
from bs4 import BeautifulSoup
import json
import os

URLS = [ 
    { "label": "Cars.BG", 
     "url": "https://www.cars.bg/carslist.php?filterOrderBy=2&subm=1&add_search=1&typeoffer=1&brandId=31&models%5B%5D=497&priceFrom=4000&priceTo=8000&conditions%5B%5D=4&conditions%5B%5D=1&locationId=17&radius=3&filterOrderBy=1" 
     },
     {"label" : "Mobile.BG - Pernik", 
      "url": "https://www.mobile.bg/obiavi/avtomobili-dzhipove/honda/civic/oblast-pernik?price=4000&price1=8000&sort=6&nup=014"
      },
      {
          "label": "Mobile.BG - Sofia",
          "url": "https://www.mobile.bg/obiavi/avtomobili-dzhipove/honda/civic/oblast-sofiya?price=4000&price1=8000&sort=6&nup=014"
      },
         {
          "label": "Auto.BG - Pernik",
          "url": "https://www.auto.bg/obiavi/avtomobili-dzhipove/honda/civic/oblast-pernik?nup=013&price=4000&price1=8000"
      },
       {
          "label": "Auto.BG - Sofia",
          "url": "https://www.auto.bg/obiavi/avtomobili-dzhipove/honda/civic/oblast-sofiya?nup=013&price=4000&price1=8000"
      },
]
SEEN_FILE = "seen_listings.json"

def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ Warning: seen_listings.json is empty or corrupted. Starting fresh.")
            return {}
    return {}



seen_listings = load_seen()

def log_new_listings_to_file(label, new_items):
    with open("new_listings.txt", "a", encoding="utf-8") as f:
        for title, link in new_items:
            f.write(f"[{label}] {title} - {link}\n")



def save_seen(data):
    with open(SEEN_FILE, "w") as f:
        json.dump(data, f)

def parse_listings(label, soup, url):
    results = []


    if "cars.bg" in url:
        listings = soup.select("#listContainer .offer-item")  # You'll need to verify this selector
        for listing in listings:
            a = listing.find("a", href=True)
            if a:
                title = listing.find("h5", class_="observable").get_text(strip=True)
                link = a["href"]
                results.append((title, link))

    elif "mobile.bg" in url:
        listings = soup.select(".ads2023 .item")[:-1]  # Listing rows
        for listing in listings:
            a = listing.find("a", href=True)
            if a:
                title = a.get_text(strip=True)
                link = "https:" + a["href"]
                results.append((title, link))

    elif "auto.bg" in url:
        listings = soup.select(".results .resultItem")  # May be same as mobile.bg
        for listing in listings:
            a = listing.find("a", href=True)
            if a:
                title = a.get_text(strip=True)
                link =  a['href']
                results.append((title, link))

    return results

def check_new_listings():
    for entry in URLS:
        label = entry["label"]
        url = entry["url"]
        print(f"\n🔍 Checking: {label}")

        try:
            headers = {"User-Agent": "Mozilla/5.0"}  # Avoid bot blocks
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
            listings = parse_listings(label, soup, url)

            new_items = []
            for title, link in listings:
                unique_id = link
                if unique_id not in seen_listings.get(label, set()):
                    new_items.append((title, link))
                    seen_listings.setdefault(label, []).append(unique_id)
                    save_seen(seen_listings)

            if new_items:
               log_new_listings_to_file(label, new_items)
            else:
                print(f"✅ No new listings for {label}.")

        except Exception as e:
            print(f"⚠️ Error checking {label}: {e}")

# Main loop
if __name__ == "__main__":
    check_new_listings()