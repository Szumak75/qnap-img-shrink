# Zadania

## ✅ Wykonane - Kompletna implementacja Converter

### Założenia dla klasy Converter:

1. ✓ Konstruktor przyjmuje poprawne parametry - `max_size` i `quality`
2. ✓ Metoda `.convert()`:
   - ✓ Przyjmuje obiekt `ImageFileInfo`
   - ✓ Sprawdza możliwość odczytu/zapisu pliku
   - ✓ Przy pomocy modułu Pillow odczytuje plik
   - ✓ Sprawdza rozmiar najdłuższego boku:
     - ✓ Jeśli przekracza `Config.max_size` - uruchamia konwersję
     - ✓ Zmniejsza proporcjonalnie (dłuższy bok = `Config.max_size`)
     - ✓ Jeśli mniejszy - pozostawia bez zmian i przerywa
   - ✓ Zapis nadpisujący plik źródłowy:
     - ✓ JPG: kompresja z `Config.quality`
     - ✓ PNG: maksymalna kompresja + przeplot
     - ✓ Pozostałe formaty: bez kompresji
     - ✓ Przywrócenie oryginalnych uprawnień z `ImageFileInfo`
   - ✓ Raport końcowy:
     - ✓ Liczba przetworzonych plików
     - ✓ Porównanie sumy wielkości przed i po konwersji
     - ✓ Procent kompresji

### Zrealizowane funkcjonalności:

**Klasa ConversionStats:**
- Śledzenie statystyk konwersji
- Liczba przetworzonych/pominiętych plików
- Rozmiary przed/po konwersji
- Obliczanie oszczędności i stopnia kompresji

**Converter.convert():**
- Sprawdzanie uprawnień do odczytu/zapisu
- Analiza rozmiaru obrazu
- Proporcjonalne zmniejszanie rozmiaru
- Kompresja specyficzna dla formatu:
  - JPEG: quality + optimize
  - PNG: compress_level=9 + interlace
  - Inne: bez dodatkowej kompresji
- Przywracanie uprawnień (chmod)
- Próba przywrócenia właściciela/grupy (chown)
- Statystyki w czasie rzeczywistym

**Testy jednostkowe (62 testy, 100% pass):**
- `test_app.py` - 6 testów
- `test_config.py` - 15 testów
- `test_converter.py` - 20 testów (nowa wersja)
- `test_file_find.py` - 21 testów

## Podsumowanie wcześniejszych zadań

### FileFind.find_images():
- ✓ Rekurencyjne skanowanie katalogu roboczego
- ✓ Obsługa rozszerzeń: .jpg, .jpeg, .bmp, .tiff, .tif, .png
- ✓ Case-insensitive wyszukiwanie
- ✓ Zwracanie obiektów `ImageFileInfo` z metadanymi
- ✓ Obsługa błędów (brak katalogu, uprawnienia)

### Dodatkowe ulepszenia:
- Plik konfiguracyjny YAML (`etc/config.yaml`)
- Metoda `Config.load_from_file()` z walidacją
- Klasa `ImageFileInfo` z pełnymi metadanymi
- Wszystkie testy przechodzą pomyślnie (62/62)
- Kod sformatowany przez `black`
- Pełna integracja wszystkich komponentów w `App.run()`
