import requests
import math
import json

# Notion API Config
NOTION_TOKEN = "NOTION_TOKEN"
DATABASE_ID = "1e26839379ed802a9f96f7875c65dc6d"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Schritt 1: Datenbank-Einträge aus Notion abrufen
def get_notion_predictions():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    predictions = []
    has_more = True
    next_cursor = None

    while has_more:
        payload = {}
        if next_cursor:
            payload["start_cursor"] = next_cursor

        res = requests.post(url, headers=HEADERS, json=payload)
        data = res.json()

        for page in data.get("results", []):
            prediction_val = page["properties"]["Prediction"].get("number")
            if prediction_val is not None:  # nur gefahrene Rennen zählen
                predictions.append(prediction_val)

        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")

    return predictions

# Schritt 2: Accuracy berechnen
def calculate_accuracy(predictions):
    if not predictions:
        return 0
    sum_predictions = sum(predictions)
    count_races = len(predictions)
    accuracy = sum_predictions / (3 * count_races)
    return accuracy

# Schritt 3: HTML mit Chart.js generieren
def generate_html(accuracy):
    percent = round(accuracy * 100, 1)
    color = "#ffffff"  # Weißer Ring
    text_color = "#ffffff"

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Prediction Accuracy</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    html, body {{
      margin: 0;
      padding: 0;
      background: transparent;
    }}
    canvas {{
      display: block;
    }}
  </style>
</head>
<body>
  <canvas id="accuracyChart" width="300" height="300"></canvas>

  <script>
    const ctx = document.getElementById('accuracyChart').getContext('2d');

    const accuracy = {percent};

    const chart = new Chart(ctx, {{
      type: 'doughnut',
      data: {{
        datasets: [{{
          data: [accuracy, 100 - accuracy],
          backgroundColor: ['{color}', 'rgba(255,255,255,0.1)'],
          borderWidth: 0
        }}]
      }},
      options: {{
        cutout: '80%',
        responsive: true,
        animation: false,
        plugins: {{
          tooltip: {{ enabled: false }},
          legend: {{ display: false }}
        }}
      }},
      plugins: [{{
        id: 'centerText',
        beforeDraw: (chart) => {{
          const {{ ctx, chartArea: {{ width, height }} }} = chart;
          ctx.save();
          ctx.font = 'bold 32px Arial';
          ctx.fillStyle = '{text_color}';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(accuracy + '%', width / 2, height / 2);
        }}
      }}]
    }});
  </script>
</body>
</html>
"""
    with open("accuracy_chart.html", "w", encoding="utf-8") as f:
        f.write(html_content)

# Hauptlogik
if __name__ == "__main__":
    predictions = get_notion_predictions()
    accuracy = calculate_accuracy(predictions)
    generate_html(accuracy)
    print(f"✅ Prediction Accuracy Chart erstellt ({round(accuracy*100, 1)}%) → accuracy_chart.html")
