import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


def test_vector_search():
    persist_directory = "chroma_db"

    # הכנס את מפתח ה-API שלך כאן
    os.environ["OPENAI_API_KEY"] = "REMOVEDproj-IWBCO7fdLn6aDP7jhodhqZHIchP3ItpVIZzl2H2gCyHYdtCz4E1YQCwJ7UNMJP_oHHRXnHduNJT3BlbkFJMq6l5MsX7VfD1G1O_YqMEEW5KHfiW73ojt3nNPVoJ035iQT0ZzJLXjQRtm4j5J7XN5WQZXmwwA"

    # 1. טעינת מסד הנתונים הקיים (ChromaDB לא יבנה אותו מחדש, רק יקרא ממנו)
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings_model
    )

    # 2. השאלה המורכבת שלנו (כאן ה"קסם" נבחן)
    query = "אני סטודנט להנדסת תוכנה, מוכר כנפגע פעולות איבה עם 46% נכות נפשית. האם אני זכאי למימון שכר לימוד ללימודי התואר ודמי מחיה?"

    print(f"🔎 מחפש תשובות לשאילתה:\n'{query}'\n")

    # 3. ביצוע החיפוש! נבקש את ה-3 התוצאות הכי רלוונטיות (k=3)
    results = vectorstore.similarity_search(query, k=3)

    # 4. הדפסת התוצאות ל-QA
    if not results:
        print("❌ לא נמצאו תוצאות רלוונטיות במסד הנתונים.")
        return

    print("🎯 נמצאו התוצאות הבאות (מהכי רלוונטית להכי פחות):")
    for i, doc in enumerate(results):
        print("\n" + "=" * 50)
        print(f"תוצאה #{i + 1}")
        print(f"🏷️ מקור (Metadata): {doc.metadata}")
        print("-" * 50)
        print(f"📝 טקסט שנשלף:\n{doc.page_content}")
    print("=" * 50)


if __name__ == "__main__":
    test_vector_search()