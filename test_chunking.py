import os
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter


def test_chunking():
    # 1. הגדרת הכותרות שלפיהן נחתוך את המסמך
    headers_to_split_on = [
        ("#", "Right Name"),
        ("##", "Sub Section"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    # הפתרון לבאג הנתיבים: מוצאים את התיקייה שבה הסקריפט יושב באופן דינמי
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sample_file = os.path.join(script_dir, "smart_data", "right_1.md")

    if not os.path.exists(sample_file):
        print(f"❌ לא נמצא קובץ בנתיב המלא:\n{sample_file}")
        return

    with open(sample_file, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # ביצוע החיתוך
    header_splits = markdown_splitter.split_text(md_text)
    final_chunks = text_splitter.split_documents(header_splits)

    # הדפסה ל-QA
    print(f"✅ הקובץ חולק בהצלחה ל-{len(final_chunks)} חתיכות (Chunks).")
    print("\n" + "=" * 50)
    print("הנה החתיכה הראשונה להדגמה:")
    print("=" * 50)
    print(f"📝 תוכן הטקסט שייכנס ל-AI:\n{final_chunks[0].page_content}")
    print("-" * 50)
    print(f"🏷️ מטא-דאטה:\n{final_chunks[0].metadata}")
    print("=" * 50)


if __name__ == "__main__":
    test_chunking()