import os
from final_rag_agent import run_rights_expert_agent

# יצירת תיקייה לשמירת תוצאות הטסטים
if not os.path.exists("test_results"):
    os.makedirs("test_results")

# ==========================================
# מאגר הפרופילים לבדיקה (Test Suite)
# ==========================================
test_profiles = [
    {
        "test_name": "01_low_disability_15_pct",
        "data": {
            "age": 30,
            "marital_status": "רווק",
            "status": "עובד שכיר",
            "disability_category": "נפגע פעולות איבה",
            "medical_condition": "15% נכות נפשית (חרדה קלה)",
            "disability_percentage": 15
        }
    },
    {
        "test_name": "02_max_physical_100_pct_married",
        "data": {
            "age": 42,
            "marital_status": "נשוי + 3",
            "status": "עובד שכיר",
            "disability_category": "נפגע פעולות איבה",
            "medical_condition": "100% נכות פיזית (קטיעת גפיים ופגיעות רסיסים קשות)",
            "disability_percentage": 100
        }
    },
    {
        "test_name": "03_mid_level_35_pct_unemployed",
        "data": {
            "age": 55,
            "marital_status": "גרוש",
            "status": "לא עובד",
            "disability_category": "נפגע פעולות איבה",
            "medical_condition": "35% נכות (פגיעת ראש ורסיסים)",
            "disability_percentage": 35
        }
    },
    {
        "test_name": "04_student_complex_46_pct",
        "data": {
            "age": 25,
            "marital_status": "רווק",
            "status": "סטודנט",
            "disability_category": "נפגע פעולות איבה",
            "medical_condition": "40% נכות נפשית (PTSD) ו-10% נכות פיזית (גב - פריצת דיסק)",
            "disability_percentage": 46
        }
    }
]

# ==========================================
# הרצת הטסטים
# ==========================================
print("🚀 מתחיל הרצת אוטומציית טסטים...")

for profile in test_profiles:
    test_name = profile["test_name"]
    user_data = profile["data"]

    try:
        # הרצת הסוכן שלנו!
        result_text = run_rights_expert_agent(user_data)

        # שמירת התוצאה לקובץ
        file_path = f"test_results/{test_name}.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# תוצאות טסט: {test_name}\n")
            f.write(
                f"**פרופיל:** {user_data['disability_percentage']}% נכות, {user_data['medical_condition']}, {user_data['status']}\n")
            f.write("=" * 60 + "\n\n")
            f.write(result_text)

        print(f"✅ טסט {test_name} הושלם בהצלחה! התוצאה נשמרה בתיקיית test_results.")

    except Exception as e:
        print(f"❌ שגיאה בטסט {test_name}: {e}")

print("\n🎉 כל הטסטים הסתיימו. בדוק את תיקיית test_results!")