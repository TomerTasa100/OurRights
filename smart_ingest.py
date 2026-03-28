import json
import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import time
from tqdm import tqdm
from dotenv import load_dotenv  # הוספנו את הייבוא הזה

# טוענים את משתני הסביבה מקובץ ה-.env
load_dotenv()

# שולפים את המפתח בצורה מאובטחת
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ לא נמצא מפתח API! ודא שיש לך קובץ .env עם OPENAI_API_KEY")

# מאתחלים את הלקוח עם המפתח שנשאב מהקובץ
client = OpenAI(api_key=api_key)


def clean_and_extract_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # מוחקים תפריטים, סקריפטים ועיצובים שלא תורמים לטקסט
    for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
        element.decompose()
    return soup.get_text(separator='\n', strip=True)


def process_url_with_ai(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        raw_text = clean_and_extract_text(response.content)

        # אם העמוד ריק או שגיאת חסימה, נדלג
        if len(raw_text) < 100:
            return None

        # הפרומפט הנוקשה ל-AI: להוציא רק עובדות יבשות
        system_prompt = """
        You are an expert Israeli legal data extractor. 
        Read the following raw scraped text from an Israeli rights website (Bituach Leumi / Kol Zchut). 
        Extract the core information and format it EXACTLY in this Markdown structure, in Hebrew:

        # [Name of the Right/Benefit]
        **תנאי זכאות:** [Bullet points of exactly who is eligible, exact percentages required, etc.]
        **סכומים והטבות:** [Exact financial amounts, percentages, or benefits granted]
        **אופן המימוש:** [Forms to fill out, committees to attend, or portals to log into]

        Ignore menus, generic contact info, and fluff. If a section is not applicable, write "לא רלוונטי".
        Make it short, punchy, and highly accurate.
        """

        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # המודל הכי משתלם ומהיר למשימות כאלה
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": raw_text[:10000]}  # חותכים טקסטים ארוכים מדי כדי לחסוך טוקנים
            ],
            temperature=0.0  # אפס יצירתיות, אנחנו רוצים רק את העובדות האמיתיות
        )

        return completion.choices[0].message.content

    except Exception as e:
        print(f"\n❌ Error processing {url}: {e}")
        return None


def main():
    # קוראים את הלינקים שאספת
    with open('hostilities_sources.json', 'r', encoding='utf-8') as f:
        urls_data = json.load(f)

    # יוצרים תיקייה לקבצים הנקיים
    os.makedirs('smart_data', exist_ok=True)

    print(f"🚀 Starting Smart Ingest Pipeline for {len(urls_data)} URLs...")

    # עוברים על הלינקים עם מד התקדמות יפה (tqdm)
    for i, item in enumerate(tqdm(urls_data)):
        url = item['url']

        # מדלגים על לינקים טכניים ופסולת שעלו בשאיבה
        if "RssPage" in url or "#" in url or "Link2" in url:
            continue

        markdown_content = process_url_with_ai(url)

        if markdown_content:
            # שומרים כל זכות כקובץ נפרד
            filename = f"smart_data/right_{i + 1}.md"
            with open(filename, 'w', encoding='utf-8') as md_file:
                md_file.write(markdown_content)

        # השהייה קטנה של שנייה כדי לא להעמיס על ביטוח לאומי ולא לחטוף חסימה
        time.sleep(1)

    print("\n✅ All done! Check the 'smart_data' folder for the clean Markdown files.")


if __name__ == "__main__":
    main()