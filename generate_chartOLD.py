import os
import requests

# Notion API Token und Datenbank-ID aus Umgebungsvariablen lesen
NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def query_notion_database():
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    data = {}  # keine Filter, alle Einträge

    response = requests.post(url, headers=HEADERS, json=data)
    response.raise_for_status()
    results = response.json()["results"]
    return results

def count_predictions(results):
    correct = 0
    wrong = 0
    for page in results:
        props = page["properties"]
        # Annahme: Die Eigenschaft heißt "Prediction" und ist vom Typ number
        prediction_value = props.get("Prediction", {}).get("number")
        if prediction_value is None:
            continue

        # Annahme: prediction_value ist Anzahl der richtigen Predictions
        # Beispiel: richtig = prediction_value, falsch = (3 - prediction_value) wenn max 3 Predictions pro Rennen
        correct += prediction_value
        wrong += (3 - prediction_value)  # Anpassen, falls anders

    return correct, wrong

def generate_html(correct, wrong):
    total = correct + wrong
    percent_correct = (correct / total) * 100 if total > 0 else 0

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Prediction Chart</title>
      <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
      <style>
        body {{
          background: transparent;
          margin: 0;
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100vh;
        }}
        canvas {{
          max-width: 300px;
          max-height: 300px;
        }}
      </style>
    </head>
    <body>
      <canvas id="myChart"></canvas>
      <script>
        const data = {{
          labels: ['Correct', 'Wrong'],
          datasets: [{{
            data: [{correct}, {wrong}],
            backgroundColor: ['#4CAF50', '#F44336'],
            borderWidth: 1
          }}]
        }};

        const config = {{
          type: 'doughnut',
          data: data,
          options: {{
            responsive: true,
            plugins: {{
              legend: {{
                position: 'bottom',
              }},
              tooltip: {{
                enabled: true
              }}
            }}
          }}
        }};

        new Chart(
          document.getElementById('myChart'),
          config
        );
      </script>
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    results = query_notion_database()
    correct_predictions, wrong_predictions = count_predictions(results)
    print(f"Correct: {correct_predictions}, Wrong: {wrong_predictions}")

    generate_html(correct_predictions, wrong_predictions)
