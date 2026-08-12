import random
from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy import text

from src.database.database_connection import engine

fake = Faker()

FRAUD_PERCENTAGE = 0.08


def update_enrollments(connection):

    print("Updating enrollments...")

    result = connection.execute(

        text(
            """
            SELECT enrollment_id
            FROM enrollments
            """
        )

    )

    enrollment_ids = [row[0] for row in result]

    fraud_count = 0

    for enrollment_id in enrollment_ids:

        fraud = 1 if random.random() < FRAUD_PERCENTAGE else 0

        if fraud:

            fraud_count += 1

            payment_status = random.choice(
                ["FAILED", "PENDING"]
            )

            enrollment_source = random.choice(
                ["BOT", "API"]
            )

            enrollment_status = "SUSPICIOUS"

        else:

            payment_status = "PAID"

            enrollment_source = random.choice(
                ["WEB", "MOBILE"]
            )

            enrollment_status = "ACTIVE"

        connection.execute(

            text(
                """
                UPDATE enrollments
                SET
                    payment_status = :payment_status,
                    enrollment_source = :source,
                    enrollment_status = :status,
                    is_fraud = :fraud
                WHERE enrollment_id = :id
                """
            ),

            {
                "payment_status": payment_status,
                "source": enrollment_source,
                "status": enrollment_status,
                "fraud": fraud,
                "id": enrollment_id
            }

        )

    print(f"Fraud Enrollments : {fraud_count}")


def update_activity_logs(connection):

    print("Updating activity logs...")

    result = connection.execute(

        text(
            """
            SELECT activity_id
            FROM activity_logs
            """
        )

    )

    activity_ids = [row[0] for row in result]

    for activity_id in activity_ids:

        fraud = random.random() < FRAUD_PERCENTAGE

        if fraud:

            login_count = random.randint(150, 500)
            device_count = random.randint(3, 8)
            ip_changes = random.randint(5, 20)
            score = round(random.uniform(75, 100), 2)

        else:

            login_count = random.randint(5, 60)
            device_count = random.randint(1, 2)
            ip_changes = random.randint(0, 2)
            score = round(random.uniform(0, 40), 2)

        connection.execute(

            text(
                """
                UPDATE activity_logs
                SET
                    login_count = :login_count,
                    device_count = :device_count,
                    ip_changes = :ip_changes,
                    last_activity = :last_activity,
                    suspicious_activity_score = :score
                WHERE activity_id = :id
                """
            ),

            {
                "login_count": login_count,
                "device_count": device_count,
                "ip_changes": ip_changes,
                "last_activity": fake.date_time_between(
                    start_date="-30d",
                    end_date="now"
                ),
                "score": score,
                "id": activity_id
            }

        )


def main():

    with engine.begin() as connection:

        update_enrollments(connection)

        update_activity_logs(connection)

    print("\nFraud Data Updated Successfully.")


if __name__ == "__main__":

    main()