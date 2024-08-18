import requests
from bs4 import BeautifulSoup
import json
import time

api_endpoints = {
    "aya_staffing": "https://api.ayastaffing.com/data",
    "cross_country_staffing": "https://api.crosscountrystaffing.com/data",
    "amn_staffing": "https://api.amnstaffing.com/data",
    "qualavis": "https://api.qualavis.com/data",
    "vizient": "https://api.vizient.com/data"
}

html_urls = {
    "aya_staffing_html": "https://www.ayastaffing.com/bill-rates",
    "cross_country_staffing_html": "https://www.crosscountrystaffing.com/bill-rates",
    "amn_staffing_html": "https://www.amnstaffing.com/bill-rates",
    "qualavis_html": "https://www.qualavis.com/bill-rates",
    "vizient_html": "https://www.vizient.com/bill-rates"
}

def fetch_data(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {api_url}: {e}")
        return None

def parse_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except requests.exceptions.RequestException as e:
        print(f"Error fetching HTML from {url}: {e}")
        return None

def extract_data_from_soup(soup):
    data = []
    for item in soup.find_all('div', class_='data-class'):
        try:
            bill_rate = item.find('span', class_='bill-rate').text.strip()
            skillset = item.find('span', class_='skillset').text.strip()
            data.append({
                'bill_rate': bill_rate,
                'skillset': skillset
            })
        except AttributeError:
            continue  
    return data

def handle_pagination(url):
    results = []
    page = 1
    while True:
        paginated_url = f"{url}?page={page}"
        soup = parse_html(paginated_url)
        if not soup or not soup.find_all('div', class_='data-class'):
            break  
        data = extract_data_from_soup(soup)
        results.extend(data)
        page += 1
        time.sleep(1)  
    return results

def save_to_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Data saved to {filename}")

def main():
    results = {}
    for name, api_url in api_endpoints.items():
        data = fetch_data(api_url)
        if data:
            results[name] = data
    for name, url in html_urls.items():
        if 'html' in name:
            data = handle_pagination(url)  
            if data:
                results[name] = data
    save_to_file(results, 'staffing_agencies_data.json')

if __name__ == "__main__":
    main()
