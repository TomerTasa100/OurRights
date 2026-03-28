import requests
from bs4 import BeautifulSoup
import json
import time
import random

# רשימת User-Agents כדי להיראות כמו גולשים שונים ולא כמו רובוט
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
]


def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    }


def fetch_bituach_leumi_sitemap():
    print("🔍 סורק את מפת האתר של ביטוח לאומי...")
    # בהרבה אתרי ממשלה מפת האתר נמצאת בכתובת הזו
    sitemap_url = "https://www.btl.gov.il/sitemap.xml"

    # מילות המפתח ב-URL שמעידות שזה קשור לנפגעי איבה או שיקום
    keywords = ["Victims_of_Hostilities", "Vocational_Rehabilitation", "איבה", "שיקום"]

    found_links = []
    try:
        response = requests.get(sitemap_url, headers=get_random_headers(), timeout=20)

        # אם אין מפת אתר ציבורית או שנחסמנו
        if response.status_code != 200:
            print(f"⚠️ לא הצלחתי לגשת למפת האתר של ביטוח לאומי (סטטוס: {response.status_code}).")
            return found_links

        # מפענחים את ה-XML
        soup = BeautifulSoup(response.content, 'xml')
        urls = soup.find_all('loc')

        for url_tag in urls:
            url = url_tag.text
            # אם הלינק מכיל אחת ממילות המפתח, נשמור אותו
            if any(keyword.lower() in url.lower() for keyword in keywords):
                # נסנן קבצי PDF או וורד - אנחנו רוצים רק דפי HTML
                if not url.lower().endswith(('.pdf', '.xlsx', '.doc', '.docx')):
                    found_links.append({
                        "source": "ביטוח לאומי",
                        "url": url,
                        "category": "נפגעי איבה / שיקום"
                    })
        print(f"✅ נמצאו {len(found_links)} לינקים רלוונטיים בביטוח לאומי.")
    except Exception as e:
        print(f"❌ שגיאה בסריקת ביטוח לאומי: {e}")

    return found_links


def fetch_kol_zchut_portal():
    print("🔍 סורק את פורטל 'נפגעי פעולות איבה' באתר כל זכות...")
    portal_url = "https://www.kolzchut.org.il/he/פורטל:נפגעי_פעולות_איבה"
    base_url = "https://www.kolzchut.org.il"

    found_links = []
    try:
        response = requests.get(portal_url, headers=get_random_headers(), timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # כל זכות שמים את רוב הלינקים החשובים בתוך ה-Body
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']

            # אנחנו רוצים רק לינקים פנימיים למאמרים (מתחילים ב-/he/ ולא דפי מערכת שמכילים ':')
            if href.startswith('/he/') and ':' not in href[4:]:
                full_url = base_url + href
                title = a_tag.text.strip()

                # מוודאים שזה לינק אמיתי ולא כפילות
                if len(title) > 2 and not any(link['url'] == full_url for link in found_links):
                    found_links.append({
                        "source": "כל זכות",
                        "url": full_url,
                        "category": "כל זכות - נפגעי איבה"
                    })
        print(f"✅ נמצאו {len(found_links)} לינקים רלוונטיים ב'כל זכות'.")
    except Exception as e:
        print(f"❌ שגיאה בסריקת כל זכות: {e}")

    return found_links


def main():
    print("🚀 מתחיל תהליך גילוי לינקים (URL Discovery)...\n")

    btl_links = fetch_bituach_leumi_sitemap()

    # השהייה אקראית כדי לחקות התנהגות אנושית בין האתרים
    time.sleep(random.uniform(2.5, 4.5))

    kol_zchut_links = fetch_kol_zchut_portal()

    all_links = btl_links + kol_zchut_links

    # שומרים את האוצר שלנו לקובץ JSON
    output_file = "all_potential_links.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_links, f, ensure_ascii=False, indent=4)

    print(f"\n🎉 התהליך הושלם! {len(all_links)} לינקים נשמרו בהצלחה לקובץ '{output_file}'.")


if __name__ == "__main__":
    main()