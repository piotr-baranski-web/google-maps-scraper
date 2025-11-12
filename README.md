# Google Maps Scraper

Program automatycznie zbiera dane kontaktowe firm z Google Maps i zapisuje je do pliku CSV, który od razu otwiera w Excelu.

## Co robi?

Wyszukuje miejsca na Google Maps i wyciąga:
- Nazwę firmy
- Adres
- Telefon
- Stronę internetową
- Email (automatycznie szuka na stronie WWW)

Wyniki zapisuje do pliku CSV i automatycznie go otwiera.

## Instalacja

### Wymagania
- Python 3.8+
- Google Chrome

### Krok 1: Pobierz projekt

```bash
git clone https://github.com/piotr-baranski-web/google-maps-scraper.git
cd google-maps-scraper
```

Lub pobierz ZIP z GitHuba i rozpakuj.

### Krok 2: Zainstaluj biblioteki

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

*Na Windowsie: `venv\Scripts\activate` zamiast `source venv/bin/activate`*

## Użycie

### Sposób 1: Interaktywny

```bash
python main.py
```

Program zapyta cię o:
- Co chcesz wyszukać?
- Ile wyników zebrać?

### Sposób 2: Z parametrami

```bash
python main.py Hotel Warszawa
```

Automatycznie wyszuka "Hotel Warszawa" i zbierze 10 wyników.

## Przykłady

```bash
# Hotele w Warszawie
python main.py Hotel Warszawa

# Restauracje
python main.py Restauracja Kraków

# Firmy zarządzające nieruchomościami
python main.py Firma zarządzająca nieruchomościami Warszawa

# Dentyści
python main.py Dentysta Gdańsk
```

## Co się stanie?

1. Otworzy się przeglądarka Chrome
2. Program wejdzie na Google Maps
3. Wyszuka miejsca
4. Zbierze dane z każdego wyniku
5. Zapisze do pliku CSV
6. **Automatycznie otworzy plik w Excelu/domyślnym programie**

Poczekaj 2-5 minut (zależnie od liczby wyników).

## Wyniki

Plik CSV zawiera kolumny:
- nazwa
- adres
- telefon
- strona_www
- email
- ocena
- liczba_opinii

Plik możesz otworzyć w:
- Microsoft Excel
- Google Sheets (File → Import)
- LibreOffice Calc

## Problemy?

**"Command not found: python3"**
- Na Windowsie użyj `python` zamiast `python3`

**Chrome się nie otwiera?**
- Sprawdź czy masz zainstalowanego Chrome
- Spróbuj: `pip install --upgrade webdriver-manager`

**Program nic nie znajduje?**
- Google Maps czasem zmienia strukturę strony
- Zgłoś Issue na GitHubie

## Uwagi prawne

Program do celów edukacyjnych i osobistych. Nie używaj do:
- Masowego scrapowania bez zgody
- Spamowania firm
- Łamania regulaminu Google Maps

## Licencja

MIT - możesz swobodnie używać i modyfikować.

## Autor

Piotr Barański - [@piotr-baranski-web](https://github.com/piotr-baranski-web)

Masz problemy? Otwórz Issue na GitHubie.
