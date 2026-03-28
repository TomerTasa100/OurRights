import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage


def run_rights_expert_agent():
    load_dotenv()

    persist_directory = "chroma_db"

    # שולפים את המפתח בצורה מאובטחת
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("❌ לא נמצא מפתח API! ודא שיש לך קובץ .env עם OPENAI_API_KEY")

    os.environ["OPENAI_API_KEY"] = openai_key

    # ==========================================
    # שלב 1: הנתונים מהטופס של המשתמש (Frontend)
    # ==========================================
    user_form_data = {
        "status": "עובד שכיר",
        "disability_category": "נפגע פעולות איבה",
        "medical_condition": "נכות נפשית (פוסט טראומה)",
        "disability_percentage": 50  # שיניתי ל-50 כדי שנוכל להשוות ל-CSV שלך!
    }

    print(f"👤 נתוני המשתמש התקבלו: {user_form_data['disability_percentage']}% נכות...")

    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings_model)

    # ==========================================
    # שלב 2: Multi-Query Retrieval (מצב צלף)
    # ==========================================
    print("🔎 מפעיל מערך סוכני חיפוש מורחב (מצב צלף - מביא רק את המסמכים המדויקים ביותר)...")

    unique_docs = {}
    top_k = 10 # צמצמנו את הרעש! מביאים רק את ה-4 הכי חזקים לכל קטגוריה

    # 1. סוכן קצבאות ורפואה
    medical_query = f"זכויות, קצבאות, סכום תגמול חודשי, סל שיקום, וכלב שירות עבור {user_form_data['disability_category']} בשיעור {user_form_data['disability_percentage']}% נכות נפשית."
    for doc in vectorstore.similarity_search(medical_query, k=top_k): unique_docs[doc.page_content] = doc

    # 2. סוכן הנחות ופטורים
    discounts_query = f"מענק טלפון, פטור מארנונה, הנחה בחשמל, הנחה במים, פטורים מתשלום ותעודת נכה עבור {user_form_data['disability_percentage']}% נכות."
    for doc in vectorstore.similarity_search(discounts_query, k=top_k): unique_docs[doc.page_content] = doc

    # 3. סוכן ניידות ורכב
    mobility_query = f"רכב רפואי, אחזקת רכב, דמי נסיעה, טסט, חניה וביטוח רכב לנפגעי פעולות איבה בשיעור {user_form_data['disability_percentage']}%."
    for doc in vectorstore.similarity_search(mobility_query, k=top_k): unique_docs[doc.page_content] = doc

    # 4. סוכן משפחה, פנאי ודיור
    family_query = f"השתתפות בשכר דירה, מענק דירה, חימום, ציוד ביתי, דמי הבראה, טיפולים לבני משפחה וילדים."
    for doc in vectorstore.similarity_search(family_query, k=top_k): unique_docs[doc.page_content] = doc

    # 5. סוכן פרואקטיבי (לימודים)
    if user_form_data['disability_percentage'] >= 20:
        print("💡 מפעיל סוכן פרואקטיבי לשיקום מקצועי ולימודים...")
        proactive_query = f"שיקום מקצועי, יציאה ללימודים, מכינה, שיעורי עזר, מענקי מחשב ודמי מחיה לסטודנטים."
        for doc in vectorstore.similarity_search(proactive_query, k=top_k): unique_docs[doc.page_content] = doc

    final_results = list(unique_docs.values())

    print(f"\n🔎 סך הכל נשלפו {len(final_results)} מסמכים ייחודיים ורלוונטיים:")
    context_text = ""
    for i, doc in enumerate(final_results):
        doc_title = doc.metadata.get('Right Name', 'ללא שם')
        context_text += f"\n--- מסמך מקור {i + 1} ({doc_title}) ---\n"
        context_text += doc.page_content + "\n"

    # ==========================================
    # שלב 3: הפעלת מודל השפה (Generation)
    # ==========================================
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

    system_prompt = """
    אתה עוזר וירטואלי משפטי אולטרה-מדויק למיצוי זכויות. המטרה שלך היא להפיק רשימה של זכויות על בסיס הטקסט שסופק לך.

    🚨 חוקי ברזל - סכנת פסילה אם לא תעמוד בהם:
    1. **סינון אכזרי לפי אחוזי נכות (קריטי):** פרופיל המשתמש קובע את הכל. המשתמש מוגדר כ-50% נכות. אם אתה רואה במסמך זכות שמיועדת במפורש ולעיתים קרובות באופן בלעדי למדרגות נכות אחרות (כמו 10%-19%, או 100% מיוחדת) - **אסור לך להזכיר אותה לחלוטין!**
    2. **דיוק מתמטי:** אל תכתוב משפטים כלליים. חפש במדויק בטקסט את הסכום הרלוונטי למדרגת הנכות של המשתמש (50%) וציין רק אותו.
    3. **רזולוציה מקסימלית (ללא איגוד):** פרק את הזכויות. אל תאגד "הנחות בארנונה, חשמל ומים" לשורה אחת. הקדש שורה נפרדת לארנונה, שורה לחשמל, וכו'.
    4. **אמינות מוחלטת:** מותר לך להשתמש *אך ורק* בעובדות שמופיעות ב-Context. אל תמציא כלום (כמו הנחות שלא כתובות או הטבות שלא סופקו לך).
    5. **מבנה התשובה:** ענה אך ורק בעברית. חלק את התשובה לקטגוריות ברורות (קצבאות ומענקים, דיור והנחות, רכב וניידות, משפחה ופנאי, טיפולים רפואיים). הוסף בסוף סעיף "💡 אפשרויות לעתיד (אם תבחר ללמוד):" שיכלול את הזכויות הרלוונטיות ללימודים והכשרה מקצועית.
    """

    user_prompt = f"""
    פרופיל המשתמש:
    - סטטוס: {user_form_data['status']}
    - קטגוריה: {user_form_data['disability_category']}
    - מצב רפואי: {user_form_data['medical_condition']}
    - אחוזי נכות: {user_form_data['disability_percentage']}%

    מידע משפטי רשמי (Context):
    {context_text}

    הפק את רשימת הזכויות המדויקת והמפורטת ביותר, רק מה שרלוונטי ל-50% נכות:
    """

    print("🧠 מנתח את הנתונים ומייצר תשובה ממוקדת ומדויקת...\n")

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    response = llm.invoke(messages)

    print("=" * 60)
    print("✨ התשובה הסופית למשתמש (Frontend Output):")
    print("=" * 60)
    print(response.content)
    print("=" * 60)


if __name__ == "__main__":
    run_rights_expert_agent()