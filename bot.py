import os
import time
import requests
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = "8555585983:AAHdJ5Nb3KhK7PLTds5cxnGB81wgLgAQnAQ"
CHAT_ID = "8919992155"
OLX_URL = "https://www.olx.pl/oferty/q-iphone/"
CHECK_INTERVAL = 120  # co 2 minuty

seen_ads = set()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Błąd Telegram: {e}")

def main():
    global seen_ads
    print("Bot chmurowy wystartował!")
    send_telegram_message("☁️ Bot chmurowy ruszył i monitoruje OLX 24/7!")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    while True:
        try:
            response = requests.get(OLX_URL, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                cards = soup.find_all("div", {"data-cy": "l-card"})

                if cards:
                    new_count = 0
                    for card in cards:
                        link_elem = card.find("a")
                        if not link_elem or "href" not in link_elem.attrs:
                            continue

                        link = link_elem["href"]
                        if not link.startswith("http"):
                            link = "https://www.olx.pl" + link

                        ad_id = link.split("/")[-1].split(".html")[0]

                        if ad_id in seen_ads:
                            continue

                        is_first_run = (len(seen_ads) == 0)
                        seen_ads.add(ad_id)

                        if not is_first_run:
                            title_elem = card.find("h6") or card.find("h4")
                            title = title_elem.text.strip() if title_elem else "Nowe ogłoszenie"

                            price_elem = card.find("p", {"data-testid": "ad-price"})
                            price = price_elem.text.strip() if price_elem else "Brak ceny"

                            msg = f"🚨 <b>NOWE OGŁOSZENIE NA OLX!</b> 🚨\n\n<b>{title}</b>\n💰 Cena: {price}\n\n🔗 <a href='{link}'>Zobacz ogłoszenie</a>"
                            send_telegram_message(msg)
                            new_count += 1
                    
                    print(f"Sprawdzono. Nowych: {new_count}")
            else:
                print(f"Błąd pobierania strony OLX: {response.status_code}")
        
        except Exception as e:
            print(f"Błąd pętli: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
