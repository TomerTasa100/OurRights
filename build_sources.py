import requests
from bs4 import BeautifulSoup
import json
import urllib.parse


def scrape_portal_directly():
    print("🚀 שואב נתונים ישירות מהדלת הקדמית של 'כל זכות'...")

    # הכתובת המעודכנת של הפורטל הראשי
    portal_url = "https://www.kolzchut.org.il/he/נפגעי_פעולות_איבה"
    base_url = "https://www.kolzchut.org.il"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    sources_data = []
    seen_urls = set()

    try:
        response = requests.get(portal_url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # מוצאים את כל הלינקים בעמוד
        links = soup.find_all('a', href=True)

        for link in links:
            href = link['href']

            # אנחנו מחפשים רק לינקים פנימיים למאמרים (שמתחילים ב-/he/ ולא מכילים נקודתיים של דפי מערכת)
            if href.startswith('/he/') and ':' not in href[4:]:

                # מפענחים את הכתובת (URL Decoding) כדי להימנע מתווים מוזרים כמו %D7
                decoded_href = urllib.parse.unquote(href)
                full_url = base_url + decoded_href

                # מסננים עמודי אינדקס ודפי "אודות" למיניהם
                if full_url not in seen_urls and not any(
                        bad_word in full_url for bad_word in ["אודות", "צור_קשר", "קטגוריה"]):
                    seen_urls.add(full_url)
                    sources_data.append({"url": full_url})

        print(f"✅ נשאבו בהצלחה {len(sources_data)} זכויות מדויקות מהפורטל!")

    except Exception as e:
        print(f"❌ שגיאה בשאיבת העמוד: {e}")

    output_filename = 'hostilities_sources.json'
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(sources_data, f, ensure_ascii=False, indent=4)

    print(f"🎉 הקובץ '{output_filename}' מוכן לעבודה! מכיל {len(sources_data)} לינקים.")


if __name__ == "__main__":
    scrape_portal_directly()