import requests
import os

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_NAME = "F1 2025 Calendar"
PREDICTION_PROPERTY = "Prediction"

# 1. Hole Datenbank-ID
def get_database_id():
    url = "https://api.notion.com/v1/search"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }
    data = {
        "query": DATABASE_NAME,
        "filter": {
            "value": "database",
            "property": "object"
        }
    }
    res = requests.post(url, headers=headers, json=data)
    res.raise_for_status()
    results = res.json()["results"]
    return results[0]["id"]

# 2. Hole Einträge aus der Datenbank
def get_predictions(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28"
    }
    res = requests.post(url, headers=headers)
    res.raise_for_status()
    entries = res.json()["results"]

    total_correct = 0
    total_races = 0

    for entry in entries:
        props = entry["properties"]
        if PREDICTION_PROPERTY in props:
            prediction = props[PREDICTION_PROPERTY]
            if prediction["type"] == "number" and prediction["number"] is not None:
                total_correct += prediction["number"]
                total_races += 1

    return total_correct, total_races * 3 - total_correct

# 3. HTML-Template laden und ersetzen
def generate_html(correct, wrong):
    with open("template.html", "r") as f:
        template = f.read()

    success = round((correct / (correct + wrong)) * 100, 1) if (correct + wrong) > 0 else 0.0

    output = template.replace("{{CORRECT}}", str(correct)) \
                     .replace("{{WRONG}}", str(wrong)) \
                     .replace("{{PERCENT}}", str(success))

    with open("index.html", "w") as f:
        f.write(output)

if __name__ == "__main__":
    db_id = get_database_id()
    correct, wrong = get_predictions(db_id)
    generate_html(correct, wrong)
