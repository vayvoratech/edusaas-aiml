import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="eduai_db",
        user="postgres",
        password="YOUR_PASSWORD"
    )

    print("✅ Connection successful")
    conn.close()

except Exception as e:
    print(e)
    