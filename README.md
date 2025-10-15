# Lexus — Steam Inventory Collector

> RU / EN bilingual README. Scroll for English below.

## Описание (RU)
Скрипт собирает инвентарь аккаунтов Steam через публичный API tradeit.gg, суммирует стоимость предметов, фильтрует контейнеры и исключённые позиции, и сохраняет результат в CSV-файл `steam_accounts_inventory.csv`. Поддерживаются HTTP(S) прокси (включая авторизацию), многопоточность и прогресс-бар.

Основные возможности:
- Многопоточность (по умолчанию до 4 потоков) для ускорения обработки.
- Поддержка прокси: формат `ip:port` или `ip:port:username:password`.
- Исключение предметов по имени (файл `exclude.txt`, регистронезависимо).
- Автоматический расчёт общей стоимости инвентаря в долларах США.
- Экспорт в CSV с полями: SteamID, TotalValue, ItemImage.
- Удобный прогресс-бар через `tqdm`.

## Требования
- Python 3.9+
- Зависимости Python: `requests`, `tqdm`

Установка зависимостей (любая из опций):
```bash
# Опция A: Установка напрямую
pip install requests tqdm

# Опция B: Через виртуальное окружение (рекомендуется)
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
pip install --upgrade pip
pip install requests tqdm
# macOS/Linux:
# source .venv/bin/activate
# pip install --upgrade pip
# pip install requests tqdm
```

## Подготовка данных
В корне проекта используются три файла:
- `id.txt` — список URL профилей Steam (по одному на строку). Поддерживается только формат `https://steamcommunity.com/profiles/<steam64id>`.
- `proxy.txt` — список прокси, по одному на строку. Форматы:
  - `ip:port`
  - `ip:port:username:password`
  - допускается префикс `http://` (скрипт уберёт его автоматически)
- `exclude.txt` — (необязателен) список названий предметов для исключения (по одному на строку, без учёта регистра). Пример: `Charm Detachment Pack`

Примеры содержимого файлов:
```txt
# id.txt
https://steamcommunity.com/profiles/76561198000000000
https://steamcommunity.com/profiles/76561198000000001
```
```txt
# proxy.txt
203.0.113.5:8080
203.0.113.6:8000:username:password
```
```txt
# exclude.txt
Charm Detachment Pack
Case Name Example
```

Важно:
- Vanity-URL вида `https://steamcommunity.com/id/<nickname>` не поддерживается и будет отмечена как "Invalid Steam URL format".
- Если `proxy.txt` пустой, скрипт завершится сообщением: `No available proxies in proxy.txt`.

## Запуск
```bash
python main.py
```
При выполнении вы увидите прогресс-бар. Скрипт:
- Загружает URL-адреса профилей из `id.txt`.
- Перебирает прокси из `proxy.txt` и делает до 5 попыток получить инвентарь.
- Исключает предметы категории `Container` и те, что указаны в `exclude.txt`.
- Суммирует `totalCashPriceToday` (значения из API) для всех отфильтрованных предметов и переводит в доллары США.
- Печатает общую сумму по всем аккаунтам и сохраняет результат в `steam_accounts_inventory.csv`.

Выходные данные:
- `steam_accounts_inventory.csv` с разделителем `;`, полями:
  - `SteamID` — Steam64 ID
  - `TotalValue` — суммарная стоимость инвентаря в долларах США (строкой, например `12.34$`)
  - `ItemImage` — URL изображения первого предмета (или `N/A`/пусто при отсутствии)

## Настройки и тонкая настройка
- Количество потоков: измените переменную `max_threads` в `main.py` (по умолчанию `4`).
- Таймаут запроса: 30 секунд на попытку.
- Повторы: до 5 попыток, между циклами — ожидание 7 секунд.

