#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps Scraper - zbiera dane firm z wyników wyszukiwania Google Maps
"""

import time
import re
import csv
import os
import subprocess
import platform
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests


class GoogleMapsScraper:
    def __init__(self, headless=False):
        """Inicjalizacja scrapera"""
        self.headless = headless
        self.driver = None
        self.results = []
        
    def setup_driver(self):
        """Konfiguracja i uruchomienie przeglądarki Chrome"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
    def search_places(self, query):
        """Wyszukaj miejsca w Google Maps"""
        print(f"\n🔍 Wyszukuję: {query}")
        
        self.driver.get('https://www.google.com/maps')
        time.sleep(2)
        
        try:
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'searchboxinput'))
            )
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            time.sleep(5)
            return True
        except TimeoutException:
            print("❌ Nie znaleziono pola wyszukiwania")
            return False
            
    def scroll_results(self, max_scrolls=5):
        """Przewija listę wyników aby załadować więcej miejsc"""
        print("📜 Przewijam wyniki...")
        
        try:
            results_panel = self.driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
            
            for i in range(max_scrolls):
                self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', results_panel)
                time.sleep(2)
                print(f"  Przewinięto {i+1}/{max_scrolls}")
                
        except Exception as e:
            print(f"⚠️ Problem z przewijaniem: {e}")
            
    def scrape_results(self, max_results=20):
        """Zbiera dane z wyników wyszukiwania"""
        print(f"\n📊 Zbieram dane (max {max_results} miejsc)...")
        
        try:
            place_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href^="https://www.google.com/maps/place"]')
            print(f"✅ Znaleziono {len(place_links)} wyników\n")
            
            for idx, link in enumerate(place_links[:max_results]):
                print(f"[{idx+1}/{min(len(place_links), max_results)}]\n")
                
                try:
                    link.click()
                    time.sleep(3)
                    
                    place_data = self._extract_place_data()
                    if place_data:
                        self.results.append(place_data)
                        
                except Exception as e:
                    print(f"⚠️ Błąd przy przetwarzaniu miejsca: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Błąd zbierania danych: {e}")
            
    def _extract_place_data(self):
        """Wyciąga dane o pojedynczym miejscu"""
        data = {
            'nazwa': 'Brak',
            'adres': 'Brak',
            'telefon': 'Brak',
            'strona_www': 'Brak',
            'email': 'Brak',
            'ocena': 'Brak',
            'liczba_opinii': 'Brak'
        }
        
        try:
            # Nazwa
            try:
                name_elem = self.driver.find_element(By.CSS_SELECTOR, 'h1')
                data['nazwa'] = name_elem.text
                print(f"📍 {data['nazwa']}")
            except:
                pass
                
            # Adres
            try:
                address_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-item-id="address"]')
                data['adres'] = address_button.get_attribute('aria-label').replace('Adres: ', '')
                print(f"  📮 Adres: {data['adres']}")
            except:
                pass
                
            # Telefon
            try:
                phone_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-item-id*="phone"]')
                phone_text = phone_button.get_attribute('aria-label')
                if phone_text:
                    data['telefon'] = phone_text.replace('Telefon: ', '').replace('Zadzwoń ', '')
                    print(f"  📞 Telefon: {data['telefon']}")
            except:
                pass
                
            # Strona WWW
            try:
                website_link = self.driver.find_element(By.CSS_SELECTOR, 'a[data-item-id="authority"]')
                data['strona_www'] = website_link.get_attribute('href')
                print(f"  🌐 Strona: {data['strona_www']}")
                
                # Szukaj emaila na stronie
                if data['strona_www'] != 'Brak':
                    print(f"    🌐 Sprawdzam stronę: {data['strona_www']}")
                    email = self._find_email_on_website(data['strona_www'])
                    if email:
                        data['email'] = email
                        print(f"    ✅ Znaleziono email: {email}")
                    else:
                        print(f"    ⚠️ Nie znaleziono emaila na stronie")
            except:
                pass
                
        except Exception as e:
            print(f"  ⚠️ Błąd wyciągania danych: {e}")
            return None
            
        return data if data['nazwa'] != 'Brak' else None
        
    def _find_email_on_website(self, url):
        """Szuka emaila na podanej stronie"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Wzorzec emaila
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, soup.get_text())
                
                # Filtruj niepożądane emaile
                valid_emails = [
                    email for email in emails
                    if not any(x in email.lower() for x in ['example.com', 'domain.com', 'test.com', 'wix.com'])
                ]
                
                if valid_emails:
                    return valid_emails[0]
                    
                # Szukaj w linkach mailto
                mailto_links = soup.find_all('a', href=re.compile(r'^mailto:'))
                if mailto_links:
                    return mailto_links[0]['href'].replace('mailto:', '').split('?')[0]
                    
        except:
            pass
            
        return None
        
    def save_to_csv(self, filename=None, open_file=True):
        """Zapisuje wyniki do pliku CSV i opcjonalnie go otwiera"""
        if not self.results:
            print("⚠️ Brak wyników do zapisania")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'google_maps_results_{timestamp}.csv'
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['nazwa', 'adres', 'telefon', 'strona_www', 'email', 
                         'ocena', 'liczba_opinii']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(self.results)
        
        filepath = os.path.abspath(filename)
        print(f"\n✅ Zapisano {len(self.results)} wyników do pliku: {filepath}")
        
        # Automatyczne otwieranie pliku
        if open_file:
            print("📂 Otwieram plik...")
            try:
                if platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', filepath])
                elif platform.system() == 'Windows':
                    os.startfile(filepath)
                else:  # Linux
                    subprocess.run(['xdg-open', filepath])
                    
                print("✅ Plik otwarty w Excelu/domyślnej aplikacji!")
            except Exception as e:
                print(f"⚠️ Nie udało się otworzyć pliku automatycznie")
                print(f"📁 Otwórz ręcznie: {filepath}")
        
        return filepath
        
    def close(self):
        """Zamyka przeglądarkę"""
        if self.driver:
            self.driver.quit()
            print("\n🔒 Zamknięto przeglądarkę")


# Wyłącz ostrzeżenia SSL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
