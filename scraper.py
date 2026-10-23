import requests
from bs4 import BeautifulSoup
import json

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_price(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        el = soup.select_one("[data-price]")
        if el and el.get("data-price"):
            return int(el["data-price"])
        # تلاش جایگزین: اگر data-price نبود، از متن استخراج کن
        if el:
            text = el.get_text(strip=True).replace(",", "")
            if text.isdigit():
                return int(text)
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    data = {}
    # قیمت دلار آزاد
    data["dollar"] = fetch_price("https://www.tgju.org/profile/price_dollar_rl")
    # طلای ۱۸ عیار
    data["gold18"] = fetch_price("https://www.tgju.org/profile/geram18")
    # انس جهانی
    data["ounce"] = fetch_price("https://www.tgju.org/profile/gold_ounce")

    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved:", data)

if __name__ == "__main__":
    main()
