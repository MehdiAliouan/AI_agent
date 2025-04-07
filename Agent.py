import streamlit as st
from langchain_ollama import ChatOllama
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

# Initialize Ollama with your preferred local model
MODEL_NAME = "qwen2.5:3b"
llm = ChatOllama(model=MODEL_NAME, num_ctx=32000)

# Component classifier
def get_component_type(title):
    title_lower = title.lower()
    if any(keyword in title_lower for keyword in ["processeur", "cpu", "ryzen", "intel core"]):
        return "CPU"
    elif any(keyword in title_lower for keyword in ["carte graphique", "gpu", "rtx", "radeon", "geforce"]):
        return "GPU"
    elif any(keyword in title_lower for keyword in ["ssd", "hdd", "disque", "nvme"]):
        return "Storage"
    elif any(keyword in title_lower for keyword in ["ram", "mémoire", "ddr4", "ddr5"]):
        return "RAM"
    elif any(keyword in title_lower for keyword in ["carte mère", "motherboard", "b550", "z790"]):
        return "Motherboard"
    else:
        return "Other"

# Scrape one page
def scrape_ultrapc_components_page(page, url):
    page.goto(url)
    page.wait_for_timeout(2000)
    soup = BeautifulSoup(page.content(), "html.parser")
    components = []

    product_cards = soup.find_all("article", class_="product-miniature")

    for product in product_cards:
        try:
            title_container = product.find("div", class_="thumbnail-container")
            link_tag = title_container.find("a", class_="product-thumbnail")
            title_text = link_tag.get_text(separator=" ", strip=True)

            if not title_text:
                title_text = link_tag["title"] if link_tag.has_attr("title") else "No title"
                img_tag = link_tag.find("img")
                brand = img_tag.get("alt", "").split()[0] if img_tag and img_tag.has_attr("alt") else "Unknown"
            else:
                brand = title_text.split()[0]

            flags = product.find("ul", class_="product-flags")
            promo = flags.get_text(separator=", ", strip=True) if flags else "N/A"

            price_tag = product.find("span", class_="price")
            price = price_tag.text.strip() if price_tag else "Price N/A"

            category = get_component_type(title_text)

            components.append({
                "Brand": brand,
                "Title": title_text,
                "Price": price,
                "Promotion": promo,
                "Category": category
            })
        except Exception:
            continue

    return components

# Loop pages
def scrape_ultrapc_all_pages(base_url, max_pages=5):
    all_components = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for i in range(1, max_pages + 1):
            url = f"{base_url}?p={i}"
            st.info(f"🔄 Scraping page {i}...")
            components = scrape_ultrapc_components_page(page, url)
            if not components:
                break
            all_components.extend(components)
        browser.close()
    return all_components

# AI analysis
def analyze_component_trends(components):
    if not components:
        return "No components found."
    df = pd.DataFrame(components)
    summary = df.to_string(index=False)

    prompt = (
        f"Analyze the following PC component listings from Ultrapc.ma and provide insights on price ranges, popular brands, availability, and types of components. "
        f"Also, suggest which components are good deals within a price range of 3000dh to 4000dh:\n\n{summary}\n\nAI Analysis:"
    )

    return llm.invoke(prompt)

# Clean and convert price
def clean_price(df):
    df["Price (DH)"] = (
        df["Price"]
        .str.replace("DH", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.extract(r"(\d+)")
        .astype(float)
    )
    return df

# Visualize data
def show_visualizations(df):
    st.subheader("📊 Visualizations")

    # Category distribution
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    sns.countplot(data=df, x="Category", order=df["Category"].value_counts().index, palette="Set2", ax=ax1)
    ax1.set_title("Component Count by Category")
    ax1.set_xlabel("Component Type")
    ax1.set_ylabel("Count")
    st.pyplot(fig1)

    # Price per category
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df, x="Category", y="Price (DH)", ci=None, palette="Set3", ax=ax2)
    ax2.set_title("Average Price by Component Category")
    ax2.set_xlabel("Category")
    ax2.set_ylabel("Average Price (DH)")
    st.pyplot(fig2)

    # Top brands
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    top_brands = df["Brand"].value_counts().head(10)
    sns.barplot(x=top_brands.index, y=top_brands.values, palette="Paired", ax=ax3)
    ax3.set_title("Top 10 Brands by Number of Products")
    ax3.set_xlabel("Brand")
    ax3.set_ylabel("Count")
    st.pyplot(fig3)

# Main app
def main():
    st.set_page_config(page_title="UltraPC Scraper", layout="wide")
    st.title("🖥️ UltraPC.ma Component Scraper & AI Insights")

    if st.button("🚀 Scrape and Analyze"):
        base_url = "https://www.ultrapc.ma/20-composants"
        components = scrape_ultrapc_all_pages(base_url, max_pages=72)

        if components:
            df = pd.DataFrame(components)
            df = clean_price(df)

            st.success(f"✅ Scraped {len(df)} products.")
            st.dataframe(df)

            show_visualizations(df)

            st.subheader("🤖 AI-Powered Insights")
            with st.spinner("Generating insights..."):
                ai_output = analyze_component_trends(components)
                st.write(ai_output)
        else:
            st.error("❌ No component data found.")

if __name__ == "__main__":
    main()