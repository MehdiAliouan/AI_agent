# scraper.py

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
import pandas as pd
import re

# Same classification function
def get_component_type(title):
    title_lower = title.lower()
    if any(k in title_lower for k in ["processeur", "cpu", "ryzen", "intel core"]):
        return "CPU"
    elif any(k in title_lower for k in ["carte graphique", "gpu", "rtx", "radeon", "geforce"]):
        return "GPU"
    elif any(k in title_lower for k in ["ssd", "hdd", "disque", "nvme"]):
        return "Storage"
    elif any(k in title_lower for k in ["ram", "mémoire", "ddr4", "ddr5"]):
        return "RAM"
    elif any(k in title_lower for k in ["carte mère", "motherboard", "b550", "z790"]):
        return "Motherboard"
    else:
        return "Other"

def scrape_ultrapc_components_page(page, url):
    try:
        page.goto(url, timeout=10000)
        page.wait_for_timeout(2000)
        soup = BeautifulSoup(page.content(), "html.parser")
        components = []

        for product in soup.find_all("article", class_="product-miniature"):
            try:
                title_container = product.find("div", class_="thumbnail-container")
                link_tag = title_container.find("a", class_="product-thumbnail")
                title_text = link_tag.get_text(separator=" ", strip=True) or link_tag.get("title", "No title")

                img_tag = link_tag.find("img")
                brand = img_tag.get("alt", "").split()[0] if img_tag and img_tag.has_attr("alt") else "Unknown"

                flags = product.find("ul", class_="product-flags")
                promo = flags.get_text(separator=", ", strip=True) if flags else "N/A"

                price_tag = product.find("span", class_="price")
                price = price_tag.text.strip() if price_tag else "Price N/A"

                components.append({
                    "Brand": brand,
                    "Title": title_text,
                    "Price": price,
                    "Promotion": promo,
                    "Category": get_component_type(title_text)
                })
            except Exception:
                continue

        return components
    except Exception:
        return []

def scrape_and_save(base_url, max_pages=72):
    all_components = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for i in range(1, max_pages + 1):
            url = f"{base_url}?p={i}"
            print(f"Scraping page {i}")
            components = scrape_ultrapc_components_page(page, url)
            if not components:
                break
            all_components.extend(components)
        browser.close()
    df = pd.DataFrame(all_components)
    df.to_csv("components.csv", index=False)
    print("✅ Data saved to components.csv")

if __name__ == "__main__":
    BASE_URL = "https://www.ultrapc.ma/20-composants"
    scrape_and_save(BASE_URL, max_pages=72)