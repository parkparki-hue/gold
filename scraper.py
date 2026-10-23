import requests
from bs4 import BeautifulSoup
import json
from dollar_price import get_dollar_price  # کتابخانه‌ای که اضافه کردی

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.8",
}

def fetch_price_by_row(url, row_key):
    """
    استخراج قیمت با استفاده از data-market-row (روش مقاوم‌تر).
    row_key برای دلار: price_dollar_rl
    row_key برای طلای ۱۸: geram18
    row_key برای انس: gold_ounce
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # روش ۱: پیدا کردن سطر با data-market-row و سپس اولین سلول با کلاس nf
        row = soup.find("tr", attrs={"data-market-row": row_key})
        if row:
            price_cell = row.find("td", class_="nf")
            if price_cell:
                text = price_cell.get_text(strip=True).replace(",", "")
                if text.isdigit():
                    return int(text)
            # اگر کلاس nf نبود، اولین سلول را امتحان کن
            first_cell = row.find("td")
            if first_cell:
                text = first_cell.get_text(strip=True).replace(",", "")
                if text.isdigit():
                    return int(text)

        # روش ۲ (Fallback): اگر سطر پیدا نشد، از data-price عمومی استفاده کن
        el = soup.select_one("[data-price]")
        if el and el.get("data-price"):
            return int(el["data-price"])

        return None
    except Exception as e:
        print(f"Error fetching {row_key} from {url}: {e}")
        return None

def main():
    data = {}

    # ۱. دلار (با استفاده از کتابخانه‌ای که نصب کردی)
    print("Fetching dollar price via library...")
    try:
        data["dollar"] = get_dollar_price()
    except Exception as e:
        print(f"Library error for dollar: {e}")
        data["dollar"] = None

    # ۲. طلای ۱۸ عیار (از صفحه پروفایل geram18)
    print("Fetching gold18 price...")
    data["gold18"] = fetch_price_by_row(
        "https://www.tgju.org/profile/geram18",
        "geram18"
    )

    # ۳. انس جهانی (از صفحه پروفایل gold_ounce)
    print("Fetching ounce price...")
    data["ounce"] = fetch_price_by_row(
        "https://www.tgju.org/profile/gold_ounce",
        "gold_ounce"
    )

    # بررسی نهایی
    print("--- Results ---")
    for key, val in data.items():
        if val is None:
            print(f"⚠️ {key}: FAILED (null)")
        else:
            print(f"✅ {key}: {val:,}")

    # ذخیره در فایل
    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved to prices.json")

if __name__ == "__main__":
    main()
