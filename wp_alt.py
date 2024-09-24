import requests
import json
from openai import OpenAI
import os
from requests.auth import HTTPBasicAuth

# OpenAI API-Schlüssel
OPENAI_API_KEY = "dein_apikey"

# WordPress-Zugangsdaten
WP_URL = "https://deine-url.de/"
WP_USER = "dein_username"
WP_APP_PASSWORD = "dein_apppassword"

def get_image_urls(site_url, per_page=100):
    image_urls = []
    page = 1
    
    while True:
        api_url = f"{site_url}/wp-json/wp/v2/media?per_page={per_page}&page={page}"
        response = requests.get(api_url)
        
        if response.status_code != 200:
            print(f"Fehler beim Abrufen der Daten: HTTP {response.status_code}")
            break
        
        data = json.loads(response.text)
        
        if not data:
            break
        
        for item in data:
            if 'source_url' in item:
                image_urls.append({'id': item['id'], 'url': item['source_url']})
        
        page += 1
    
    return image_urls

def generate_alt_tag(image_url):
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Generiere einen prägnanten und beschreibenden ALT-Tag für dieses Bild auf Deutsch. Konzentriere dich auf die Hauptelemente und den Zweck des Bildes. Der ALT-Tag sollte nicht länger als 125 Zeichen sein."},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url},
                    },
                ],
            }
        ],
        max_tokens=50,
    )
    return response.choices[0].message.content.strip()

def update_wordpress_alt_tag(image_id, alt_tag):
    update_url = f"{WP_URL}/wp-json/wp/v2/media/{image_id}"
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "alt_text": alt_tag
    }
    response = requests.post(
        update_url,
        headers=headers,
        json=data,
        auth=HTTPBasicAuth(WP_USER, WP_APP_PASSWORD)
    )
    if response.status_code == 200:
        print(f"ALT-Tag für Bild {image_id} erfolgreich aktualisiert.")
    else:
        print(f"Fehler beim Aktualisieren des ALT-Tags für Bild {image_id}: HTTP {response.status_code}")

def main():
    images = get_image_urls(WP_URL)
    for image in images:
        alt_tag = generate_alt_tag(image['url'])
        update_wordpress_alt_tag(image['id'], alt_tag)

if __name__ == "__main__":
    main()