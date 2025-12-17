import os
import sqlite3
from flask import Flask, jsonify, Response

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'data', "database.db")

def get_conn():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_placemarks_table_exists():
    """
    На всякий случай создаём таблицу placemarks, если её нет.
    Схема скопирована из DB._create_placemarks_table().
    Данные НЕ трогаем.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS placemarks
        (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER REFERENCES users,
            datetime    TEXT,
            address     TEXT,
            latitude    TEXT,
            longitude   TEXT,
            description TEXT,
            status      TEXT
        )
        """
    )
    conn.commit()
    conn.close()


@app.route("/api/placemarks")
def api_placemarks():
    """
    Отдаём все точки с координатами:
    [{id, lat, lon, address, description, datetime, status}, ...]
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, datetime, address, latitude, longitude, description, status
        FROM placemarks
        WHERE latitude IS NOT NULL
          AND longitude IS NOT NULL
        """
    )
    rows = cur.fetchall()
    conn.close()

    data = []
    for r in rows:
        raw_lat = (r["latitude"] or "").strip()
        raw_lon = (r["longitude"] or "").strip()

        # В БД координаты хранятся как TEXT, аккуратно приводим к float
        try:
            lat = float(raw_lat.replace(",", "."))
            lon = float(raw_lon.replace(",", "."))
        except ValueError:
            continue  # пропускаем битые значения

        data.append(
            {
                "id": r["id"],
                "lat": lat,
                "lon": lon,
                "address": r["address"] or "",
                "description": r["description"] or "",
                "datetime": r["datetime"] or "",
                "status": r["status"] or "",
            }
        )

    return jsonify(data)


@app.route("/")
def index():
    """
    Простая HTML-страница с картой Яндекс и метками из /api/placemarks.
    """
    html = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <title>Чем пахнет Москва? — карта (Яндекс)</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    html, body {
      margin: 0;
      padding: 0;
      height: 100%;
    }
    #map {
      width: 100%;
      height: 100vh;
    }
    .balloon-title {
      font-weight: 600;
      font-size: 13px;
      margin-bottom: 4px;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .balloon-body {
      font-size: 12px;
      margin-bottom: 4px;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .balloon-address {
      font-size: 11px;
      color: #666;
      margin-bottom: 4px;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .balloon-meta {
      font-size: 10px;
      color: #999;
      margin-top: 2px;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <!-- JavaScript API Яндекс.Карт 2.1 -->
  <script src="https://api-maps.yandex.ru/2.1/?apikey=3ad71976-36a9-44da-a66a-788e67b7831f&lang=ru_RU"
          type="text/javascript"></script>

  <script>
    ymaps.ready(init);

    function init() {
      // Создаём карту. Порядок координат в Яндекс.Картах: [lat, lon].
      var map = new ymaps.Map('map', {
        center: [55.751244, 37.618423],
        zoom: 11,
        controls: ['zoomControl']
      });

      // Тянем точки из Flask-API
      fetch('/api/placemarks')
        .then(function(response) { return response.json(); })
        .then(function(points) {
          points.forEach(function(p) {
            var title = p.description && p.description.length > 40
              ? p.description.slice(0, 40) + '…'
              : (p.description || 'Запах');

            var balloonHtml = '';

            if (p.description) {
              balloonHtml += '<div class="balloon-title">' + title + '</div>';
              balloonHtml += '<div class="balloon-body">' + p.description + '</div>';
            } else {
              balloonHtml += '<div class="balloon-title">Запах</div>';
            }

            if (p.address) {
              balloonHtml += '<div class="balloon-address">' + p.address + '</div>';
            }

            if (p.datetime) {
              balloonHtml += '<div class="balloon-meta">' + p.datetime + '</div>';
            }

            var placemark = new ymaps.Placemark(
              [p.lat, p.lon], // здесь [lat, lon]
              {
                balloonContent: balloonHtml,
                hintContent: p.address || title
              },
              {
                preset: 'islands#blueIcon' // стандартная синяя метка
              }
            );

            map.geoObjects.add(placemark);
          });
        })
        .catch(function(err) {
          console.error('Ошибка загрузки точек', err);
        });
    }
  </script>
</body>
</html>
"""
    return Response(html, mimetype="text/html; charset=utf-8")


if __name__ == "__main__":
    ensure_placemarks_table_exists()
    print("Используем базу:", database_path)
    app.run(debug=True)

