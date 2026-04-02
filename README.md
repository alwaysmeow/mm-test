# ENCAR Cars Project

Тестовый проект состоит из двух частей:

- `server/` — парсинг ENCAR, перевод данных, ежедневный pipeline и FastAPI
- `client/` — React SPA с каталогом автомобилей в стиле `millionmiles.ae/cars`

## Структура

```text
mm-test/
├── client/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
└── server/
    ├── data/
    │   ├── encar_cars.json
    │   └── encar_cars_en.json
    ├── scraper.py
    ├── translate_to_english.py
    ├── daily_pipeline.py
    ├── cars_api.py
    └── requirements.txt
```

## Что делает backend

### `scraper.py`

Собирает автомобили из ENCAR API.

По умолчанию использует 4 источника:

```text
foreign_general
foreign_premium
korean_general
korean_premium
```

Логика:

- ходит в ENCAR API через `requests`
- проходит по страницам через параметр `sr`
- объединяет `general` и `premium`
- убирает дубликаты по `car_id`
- сохраняет результат в `server/data/encar_cars.json`

Собираемые поля:

- `car_id`
- `source_kind`
- `brand`
- `model`
- `year`
- `mileage_km`
- `price`
- `photo_url`
- `source_url`
- `fuel_type`
- `location`

Запуск:

```bash
python3 server/scraper.py
```

Примеры:

```bash
python3 server/scraper.py --page-size 50
python3 server/scraper.py --page-size 100 --max-pages 10
python3 server/scraper.py --url 'https://api.encar.com/search/car/list/premium?count=true&q=(And.(And.Hidden.N._.CarType.Y.)_.AdType.B.)&sr=%7CModifiedDate%7C0%7C20'
```

### `translate_to_english.py`

Читает исходный JSON и создаёт отдельный переведённый файл:

- читает `server/data/encar_cars.json`
- создаёт `server/data/encar_cars_en.json`

Что делает:

- переводит бренды, города, тип топлива и часть слов в моделях
- оставляет оригинальный JSON нетронутым
- пытается получить курс USD/KRW через `frankfurter.app`
- если не получается, использует fallback `1455.0`
- переводит `price` в USD

Запуск:

```bash
python3 server/translate_to_english.py
```

Пример:

```bash
python3 server/translate_to_english.py --usd-krw-rate 1455
```

### `daily_pipeline.py`

Программа для ежедневного обновления данных.

Что делает:

1. запускает `scraper.py`
2. затем запускает `translate_to_english.py`
3. ждёт до следующего окна запуска

Запуск:

```bash
python3 server/daily_pipeline.py --run-now --time 03:00
```

Примеры:

```bash
python3 server/daily_pipeline.py --time 03:00
python3 server/daily_pipeline.py --run-now --time 03:00
python3 server/daily_pipeline.py --run-now --scraper-arg=--max-pages --scraper-arg=10
```

## FastAPI

### `cars_api.py`

API отдаёт готовый переведённый JSON.

Endpoint:

```text
GET /cars
```

Запуск из корня проекта:

```bash
uvicorn server.cars_api:app --reload
```

API читает:

```text
server/data/encar_cars_en.json
```

## Frontend

Фронтенд находится в `client/`.

Стек:

- React
- Vite
- react-icons

Что уже сделано:

- светлая каталог-страница в стиле `millionmiles.ae/cars`
- чёрный header
- подключено SVG logo
- верхние фильтры
- карточки автомобилей
- сортировка
- загрузка данных с `GET /cars`

Установка и запуск:

```bash
cd client
npm install
npm run dev
```

Vite proxy настроен на backend:

```text
/cars -> http://127.0.0.1:8000
```

## Полный локальный запуск

### 1. Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r server/requirements.txt
uvicorn server.cars_api:app --reload
```

### 2. Data refresh

```bash
python3 server/scraper.py
python3 server/translate_to_english.py
```

### 3. Frontend

```bash
cd client
npm install
npm run dev
```

## Полезные замечания

- В `scraper.py` стоит защитный лимит `--max-pages 20`, чтобы не уйти в бесконечный цикл.
- Изображения для listing-карточек собираются через CDN `ci.encar.com`, иначе часть ссылок отдаёт `404`.
- `general` и `premium` объединяются, потому что это разные выдачи.
- Переведённый файл создаётся отдельно, без изменения исходного JSON.

## Формат данных

Пример ENCAR API-ответа, на который ориентирован парсер:

```json
{
  "Count": 8207,
  "SearchResults": []
}
```
