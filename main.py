import requests
import time
import csv
import threading
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import sys

class Logger:
    def __init__(self, progress_bar):
        self.progress_bar = progress_bar
        
    def print(self, message):
        self.progress_bar.clear()
        print(message)
        self.progress_bar.refresh()

def load_proxies():
    with open('proxy.txt', 'r') as f:
        proxies = [line.strip() for line in f if line.strip()]
    return proxies

def load_excluded_items():
    try:
        with open('exclude.txt', 'r') as f:
            return [line.strip().lower() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def get_session_with_proxy(proxy):
    session = requests.Session()
    
    if proxy.startswith('http://'):
        proxy = proxy[7:]
    
    proxy_parts = proxy.split(':')
    if len(proxy_parts) == 4:
        ip, port, username, password = proxy_parts
        proxy_url = f"http://{username}:{password}@{ip}:{port}"
        session.proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
    elif len(proxy_parts) == 2:
        ip, port = proxy_parts
        proxy_url = f"http://{ip}:{port}"
        session.proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
    return session

def get_inventory_data(steam_id, proxies, logger):
    attempt = 0
    while attempt < 5:
        for proxy in proxies:
            try:
                url = f"https://tradeit.gg/api/v2/inventory/search?steamId={steam_id}"
                session = get_session_with_proxy(proxy)
                response = session.get(url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("data", {}).get("isWaiting"):
                        continue
                    return data
                else:
                    logger.print(f"Error getting inventory data with proxy: {proxy} - Status: {response.status_code}")
            except requests.exceptions.ProxyError as e:
                logger.print(f"Proxy error: {str(e)} for proxy: {proxy}")
                continue
            except Exception as e:
                logger.print(f"Error during request with proxy {proxy}: {str(e)}")
                continue
        
        attempt += 1
        logger.print(f"Failed to get data, attempt {attempt}. Waiting 7 seconds...")
        for _ in range(7):
            time.sleep(1)
            logger.progress_bar.refresh()
    
    return None

def parse_inventory_data(inventory_data, excluded_items):
    if not inventory_data:
        return None
    
    inventory_items = inventory_data.get("data", {}).get("inventory", [])
    
    filtered_items = [
        item for item in inventory_items 
        if item.get('category', '') != 'Container' and 
        item.get('name', '').lower() not in excluded_items
    ]
    
    return {
        "items": filtered_items
    }

def extract_steam_id(steam_profile_url):
    if "steamcommunity.com/profiles/" in steam_profile_url:
        return steam_profile_url.split('/')[-1].strip()
    return None

def process_profile_with_retry(steam_profile_url, proxies, all_data, lock, excluded_items, logger):
    steam_profile_url = steam_profile_url.strip()
    if not steam_profile_url:
        return
    
    steam_id = extract_steam_id(steam_profile_url)
    if not steam_id:
        logger.print(f"Invalid Steam URL format: {steam_profile_url}")
        with lock:
            all_data.append({
                "SteamID": "N/A",
                "TotalValue": "0.00$",
                "ItemImage": "N/A"
            })
        logger.progress_bar.update(1)
        return
    
    inventory_data = get_inventory_data(steam_id, proxies, logger)
    
    if not inventory_data:
        with lock:
            all_data.append({
                "SteamID": steam_id,
                "TotalValue": "0.00$",
                "ItemImage": "N/A"
            })
        logger.progress_bar.update(1)
        return
    
    parsed_data = parse_inventory_data(inventory_data, excluded_items)
    if parsed_data:
        try:
            total_value = sum(float(item.get('totalCashPriceToday', 0)) for item in parsed_data['items']) / 100
            if total_value == 0:
                total_value = 0.00
            item_image = parsed_data["items"][0].get('imgURL', 'N/A') if parsed_data["items"] else 'N/A'
            
            if item_image == 'N/A':
                total_value = 0.00
            
            with lock:
                all_data.append({
                    "SteamID": steam_id,
                    "TotalValue": f"{total_value:.2f}$",
                    "ItemImage": item_image
                })
        except Exception as e:
            logger.print(f"Error processing data for SteamID {steam_id}: {str(e)}")
            with lock:
                all_data.append({
                    "SteamID": steam_id,
                    "TotalValue": "0.00$",
                    "ItemImage": "N/A"
                })
    else:
        logger.print(f"No data available for SteamID {steam_id}.")
        with lock:
            all_data.append({
                "SteamID": steam_id,
                "TotalValue": "0.00$",
                "ItemImage": "N/A"
            })
    
    logger.progress_bar.update(1)

def main():
    with open('id.txt', 'r') as file:
        urls = file.readlines()
        url_count = len(urls)
        print(f"Found {url_count} links in id.txt")
    
    proxies = load_proxies()
    if not proxies:
        print("No available proxies in proxy.txt")
        return
    
    excluded_items = load_excluded_items()
    if excluded_items:
        print(f"Loaded {len(excluded_items)} items to exclude")
    
    all_data = []
    lock = threading.Lock()
    total_balance = 0.0
    
    max_threads = 4
    
    sys.stdout.write("\n")
    with tqdm(total=url_count, desc="Processing URLs", unit="URL", position=0, leave=True, dynamic_ncols=True) as main_progress:
        logger = Logger(main_progress)
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            for steam_profile_url in urls:
                futures.append(executor.submit(
                    process_profile_with_retry, 
                    steam_profile_url, 
                    proxies, 
                    all_data, 
                    lock,
                    excluded_items,
                    logger
                ))
            
            for future in futures:
                future.result()
    
    for row in all_data:
        try:
            if row["TotalValue"] != "N/A" and row["TotalValue"] != "0.00$":
                total_balance += float(row["TotalValue"].replace('$', ''))
        except:
            continue
    
    print(f"\nTotal balance across all accounts: {total_balance:.2f}$")
    
    if all_data:
        headers = ["SteamID", "TotalValue", "ItemImage"]
        
        with open('steam_accounts_inventory.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            
            for row in all_data:
                if row["TotalValue"] == "N/A":
                    row["TotalValue"] = "0.00$"
                if row["TotalValue"] == "0.00$":
                    row["ItemImage"] = None
            
            filtered_data = [row for row in all_data if row["TotalValue"] != "0.00$" or row["ItemImage"] is None]
            writer.writerows(filtered_data)
        
        print(f"Data successfully written to steam_accounts_inventory.csv")

if __name__ == "__main__":
    main()
