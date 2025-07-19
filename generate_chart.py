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

    # Schreibe die HTML-Datei (in docs/index.html oder index.html)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    # Beispielwerte, diese ersetzt du durch echte Werte aus Notion
    correct_predictions = 7
    wrong_predictions = 3

    generate_html(correct_predictions, wrong_predictions)
