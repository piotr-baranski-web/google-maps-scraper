#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps Scraper - Główny skrypt uruchomieniowy
"""

import importlib.util
import sys
import os

# Import z pliku z myślnikami
script_dir = os.path.dirname(os.path.abspath(__file__))
scraper_path = os.path.join(script_dir, "google-maps-scraper.py")
spec = importlib.util.spec_from_file_location("google_maps_scraper", scraper_path)
module = importlib.util.module_from_spec(spec)
sys.modules["google_maps_scraper"] = module
spec.loader.exec_module(module)
GoogleMapsScraper = module.GoogleMapsScraper


def main():
    print("=" * 70)
    print("🗺️  GOOGLE MAPS SCRAPER")
    print("=" * 70)
    
    # Pobierz parametry
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        query = input("\n🔍 Co chcesz wyszukać? (np. 'Hotel Warszawa'): ")
    
    if not query:
        print("❌ Nie podano zapytania!")
        return
    
    # Liczba wyników
    try:
        max_results = int(input("📊 Ile wyników zebrać? (domyślnie 10): ") or "10")
    except:
        max_results = 10
    
    print("\n⏳ Uruchamiam scraper...")
    print(f"📌 Zapytanie: {query}")
    print(f"🔢 Max wyników: {max_results}")
    print()
    
    # Utwórz scraper
    scraper = GoogleMapsScraper(headless=False)
    
    try:
        # Uruchom
        scraper.setup_driver()
        
        if scraper.search_places(query):
            scraper.scroll_results(max_scrolls=3)
            scraper.scrape_results(max_results=max_results)
            
            # Zapisz i otwórz plik
            if scraper.results:
                filename = f"wyniki_{query.replace(' ', '_')[:30]}.csv"
                scraper.save_to_csv(filename, open_file=True)
            else:
                print("\n⚠️  Nie znaleziono żadnych wyników")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Przerwano przez użytkownika")
        if scraper.results:
            scraper.save_to_csv(open_file=True)
    
    except Exception as e:
        print(f"\n❌ Wystąpił błąd: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.close()
    
    print("\n" + "=" * 70)
    print("✨ Gotowe!")
    print("=" * 70)


if __name__ == "__main__":
    main()
