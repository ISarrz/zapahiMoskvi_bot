import os
import sqlite3
from datetime import datetime, timedelta

from flask import Flask, jsonify, Response, request

app = Flask(__name__)

# Базовая директория проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Боевая база бота
DATABASE_PATH = os.path.join(BASE_DIR, "data", "database.db")


def get_conn():
    """
    Открываем соединение с БД бота.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/api/placemarks")
def api_placemarks():
    """
    Возвращает approved-метки с координатами и категорией.

    Поддерживает:
      - period=all|week|month
      - date_from=YYYY-MM-DD
      - date_to=YYYY-MM-DD

    Если date_from/date_to заданы, они имеют приоритет над period.
    """

    period = request.args.get("period", "all").strip()      # all | week | month
    date_from = request.args.get("date_from", "").strip()   # YYYY-MM-DD
    date_to = request.args.get("date_to", "").strip()       # YYYY-MM-DD

    conn = get_conn()
    cur = conn.cursor()

    conditions = [
        "p.status = 'approved'",
        "p.latitude IS NOT NULL AND p.latitude <> ''",
        "p.longitude IS NOT NULL AND p.longitude <> ''",
    ]
    params = []

    # В БД p.datetime хранится как: DD.MM.YYYY HH:MM
    # Преобразуем к YYYY-MM-DD HH:MM:SS, чтобы можно было корректно сравнивать.
    normalized_dt = """
        (
            substr(p.datetime, 7, 4) || '-' ||
            substr(p.datetime, 4, 2) || '-' ||
            substr(p.datetime, 1, 2) || ' ' ||
            substr(p.datetime, 12, 5) || ':00'
        )
    """

    # Пользовательский диапазон имеет приоритет
    if date_from:
        conditions.append(f"{normalized_dt} >= ?")
        params.append(f"{date_from} 00:00:00")

    if date_to:
        conditions.append(f"{normalized_dt} <= ?")
        params.append(f"{date_to} 23:59:59")

    # Если диапазон не задан — используем быстрые фильтры
    if not date_from and not date_to:
        if period in ("week", "month"):
            now = datetime.now()
            cutoff = now - timedelta(days=7 if period == "week" else 30)
            conditions.append(f"{normalized_dt} >= ?")
            params.append(cutoff.strftime("%Y-%m-%d %H:%M:%S"))

    where_clause = " WHERE " + " AND ".join(conditions)

    cur.execute(
        f"""
        SELECT
            p.id,
            p.datetime,
            p.address,
            p.latitude,
            p.longitude,
            p.description,
            p.status,
            COALESCE(MIN(c.name), '') AS category
        FROM placemarks p
        LEFT JOIN placemarks_tags pt ON pt.placemark_id = p.id
        LEFT JOIN tags_categories tc ON tc.tag_id = pt.tag_id
        LEFT JOIN categories c ON c.id = tc.category_id
        {where_clause}
        GROUP BY
            p.id, p.datetime, p.address, p.latitude, p.longitude, p.description, p.status
        ORDER BY
            {normalized_dt} DESC
        """,
        params,
    )

    rows = cur.fetchall()
    conn.close()

    data = []
    for r in rows:
        raw_lat = (r["latitude"] or "").strip()
        raw_lon = (r["longitude"] or "").strip()

        try:
            lat = float(raw_lat.replace(",", "."))
            lon = float(raw_lon.replace(",", "."))
        except ValueError:
            continue

        data.append(
            {
                "id": r["id"],
                "lat": lat,
                "lon": lon,
                "address": r["address"] or "",
                "description": r["description"] or "",
                "datetime": r["datetime"] or "",
                "status": r["status"] or "",
                "category": r["category"] or "",
            }
        )

    return jsonify(data)


@app.route("/")
def index():
    # ВСТАВЬ СЮДА СВОЙ КЛЮЧ ЯНДЕКС.КАРТ
    YMAPS_API_KEY = "ВСТАВЬ_СЮДА_СВОЙ_API_KEY"

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <title>Чем пахнет Москва? — карта</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    html, body {{
      margin: 0;
      padding: 0;
      height: 100%;
    }}

    #controls {{
      padding: 10px 12px;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 14px;
      background: #ffffff;
      border-bottom: 1px solid #eee;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
    }}

    #map {{
      width: 100%;
      height: calc(100vh - 95px);
    }}

    .balloon-title {{
      font-weight: 600;
      font-size: 13px;
      margin-bottom: 4px;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}

    .balloon-body {{
      font-size: 12px;
      margin-bottom: 4px;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}

    .balloon-address {{
      font-size: 11px;
      color: #666;
      margin-bottom: 4px;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}

    .balloon-meta {{
      font-size: 10px;
      color: #999;
      margin-top: 2px;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}

    .legend {{
      width: 100%;
      margin-top: 4px;
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      font-size: 12px;
      color: #444;
    }}

    .legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    .legend-color {{
      width: 12px;
      height: 12px;
      border-radius: 999px;
      border: 1px solid #ccc;
    }}

    input, select, button {{
      font: inherit;
      padding: 4px 6px;
    }}
  </style>
</head>
<body>
  <div id="controls">
    <span>Быстрый фильтр:</span>
    <select id="periodFilter">
      <option value="all">За всё время</option>
      <option value="month">За последний месяц</option>
      <option value="week">За последнюю неделю</option>
    </select>

    <span style="margin-left: 8px;">с</span>
    <input type="date" id="dateFrom">

    <span>по</span>
    <input type="date" id="dateTo">

    <button id="applyRange">Применить</button>
    <button id="resetRange">Сбросить</button>

    <div class="legend" id="legend"></div>
  </div>

  <div id="map"></div>

  <script src="https://api-maps.yandex.ru/2.1/?apikey=3ad71976-36a9-44da-a66a-788e67b7831f&lang=ru_RU"
          type="text/javascript"></script>

  <script>
    // Ключи должны совпадать с categories.name в БД
    const CATEGORY_COLORS = {{
      "Технические": "#ec4899",
      "Природные": "#22c55e",
      "Человеческие": "#f97316"
    }};

    function buildLegend() {{
      const legend = document.getElementById('legend');
      legend.innerHTML = '';

      Object.keys(CATEGORY_COLORS).forEach(function(cat) {{
        const color = CATEGORY_COLORS[cat];
        const item = document.createElement('div');
        item.className = 'legend-item';

        const swatch = document.createElement('div');
        swatch.className = 'legend-color';
        swatch.style.backgroundColor = color;

        const label = document.createElement('span');
        label.textContent = cat;

        item.appendChild(swatch);
        item.appendChild(label);
        legend.appendChild(item);
      }});
    }}

    ymaps.ready(init);

    function init() {{
      var map = new ymaps.Map('map', {{
        center: [55.751244, 37.618423],
        zoom: 11,
        controls: ['zoomControl']
      }});

      var periodSelect = document.getElementById('periodFilter');
      var dateFromInput = document.getElementById('dateFrom');
      var dateToInput = document.getElementById('dateTo');
      var applyRangeBtn = document.getElementById('applyRange');
      var resetRangeBtn = document.getElementById('resetRange');

      function loadPoints() {{
        var period = periodSelect.value;
        var dateFrom = dateFromInput.value; // YYYY-MM-DD
        var dateTo = dateToInput.value;     // YYYY-MM-DD

        if (dateFrom && dateTo && dateFrom > dateTo) {{
          alert('Дата "с" не может быть позже даты "по"');
          return;
        }}

        var params = new URLSearchParams();
        params.append('period', period);

        if (dateFrom) {{
          params.append('date_from', dateFrom);
        }}
        if (dateTo) {{
          params.append('date_to', dateTo);
        }}

        var url = '/api/placemarks?' + params.toString();

        fetch(url)
          .then(function(response) {{
            return response.json();
          }})
          .then(function(points) {{
            map.geoObjects.removeAll();

            points.forEach(function(p) {{
              var title = p.description && p.description.length > 40
                ? p.description.slice(0, 40) + '…'
                : (p.description || 'Запах');

              var balloonHtml = '';

              if (p.description) {{
                balloonHtml += '<div class="balloon-title">' + title + '</div>';
                balloonHtml += '<div class="balloon-body">' + p.description + '</div>';
              }} else {{
                balloonHtml += '<div class="balloon-title">Запах</div>';
              }}

              if (p.address) {{
                balloonHtml += '<div class="balloon-address">' + p.address + '</div>';
              }}

              if (p.datetime) {{
                balloonHtml += '<div class="balloon-meta">' + p.datetime + '</div>';
              }}

              if (p.category) {{
                balloonHtml += '<div class="balloon-meta">Категория: ' + p.category + '</div>';
              }}

              var color = CATEGORY_COLORS[p.category] || '#3b82f6';

              var placemark = new ymaps.Placemark(
                [p.lat, p.lon],
                {{
                  balloonContent: balloonHtml,
                  hintContent: p.address || title
                }},
                {{
                  preset: 'islands#circleIcon',
                  iconColor: color
                }}
              );

              map.geoObjects.add(placemark);
            }});
          }})
          .catch(function(err) {{
            console.error('Ошибка загрузки точек', err);
          }});
      }}

      periodSelect.addEventListener('change', loadPoints);
      applyRangeBtn.addEventListener('click', loadPoints);

      resetRangeBtn.addEventListener('click', function() {{
        periodSelect.value = 'all';
        dateFromInput.value = '';
        dateToInput.value = '';
        loadPoints();
      }});

      buildLegend();
      loadPoints();
    }}
  </script>
</body>
</html>
"""
    return Response(html, mimetype="text/html; charset=utf-8")


if __name__ == "__main__":
    print("Используем базу:", DATABASE_PATH)
    app.run(debug=True, port=8000)
