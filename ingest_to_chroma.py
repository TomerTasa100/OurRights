import os
import shutil
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


def build_vector_db():
    # 1. הגדרות בסיסיות
    data_folder = "smart_data"
    persist_directory = "chroma_db"  # כאן יישמר מסד הנתונים שלנו

    # הכנס את מפתח ה-API שלך כאן
    os.environ["OPENAI_API_KEY"] = "REMOVEDproj-IWBCO7fdLn6aDP7jhodhqZHIchP3ItpVIZzl2H2gCyHYdtCz4E1YQCwJ7UNMJP_oHHRXnHduNJT3BlbkFJMq6l5MsX7VfD1G1O_YqMEEW5KHfiW73ojt3nNPVoJ035iQT0ZzJLXjQRtm4j5J7XN5WQZXmwwA"

    # אם כבר קיים מסד נתונים ישן, נמחק אותו כדי להתחיל נקי
    if os.path.exists(persist_directory):
        print("🗑️ Deleting old database...")
        shutil.rmtree(persist_directory)

    # 2. הגדרת כלי החיתוך (בדיוק כמו בטסט שעשינו)
    headers_to_split_on = [
        ("#", "Right Name"),
        ("##", "Sub Section"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

    all_chunks = []

    # 3. מעבר על כל קבצי ה-Markdown בתיקייה
    print(f"📂 Reading files from '{data_folder}'...")
    for filename in os.listdir(data_folder):
        if filename.endswith(".md"):
            file_path = os.path.join(data_folder, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                md_text = f.read()

            # חיתוך הקובץ
            header_splits = markdown_splitter.split_text(md_text)
            chunks = text_splitter.split_documents(header_splits)
            all_chunks.extend(chunks)

    print(f"✂️ Total chunks created: {len(all_chunks)}")

    # 4. יצירת ההטמעות (Embeddings) ושמירה ל-ChromaDB
    print("🧠 Converting text to vectors and saving to ChromaDB (this might take a few seconds)...")

    # משתמשים במודל ההטמעות החדש והזול של OpenAI
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

    vectorstore = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings_model,
        persist_directory=persist_directory
    )

    print(f"✅ Success! Vector Database built and saved to '{persist_directory}' folder.")


if __name__ == "__main__":
    build_vector_db()