import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage


def run_rights_expert_agent(user_form_data):
    load_dotenv()
    persist_directory = "chroma_db"

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("❌ לא נמצא מפתח API! ודא שיש לך קובץ .env עם OPENAI_API_KEY")

    os.environ["OPENAI_API_KEY"] = openai_key

    pct = user_form_data['disability_percentage']
    condition = user_form_data['medical_condition']

    print(f"\n⏳ מריץ טסט לפרופיל: בן {user_form_data['age']}, {user_form_data['marital_status']}, {user_form_data['status']} עם {pct}% נכות...")

    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings_model)

    # ==========================================
    # שלב 2: Smart Routing
    # ==========================================
    unique_docs = {}
    top_k = 6

    condition_query = f"טיפולים נפשיים, פסיכולוג, קבוצות תמיכה, פיזיותרפיה, הידרותרפיה, טיפולי גב, ציוד והתאמות עבור {condition} לנפגעי פעולות איבה."
    for doc in vectorstore.similarity_search(condition_query, k=top_k): unique_docs[doc.page_content] = doc

    # תיקון 1: השאילתה עכשיו דינמית לחלוטין ומחפשת את האחוז הספציפי ולא 40%
    base_benefit_query = f"תגמול נכות חודשי קבוע, קצבת נכות, סכומי תגמול לפי מדרגות, סכום עבור {pct}% נכות לנפגע פעולת איבה."
    for doc in vectorstore.similarity_search(base_benefit_query, k=top_k): unique_docs[doc.page_content] = doc

    discounts_query = f"פטור מארנונה לנכה, הנחה בחשבון חשמל, הטבה בחשבון מים, פטור מתשלום במקום ציבורי לנפגעי איבה."
    for doc in vectorstore.similarity_search(discounts_query, k=top_k): unique_docs[doc.page_content] = doc

    if pct >= 20 or user_form_data['status'] == "סטודנט":
        proactive_query = "סטודנט, יציאה ללימודים, מכינה, שכר לימוד, שיעורי עזר, מענקי מחשב ודמי מחיה. דמי הבראה שנתיים."
        for doc in vectorstore.similarity_search(proactive_query, k=top_k): unique_docs[doc.page_content] = doc

    if pct >= 40:
        heavy_query = "רכב רפואי, ניידות, פטור ממס על רכב, הלוואה לרכב, סיוע בשכר דירה לרווק, ומענק חימום וקירור."
        for doc in vectorstore.similarity_search(heavy_query, k=top_k): unique_docs[doc.page_content] = doc

    final_results = list(unique_docs.values())

    context_text = ""
    for i, doc in enumerate(final_results):
        doc_title = doc.metadata.get('Right Name', 'ללא שם')
        context_text += f"\n--- מסמך מקור {i + 1} ({doc_title}) ---\n"
        context_text += doc.page_content + "\n"

    # ==========================================
    # שלב 3: הפעלת מודל השפה
    # ==========================================
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

    if user_form_data['status'] == "סטודנט":
        student_and_future_template = f"""
        **🎓 עקב היותך סטודנט עבור {pct}%:**
        [צור שורה לכל זכות אקדמית שמצאת. אם לא מצאת - אל תיצור שורה!]

        **💡 אפשרויות לעתיד עבור {pct}%:**
        [צור שורה לזכויות למימוש עתידי. אם לא מצאת - אל תיצור שורה!]
        """
        # תיקון 2: ביטול הוראת החיבור. המודל רק שולף ומציג בנפרד כדי לא להמציא סכומים
        stipend_instruction = "The user is a student. Extract the base monthly stipend for their disability percentage. Then, SEPARATELY, state the student living stipend (דמי מחיה) or the maximum income limit. DO NOT do math or add them together yourself."
    else:
        student_and_future_template = f"""
        **💡 אפשרויות לעתיד עבור {pct}%:**
        [צור שורה לזכויות עתידיות. אם לא מצאת - אל תיצור שורה!]
        """
        stipend_instruction = "Extract the regular monthly stipend amount corresponding exactly to the user's disability percentage tier."

    # תיקון 3: חוקים נוקשים לסינון רפואי והפרדה בין חודשי לחד-פעמי
    system_prompt = f"""
    You are an ultra-precise legal assistant specializing in Israeli Social Security (Bituach Leumi) and victims of hostile acts.
    Your task is to AGGREGATE information from ALL provided documents into a clean report.

    🚨 CRITICAL RULES FOR A CLEAN OUTPUT:
    1. **NO MATH:** Do not add numbers together. Extract the exact text and numbers as they appear.
    2. **MONTHLY VS. ONE-TIME:** Never place a huge one-time grant (מענק חד פעמי) under 'קצבאות שוטפות' (Monthly Stipends). Monthly means paid every month!
    3. **ABSOLUTE OMISSION RULE:** If you cannot find a specific amount or clear confirmation for a benefit, DO NOT mention it at all! NEVER write "לא צוין" or empty bullet points. Just skip the benefit entirely.
    4. **Monthly Stipend:** {stipend_instruction}
    5. **Medical Filtering:** Condition: {condition}. If the condition is purely physical (e.g., amputation, back), DO NOT offer mental health treatments (PTSD/Anxiety). If it's mental, DO NOT offer physical treatments. Exclude unrelated treatments like dental.

    📝 OUTPUT TEMPLATE (Must be in HEBREW):
    Populate the sections BELOW dynamically. ONLY create a bullet point if you have actual data to show. 
    Add the source document name at the end of each bullet point: (מקור: [Document Name]).

    **💰 קצבאות שוטפות עבור {pct}%:**
    - תגמול חודשי: [הכנס את הנתונים]
    [הוסף שורות רק לקצבאות שוטפות חודשיות נוספות שמצאת. אין להכניס מענקים חד פעמיים פה!]

    **📅 מענקים חד שנתיים עבור {pct}%:**
    [הוסף שורות אך ורק למענקים שמצאת בטקסט במפורש (חימום, קירור, ציוד, הבראה). ציין סכום ליד כל אחד. אם לא מצאת - מחק את כל הקטגוריה הזו!]

    **📉 הנחות ופטורים:**
    [הוסף שורות אך ורק להנחות שמצאת. אם לא מצאת כלום - מחק את הקטגוריה הזו!]

    **⚕️ טיפולים רפואיים ושיקום:**
    [הכנס טיפולים רלוונטיים בלבד לפי הסינון הרפואי. אם לא מצאת כלום - מחק את הקטגוריה!]

    {student_and_future_template}
    """

    user_prompt = f"""
    פרופיל המשתמש:
    - גיל: {user_form_data['age']}
    - מצב משפחתי: {user_form_data['marital_status']}
    - סטטוס: {user_form_data['status']}
    - אחוזי נכות: {user_form_data['disability_percentage']}%
    - מצב רפואי: {user_form_data['medical_condition']}

    מידע משפטי רשמי לבדיקה (Context):
    {context_text}

    אנא צור את הדוח. זכור: לעולם אל תרשום "לא נמצא" - פשוט התעלם מהסעיף אם אין לך מידע.
    """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    response = llm.invoke(messages)

    return response.content