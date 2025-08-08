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
def generate_html(accuracy, predictions):
    percent = round(accuracy * 100, 1)
    total_possible = len(predictions) * 3
    correct_predictions = sum(predictions)
    incorrect_predictions = total_possible - correct_predictions
    
    ring_color = "#ffffff"
    background_ring = "rgba(255,255,255,0.1)"
    text_color = "#ffffff"

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Prediction Accuracy</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body {{
      margin: 0;
      background-color: transparent;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    }}
    #chartContainer {{
      width: 300px;
      height: 300px;
      display: flex;
      justify-content: center;
      align-items: center;
    }}
    canvas {{
      background-color: transparent;
    }}
  </style>
</head>
<body>
  <div id="chartContainer">
    <canvas id="accuracyChart"></canvas>
  </div>
  <script>
    const accuracy = {percent};
    const correctPredictions = {correct_predictions};
    const incorrectPredictions = {incorrect_predictions};
    const ctx = document.getElementById('accuracyChart').getContext('2d');

    new Chart(ctx, {{
      type: 'doughnut',
      data: {{
        labels: ['Richtig', 'Falsch'],
        datasets: [{{
          data: [accuracy, 100 - accuracy],
          backgroundColor: ['{ring_color}', '{background_ring}'],
          borderWidth: 0
        }}]
      }},
      options: {{
        cutout: '75%',
        responsive: false,
        plugins: {{
          tooltip: {{ 
            enabled: true,
            callbacks: {{
              label: function(context) {{
                if (context.dataIndex === 0) {{
                  return 'Richtige Predictions: ' + correctPredictions;
                }} else {{
                  return 'Falsche Predictions: ' + incorrectPredictions;
                }}
              }}
            }}
          }},
          legend: {{ display: false }}
        }}
      }},
      plugins: [{{
        id: 'centerText',
        beforeDraw: (chart) => {{
          const {{ ctx, chartArea: {{ width, height }} }} = chart;
          ctx.save();
          
          // "Predictions" Label
          ctx.font = '14px -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif';
          ctx.fillStyle = '{text_color}';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText('Predictions', width / 2, height / 2 - 20);
          
          // Percentage
          ctx.font = 'bold 32px -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif';
          ctx.fillStyle = '{text_color}';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(accuracy + '%', width / 2, height / 2 + 10);
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
    generate_html(accuracy, predictions)
    print(f"✅ Prediction Accuracy Chart erstellt ({round(accuracy*100, 1)}%) → accuracy_chart.html")