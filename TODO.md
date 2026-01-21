# Zadania

## Wykonane ✓

1. ✓ Klasa file.FileFind ma wykonać skanowanie folderu wskazanego w konfiguracji Config.wrk_dir wyszukując w nim oraz w jego subfolderach pliki graficzne: jpg, bmp, tiff, png.
2. ✓ Jako wynik działania ma zostać zwrócona List[str] ze ścieżkami do znalezionych plików.
3. ✓ Wygenerowano testy jednostkowe do całości projektu.

## Podsumowanie

### Zrealizowane funkcjonalności:

**FileFind.find_images():**
- Rekurencyjne skanowanie katalogu roboczego
- Obsługa rozszerzeń: .jpg, .jpeg, .bmp, .tiff, .tif, .png
- Case-insensitive wyszukiwanie
- Zwracanie posortowanych ścieżek bezwzględnych
- Obsługa błędów (brak katalogu, uprawnienia)

**Testy jednostkowe (51 testów, 100% pass):**
- `test_app.py` - 6 testów dla klasy App
- `test_config.py` - 14 testów dla klasy Config
- `test_converter.py` - 14 testów dla klasy Converter
- `test_file_find.py` - 17 testów dla klasy FileFind

**Dodatkowe ulepszenia:**
- Plik konfiguracyjny YAML (`etc/config.yaml`)
- Metoda `Config.load_from_file()` z walidacją
- Wszystkie testy przechodzą pomyślnie
- Kod sformatowany przez `black`
