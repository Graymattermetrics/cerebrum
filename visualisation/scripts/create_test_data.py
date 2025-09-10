from typing import Any
import pandas as pd
import random
from datetime import datetime, timedelta, time
import uuid


def generate_test_data(days: int = 30):
    new_data: list[dict[str, Any]] = []
    today = datetime.now()

    for i in range(days):
        current_date = today - timedelta(days=i)
        num_tests_today = random.choice([2, 3])

        morning_time = time(
            hour=random.randint(6, 10),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
        )
        morning_datetime = datetime.combine(current_date.date(), morning_time)

        morning_record = BASE_RECORD.copy()
        morning_record["id"] = str(uuid.uuid4())
        morning_record["blocking_round_duration"] = random.randint(1050, 1250)
        morning_record["fatigue_level"] = random.randint(5, 7)
        morning_record["date"] = (
            morning_datetime.isoformat(timespec="milliseconds") + "Z"
        )
        morning_record["local_date"] = morning_datetime.strftime("%d/%m/%Y")
        morning_record["local_time"] = morning_datetime.strftime("%H:%M:%S")
        morning_record["created_at"] = morning_datetime.strftime("%Y-%m-%d %H:%M:%S")
        new_data.append(morning_record)

        evening_time = time(
            hour=random.randint(17, 22),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
        )
        evening_datetime = datetime.combine(current_date.date(), evening_time)

        evening_record = BASE_RECORD.copy()
        evening_record["id"] = str(uuid.uuid4())
        evening_record["blocking_round_duration"] = random.randint(1280, 1450)
        evening_record["fatigue_level"] = random.randint(1, 4)
        evening_record["date"] = (
            evening_datetime.isoformat(timespec="milliseconds") + "Z"
        )
        evening_record["local_date"] = evening_datetime.strftime("%d/%m/%Y")
        evening_record["local_time"] = evening_datetime.strftime("%H:%M:%S")
        evening_record["created_at"] = evening_datetime.strftime("%Y-%m-%d %H:%M:%S")
        new_data.append(evening_record)

        if num_tests_today == 3:
            midday_time = time(
                hour=random.randint(12, 15),
                minute=random.randint(0, 59),
                second=random.randint(0, 59),
            )
            midday_datetime = datetime.combine(current_date.date(), midday_time)

            midday_record = BASE_RECORD.copy()
            midday_record["id"] = str(uuid.uuid4())
            # Score and fatigue are somewhere in between morning and evening levels
            midday_record["blocking_round_duration"] = random.randint(1200, 1350)
            midday_record["fatigue_level"] = random.randint(3, 5)
            midday_record["date"] = (
                midday_datetime.isoformat(timespec="milliseconds") + "Z"
            )
            midday_record["local_date"] = midday_datetime.strftime("%d/%m/%Y")
            midday_record["local_time"] = midday_datetime.strftime("%H:%M:%S")
            midday_record["created_at"] = midday_datetime.strftime("%Y-%m-%d %H:%M:%S")
            new_data.append(midday_record)

    return pd.DataFrame(new_data)


BASE_RECORD: dict[str, Any] = {
    "id": "190aab75-1c26-449a-8067-7739285266bc",
    "client_id": "Gcqp4RbdvH",
    "status_code": 0,
    "status": "success",
    "success": True,
    "message": "Test completed successfully",
    "test_duration": 39280,
    "number_of_rounds": 40,
    "blocking_round_duration": 1320,
    "cognitive_processing_index": 82,
    "machine_paced_baseline": 1998.1,
    "version": "4a2b6dacbd7b39afdf328034b3b58380cd2136a2",
    "fatigue_level": -1,
    "number_of_roll_mean_limit_exceedences": 0,
    "final_ratio": 1.6519396551724137,
    "block_count": 2,
    "lowest_block_time": 803.8709637051013,
    "highest_block_time": 1052.7855088137953,
    "block_range": 248,
    "final_block_diff": 248,
    "total_machine_paced_answers": 30,
    "total_machine_paced_correct_answers": 24,
    "total_machine_paced_incorrect_answers": 1,
    "total_machine_paced_no_response_answers": 5,
    "quickest_response": 658.1999998092651,
    "quickest_correct_response": 658.1999998092651,
    "slowest_response": 1457.5999999046326,
    "slowest_correct_response": 1197.2000000476837,
    "mean_machine_paced_answer_time": 879.7766666650772,
    "mean_correct_machine_paced_answer_time": 856.0708333353201,
    "date": "",
    "date_minute_offset": -60,
    "normalized_location": "Could not get location",
    "local_date": "",
    "local_time": "",
    "created_at": "",
}


if __name__ == "__main__":
    generated_df = generate_test_data(days=30)
    generated_df = generated_df.sort_values(by="created_at", ascending=True)

    output_filename = "generated_cogspeed_test_data.csv"
    generated_df.to_csv(output_filename, index=False)

    print(f"Successfully generated {len(generated_df)} test records.")
    print(f"Data saved to '{output_filename}'")
