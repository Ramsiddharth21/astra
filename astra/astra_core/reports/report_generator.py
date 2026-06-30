import json
from datetime import datetime


def save_report(report_data, filename="astra_report.json"):
    report_data["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4)

    return filename
