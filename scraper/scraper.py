#!/usr/bin/env python3
"""
Web Scraping & Data Extraction Script
Target: books.toscrape.com (Public benchmark dataset)
Extracts structured catalog records and transmits them to n8n webhook pipeline.
"""

import sys
import os
import re
import json
import argparse
import datetime
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://books.toscrape.com/"
CATALOG_URL = "http://books.toscrape.com/catalogue/page-1.html"

def scrape_catalog(limit=20):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    print(f"[*] Requesting catalog: {CATALOG_URL}")
    response = requests.get(CATALOG_URL, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.select("article.product_pod")

    if not articles:
        raise ValueError("Scraper failed: No product elements found on page.")

    records = []
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for idx, art in enumerate(articles[:limit]):
        # Extract title
        title_tag = art.select_one("h3 a")
        title = title_tag.get("title", "").strip() if title_tag else ""
        if not title and title_tag:
            title = title_tag.get_text().strip()

        # Extract product relative link and generate unique ID
        rel_link = title_tag.get("href", "") if title_tag else ""
        product_url = urljoin(CATALOG_URL, rel_link)
        
        # Extract unique SKU / product identifier from URL
        sku_match = re.search(r"_(\d+)/index\.html", rel_link)
        sku = f"PROD-{sku_match.group(1)}" if sku_match else f"PROD-{(idx+1):04d}"

        # Extract price
        price_tag = art.select_one("div.product_price p.price_color")
        price_raw = price_tag.get_text().strip() if price_tag else ""

        # Extract rating class
        rating_tag = art.select_one("p.star-rating")
        rating_classes = rating_tag.get("class", []) if rating_tag else []
        rating_raw = [c for c in rating_classes if c != "star-rating"]
        rating_raw = rating_raw[0] if rating_raw else "Not Rated"

        # Extract availability
        avail_tag = art.select_one("div.product_price p.instock")
        avail_raw = avail_tag.get_text().strip() if avail_tag else ""

        # Extract image URL
        img_tag = art.select_one("div.image_container img")
        img_rel = img_tag.get("src", "") if img_tag else ""
        image_url = urljoin(CATALOG_URL, img_rel)

        record = {
            "sku": sku,
            "title_raw": title,
            "price_raw": price_raw,
            "rating_raw": rating_raw,
            "availability_raw": avail_raw,
            "product_url": product_url,
            "image_url": image_url,
            "source": "books.toscrape.com",
            "category_raw": "Books",
            "scraped_at": now_iso
        }
        records.append(record)

    return records

def main():
    parser = argparse.ArgumentParser(description="Web Scraping Engine for n8n Pipeline")
    parser.add_argument("--limit", type=int, default=20, help="Number of records to scrape")
    parser.add_argument("--output", type=str, default="scraper/scraped_data.json", help="Path to save output JSON")
    parser.add_argument("--post-to", type=str, default=None, help="n8n Webhook URL to deliver scraped payload")

    args = parser.parse_args()

    records = scrape_catalog(limit=args.limit)
    print(f"[+] Scraped {len(records)} records successfully.")

    # Save to local JSON
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"[+] Saved records to {args.output}")

    # Optional POST to n8n Webhook
    if args.post_to:
        print(f"[*] Transmitting {len(records)} items to n8n webhook: {args.post_to}")
        try:
            resp = requests.post(args.post_to, json=records, timeout=30)
            print(f"[+] Webhook response [{resp.status_code}]: {resp.text[:300]}")
        except Exception as e:
            print(f"[-] Webhook delivery failed: {e}")

if __name__ == "__main__":
    main()