## Частые проблемы
- `Invalid Steam URL format`: используйте URL только вида `.../profiles/<steam64id>`. Vanity-URL (`.../id/<name>`) не поддерживается.
- `No available proxies in proxy.txt`: добавьте рабочие прокси (см. формат выше).
- Нулевая стоимость (`0.00$`): у аккаунта может не быть подходящих предметов, все предметы попали в исключения, либо API вернул неполные данные.
- Ограничения API/tradeit.gg: при высокой нагрузке возможны задержки (`isWaiting`), добавьте больше прокси или повторите позже.

## Предупреждение
Скрипт использует сторонний API (tradeit.gg).

---

## Description (EN)
This script collects Steam account inventories using the public tradeit.gg API, sums item values, filters out containers and excluded items, and saves the results into `steam_accounts_inventory.csv`. It supports HTTP(S) proxies (including authentication), multithreading, and a progress bar.

Features:
- Multithreaded processing (up to 4 threads by default).
- Proxy support: `ip:port` or `ip:port:username:password`.
- Exclude items by name via `exclude.txt` (case-insensitive).
- Automatic total inventory value calculation in USD.
- CSV export with fields: SteamID, TotalValue, ItemImage.
- Friendly progress bar via `tqdm`.

## Requirements
- Python 3.9+
- Python packages: `requests`, `tqdm`

Install dependencies (choose one):
```bash
# Option A: Install directly
pip install requests tqdm

# Option B: Use a virtual environment (recommended)
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
pip install --upgrade pip
pip install requests tqdm
# macOS/Linux:
# source .venv/bin/activate
# pip install --upgrade pip
# pip install requests tqdm
```

## Preparing inputs
The project uses three root-level files:
- `id.txt` — list of Steam profile URLs (one per line). Only `https://steamcommunity.com/profiles/<steam64id>` is supported.
- `proxy.txt` — list of proxies, one per line. Supported formats:
  - `ip:port`
  - `ip:port:username:password`
  - `http://` prefix is allowed (it will be stripped automatically)
- `exclude.txt` — (optional) item names to exclude (one per line, case-insensitive). Example: `Charm Detachment Pack`

Examples:
```txt
# id.txt
https://steamcommunity.com/profiles/76561198000000000
https://steamcommunity.com/profiles/76561198000000001
```
```txt
# proxy.txt
203.0.113.5:8080
203.0.113.6:8000:username:password
```
```txt
# exclude.txt
Charm Detachment Pack
Case Name Example
```

Notes:
- Vanity URLs like `https://steamcommunity.com/id/<nickname>` are not supported and will be marked as "Invalid Steam URL format".
- If `proxy.txt` is empty, the script will exit with: `No available proxies in proxy.txt`.

## Run
```bash
python main.py
```
During execution you will see a progress bar. The script:
- Loads profile URLs from `id.txt`.
- Iterates over proxies from `proxy.txt` and tries up to 5 attempts per profile.
- Filters out `Container` category items and those listed in `exclude.txt`.
- Sums `totalCashPriceToday` values (from the API) of filtered items and converts to USD.
- Prints the total balance across all accounts and saves results to `steam_accounts_inventory.csv`.

Output:
- `steam_accounts_inventory.csv` with `;` delimiter, fields:
  - `SteamID` — Steam64 ID
  - `TotalValue` — total inventory value in USD (string, e.g. `12.34$`)
  - `ItemImage` — URL of the first item's image (or `N/A`/empty if not available)

## Tuning
- Thread count: change `max_threads` in `main.py` (default `4`).
- Request timeout: 30s per attempt.
- Retries: up to 5, with a 7-second wait between rounds when failing.

## Troubleshooting
- `Invalid Steam URL format`: use only `.../profiles/<steam64id>`; vanity URLs (`.../id/<name>`) are not supported.
- `No available proxies in proxy.txt`: add working proxies (see formats above).
- `0.00$` totals: the account may have no matching items, items may be excluded, or the API returned incomplete data.
- API/tradeit.gg constraints: under heavy load you may see `isWaiting`; add more proxies or try later.

## Disclaimer

This script uses a third-party API (tradeit.gg). 
