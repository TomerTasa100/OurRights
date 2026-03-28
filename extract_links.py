import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import time
import random


def extract_hostilities_links():
    target_url = "https://www.btl.gov.il/benefits/Victims_of_Hostilities/Pages/default.aspx"

    # 1. תחפושת מושלמת של דפדפן (Headers)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.google.com/",  # "הגענו" מחיפוש בגוגל
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    print(f"🔍 Fetching links from: {target_url}...")

    # 2. השהייה אקראית (כדי להיראות אנושיים)
    delay = random.uniform(1.5, 3.5)
    time.sleep(delay)

    try:
        # 3. הוספת Timeout כדי שהסקריפט לא ייתקע לנצח
        response = requests.get(target_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error (Might be blocked by WAF): {e}")
        return
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a')
    extracted_urls = set()

    for link in links:
        href = link.get('href')
        if not href:
            continue

        full_url = urljoin(target_url, href)

        if "/Victims_of_Hostilities/" in full_url and full_url != target_url:
            if not full_url.lower().endswith(('.pdf', '.doc', '.docx', 'print=true')):
                extracted_urls.add(full_url)

    output_data = [{"category": "נפגעי איבה", "url": url} for url in extracted_urls]

    with open('hostilities_sources.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f"✅ Successfully extracted {len(extracted_urls)} unique links!")


if __name__ == "__main__":
    extract_hostilities_links()