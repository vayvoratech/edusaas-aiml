import os
import csv
import psycopg2

# ==========================
# PostgreSQL Connection
# ==========================
conn = psycopg2.connect(
    host="localhost",
    database="Gap_Analysis",
    user="postgres",
    password="Postgres2928@@",
    port="5432"
)

cursor = conn.cursor()

QUESTION_FOLDER = "question_bank"

total_inserted = 0
total_skipped = 0


# ======================================
# Read Every CSV File
# ======================================
for filename in os.listdir(QUESTION_FOLDER):

    if not filename.endswith(".csv"):
        continue

    filepath = os.path.join(QUESTION_FOLDER, filename)

    print(f"\nImporting {filename}...")

    with open(filepath, "r", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        inserted = 0
        skipped = 0

        for row in reader:

            # -----------------------------------
            # Get Skill ID
            # -----------------------------------
            cursor.execute("""
                SELECT skill_id
                FROM skill
                WHERE LOWER(skill_name)=LOWER(%s)
            """, (row["skill_name"],))

            skill = cursor.fetchone()

            if skill is None:
                print(f"Skill Not Found : {row['skill_name']}")
                continue

            skill_id = skill[0]

            # -----------------------------------
            # Get Difficulty ID
            # -----------------------------------
            cursor.execute("""
                SELECT difficulty_id
                FROM difficulty_levels
                WHERE LOWER(difficulty_name)=LOWER(%s)
            """, (row["difficulty"],))

            difficulty = cursor.fetchone()

            if difficulty is None:
                print(f"Difficulty Not Found : {row['difficulty']}")
                continue

            difficulty_id = difficulty[0]

            # -----------------------------------
            # Duplicate Check
            # -----------------------------------
            cursor.execute("""
                SELECT 1
                FROM questions
                WHERE question_text=%s
                AND skill_id=%s
            """, (
                row["question_text"],
                skill_id
            ))

            if cursor.fetchone():

                skipped += 1
                continue

            # -----------------------------------
            # Insert Question
            # -----------------------------------
            cursor.execute("""
                INSERT INTO questions
                (
                    skill_id,
                    difficulty_id,
                    question_text,
                    option_a,
                    option_b,
                    option_c,
                    option_d,
                    correct_option,
                    explanation,
                    marks,
                    is_active
                )
                VALUES
                (
                    %s,%s,%s,
                    %s,%s,%s,%s,
                    %s,%s,%s,%s
                )
            """, (

                skill_id,
                difficulty_id,

                row["question_text"],

                row["option_a"],
                row["option_b"],
                row["option_c"],
                row["option_d"],

                row["correct_option"],

                row["explanation"],

                int(row["marks"]),

                row["is_active"].strip().lower() == "true"

            ))

            inserted += 1

        conn.commit()

        total_inserted += inserted
        total_skipped += skipped

        print(f"Inserted : {inserted}")
        print(f"Skipped  : {skipped}")


cursor.close()
conn.close()

print("\n===============================")
print("IMPORT COMPLETED")
print("===============================")
print(f"Total Inserted : {total_inserted}")
print(f"Total Skipped  : {total_skipped}")
print("===============================")