"""
Amazon product scraper and HTML parser.
Extracts product specs, price, rating, reviews, and discounts from search pages.
"""

import re
import time
import random
import logging
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup

from .data_generator import generate_seed_catalog

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
]

BASE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}


class AmazonScraper:
    def __init__(self, domain: str = "amazon.in", timeout: int = 10):
        self.domain = domain
        self.base_url = f"https://www.{domain}"
        self.timeout = timeout
        self.session = requests.Session()

    def get_headers(self) -> Dict[str, str]:
        headers = BASE_HEADERS.copy()
        headers["User-Agent"] = random.choice(USER_AGENTS)
        return headers

    def extract_specs_from_title(self, title: str) -> Dict[str, Any]:
        """Extract RAM, storage, screen size, and processor from title using regex."""
        specs = {
            "ram_gb": 0,
            "storage_gb": 0,
            "screen_size_inches": 0.0,
            "processor": "Standard"
        }

        # RAM (e.g. 16GB RAM, 8 GB RAM)
        ram_match = re.search(r'(\d+)\s*(?:GB|gb)\s*(?:RAM|ram|DDR|ddr|Memory)?', title, re.IGNORECASE)
        if ram_match:
            val = int(ram_match.group(1))
            if val in [2, 3, 4, 6, 8, 12, 16, 24, 32, 64]:
                specs["ram_gb"] = val

        # Storage (e.g. 512GB SSD, 1TB)
        tb_match = re.search(r'(\d+)\s*(?:TB|tb)\s*(?:SSD|HDD|Storage|ROM)?', title, re.IGNORECASE)
        gb_match = re.search(r'(\d+)\s*(?:GB|gb)\s*(?:SSD|HDD|Storage|ROM|eMMC)', title, re.IGNORECASE)
        if tb_match:
            specs["storage_gb"] = int(tb_match.group(1)) * 1024
        elif gb_match:
            val = int(gb_match.group(1))
            if val in [32, 64, 128, 256, 512, 1024, 2048]:
                specs["storage_gb"] = val

        # Screen size (e.g. 15.6 inch, 14")
        screen_match = re.search(r'(\d{1,2}(?:\.\d{1,2})?)\s*(?:\"|\'|\-inch|inch|\s*inch)', title, re.IGNORECASE)
        if screen_match:
            try:
                screen_val = float(screen_match.group(1))
                if 1.0 <= screen_val <= 18.0:
                    specs["screen_size_inches"] = screen_val
            except ValueError:
                pass

        # Processor
        if re.search(r'\b(?:Apple\s+)?M[1-4]\b', title, re.IGNORECASE):
            m = re.search(r'\b(?:Apple\s+)?M[1-4]\s*(?:Pro|Max|Ultra)?\b', title, re.IGNORECASE)
            specs["processor"] = f"Apple {m.group(0).strip()}" if m and not m.group(0).startswith("Apple") else (m.group(0).strip() if m else "Apple Silicon")
        elif re.search(r'i[3579]-?\d{4,5}', title, re.IGNORECASE) or re.search(r'Core\s+i[3579]', title, re.IGNORECASE):
            specs["processor"] = "Intel Core"
        elif re.search(r'Ryzen\s+[3579]', title, re.IGNORECASE):
            specs["processor"] = "AMD Ryzen"
        elif re.search(r'Snapdragon\s+\d+', title, re.IGNORECASE):
            specs["processor"] = "Qualcomm Snapdragon"
        elif re.search(r'Dimensity\s+\d+', title, re.IGNORECASE):
            specs["processor"] = "MediaTek Dimensity"

        return specs

    def parse_product_element(self, item: BeautifulSoup, category: str) -> Optional[Dict[str, Any]]:
        try:
            asin = item.get("data-asin")
            if not asin or len(asin) < 5:
                return None

            title_elem = item.select_one("h2 a span") or item.select_one("h2 span")
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)
            if not title:
                return None

            price_elem = item.select_one("span.a-price span.a-offscreen") or item.select_one("span.a-price-whole")
            if not price_elem:
                return None
            price_raw = price_elem.get_text(strip=True)
            price_clean = re.sub(r'[^\d.]', '', price_raw)
            current_price = float(price_clean) if price_clean else 0.0
            if current_price <= 0:
                return None

            orig_elem = item.select_one("span.a-price.a-text-price span.a-offscreen")
            if orig_elem:
                orig_raw = orig_elem.get_text(strip=True)
                orig_clean = re.sub(r'[^\d.]', '', orig_raw)
                original_price = float(orig_clean) if orig_clean else current_price
            else:
                original_price = current_price

            discount_pct = round(((original_price - current_price) / original_price) * 100, 1) if original_price > current_price else 0.0

            rating_elem = item.select_one("span.a-icon-alt")
            rating = 4.0
            if rating_elem:
                r_text = rating_elem.get_text(strip=True)
                r_match = re.search(r'(\d+(?:\.\d+)?)', r_text)
                if r_match:
                    rating = float(r_match.group(1))

            rev_elem = item.select_one("span.a-size-base.s-underline-text") or item.select_one("span.a-size-base")
            review_count = 50
            if rev_elem:
                rev_text = rev_elem.get_text(strip=True)
                rev_clean = re.sub(r'[^\d]', '', rev_text)
                if rev_clean:
                    review_count = int(rev_clean)

            # Match brand from title
            brand = "Unknown"
            known_brands = ["Apple", "Samsung", "Dell", "HP", "Lenovo", "ASUS", "Acer", "MSI", "Sony", "Bose",
                            "OnePlus", "Xiaomi", "Realme", "Google", "Motorola", "Garmin", "boAt", "Noise", "Fire-Boltt"]
            for kb in known_brands:
                if kb.lower() in title.lower():
                    brand = kb
                    break
            if brand == "Unknown" and title.split():
                brand = title.split()[0]

            specs = self.extract_specs_from_title(title)

            if current_price <= 25000:
                price_tier = "Budget"
            elif current_price <= 65000:
                price_tier = "Mid-Range"
            else:
                price_tier = "Premium"

            is_prime = 1 if item.select_one("i.a-icon-prime") else 0

            return {
                "asin": asin,
                "title": title,
                "brand": brand,
                "category": category,
                "current_price": round(current_price, 2),
                "original_price": round(original_price, 2),
                "discount_percentage": discount_pct,
                "rating": rating,
                "review_count": review_count,
                "ram_gb": specs["ram_gb"],
                "storage_gb": specs["storage_gb"],
                "processor": specs["processor"],
                "screen_size_inches": specs["screen_size_inches"],
                "is_prime": is_prime,
                "in_stock": 1,
                "price_tier": price_tier,
                "product_url": f"{self.base_url}/dp/{asin}"
            }
        except Exception as e:
            logger.debug(f"Error parsing item: {e}")
            return None

    def scrape_category(self, query: str, category_name: str, max_pages: int = 2) -> List[Dict[str, Any]]:
        products = []
        for page in range(1, max_pages + 1):
            url = f"{self.base_url}/s?k={query}&page={page}"
            logger.info(f"Fetching {url}...")
            try:
                response = self.session.get(url, headers=self.get_headers(), timeout=self.timeout)
                if response.status_code == 503 or "Robot Check" in response.text:
                    logger.warning(f"Blocked by Amazon captcha (Status {response.status_code}).")
                    break

                soup = BeautifulSoup(response.text, "html.parser")
                items = soup.select('div[data-component-type="s-search-result"]')

                for itm in items:
                    parsed = self.parse_product_element(itm, category_name)
                    if parsed:
                        products.append(parsed)

                time.sleep(random.uniform(1.5, 3.0))

            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                break

        return products

    def collect_dataset(self, live: bool = False, count: int = 1200) -> List[Dict[str, Any]]:
        all_products = []
        if live:
            logger.info("Attempting live scrape...")
            queries = [
                ("laptops", "Laptops"),
                ("smartphones", "Smartphones"),
                ("headphones", "Headphones"),
                ("smartwatches", "Smartwatches"),
                ("tablets", "Tablets")
            ]
            for query, cat in queries:
                items = self.scrape_category(query, cat, max_pages=2)
                all_products.extend(items)

        # Fallback to local sample generator if scraping returned too few products or live=False
        if len(all_products) < 50:
            if live:
                logger.info("Live scrape got blocked or had too few items. Using generated sample data...")
            else:
                logger.info(f"Generating {count} sample products...")
            all_products = generate_seed_catalog(count)

        logger.info(f"Ready with {len(all_products)} products.")
        return all_products


if __name__ == "__main__":
    scraper = AmazonScraper()
    dataset = scraper.collect_dataset(live=False, count=50)
    print(f"Sample item: {dataset[0]}")
