# Konfiguracja AI Agents - qnap-img-shrink

## Informacje o projekcie

- **Nazwa projektu**: `qnap-img-shrink`
- **Główny język**: `Python`
- **Wersja języka**: `3.11+`
- **System zarządzania**: `Poetry`
- **Repozytorium**: `git`
- **Author**: "Jacek 'Szumak' Kotlarski"
- **Author Email**: 'szumak@virthost.pl'
- **Github User**: 'Szumak75'

---

## Konfiguracja plików

**files.include** - Pliki źródłowe i testy:

- `**/*.py`
- `tests/**/*.py`
- `test_*.py`
- `README.md`
- `docs/**/*.md`
- `*.md`
- `pyproject.toml`

**files.exclude** - Wykluczenia:

- `.venv/**`
- `venv/**`
- `env/**`
- `.pytest_cache/**`
- `__pycache__/**`
- `*.pyc`
- `*.pyo`
- `dist/**`
- `build/**`
- `*.egg-info/**`
- `.git/**`
- `.gitignore`
- `.vscode/**`
- `.idea/**`
- `*.swp`
- `*~`
- `*.log`
- `*.tmp`
- `tmp/**`
- `temp/**`
- `node_modules/**`

---

## Instrukcje dotyczące zachowania

### Język i zarządzanie projektem

**Dla projektów Python z Poetry:**

- **Język**: Python 3.11+
- **Zarządzanie projektem**: Projekt używa Poetry
- **Uruchamianie narzędzi**: `poetry run <polecenie>` (np. `poetry run pytest`)
- **Instalacja zależności**: `poetry install`
- **Aktualizacja**: `poetry update`

### Styl kodowania

#### Python

**Formatowanie i walidacja:**

- **Formatter**: `black` - automatyczne formatowanie kodu
  - Uruchamianie: `poetry run black .`
  - Konfiguracja: Sprawdź `[tool.black]` w `pyproject.toml`
- **Linter**: `pycodestyle` lub `flake8` - zgodność z PEP 8
  - Uruchamianie: `poetry run pycodestyle .`
- **Type checking**: `mypy` - sprawdzanie typów (opcjonalnie)
  - Uruchamianie: `poetry run mypy .`

**Konwencje kodowania:**

- Przestrzegaj PEP 8 (Style Guide for Python Code)
- Dodawaj adnotacje typów do nowych funkcji i metod
- Używaj type hints zgodnie z PEP 484
- Preferuj pojedyncze cudzysłowy `'string'`, chyba że podwójne są wymagane
- Maksymalna długość linii: 88 znaków (black default)
- Używaj f-strings do formatowania stringów (Python 3.11+)

**Docstringi:**

- Format: Google style
- Struktura: Krótka linia streszczenia, następnie sekcje
- Sekcje: `### Arguments`, `### Returns`, `### Raises`, `### Examples`
- Język: Angielski (kod i dokumentacja techniczna)

**Module-level Docstring:**

```python
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: [YYYY-MM-DD]

Purpose: [Short, one-line summary of the module's purpose.]

[Optional: More detailed description of the module's functionality,
its components, and how they fit into the larger project.]
"""
```

**Class-level Docstring:**

```python
"""[Short, one-line summary of the class's purpose.]

[Optional: More detailed description of the class's responsibilities,
design choices, and its role (e.g., utility, data structure).]
"""
```

**Function/Method-level Docstring:**

```python
"""[Short, one-line summary of what the function does.]

[Optional: More detailed explanation of the function's logic,
its use cases, or any important algorithms used.]

### Arguments:
* arg1: [type] - [Description of the first argument.]
* arg2: Optional[[type]] - [Description of the second, optional argument. Defaults to [DefaultValue].]

### Returns:
[type] - [Description of the returned value.]

### Raises:
* [ExceptionType]: [Description of the condition that causes this exception to be raised.]

### Examples:
```python
>>> function_name(arg1, arg2)
expected_result
```
"""
```

### Testowanie

#### Python

**Framework i organizacja:**

- **Framework**: `pytest`
- **Lokalizacja testów**: `tests/` w głównym katalogu
- **Nazewnictwo**: `test_*.py`
- **Uruchamianie**: `poetry run pytest`
- **Pokrycie kodu**: `pytest --cov=.` (wymaga `pytest-cov`)

**Konwencje testowe:**

- Testy są funkcjami (pytest)
- Jeden test = jedna funkcjonalność
- Używaj fixtures dla konfiguracji testowej
- Testy jednostkowe (unit) oraz integracyjne (integration) w osobnych katalogach
- Zapewnij pokrycie testami każdej nowej funkcjonalności (cel: >80%)

### Obsługa błędów

#### Python

**Strategia obsługi błędów:**

- Używaj specyficznych wyjątków zamiast ogólnego `Exception`
- Twórz własne klasy wyjątków gdy potrzebne: `class CustomError(Exception)`
- Dokumentuj wyjątki w docstringach (sekcja `### Raises`)
- Używaj `try-except-finally` odpowiednio
- Unikaj "gołych" `except:` - zawsze określ typ wyjątku
- Loguj błędy przed re-raise lub obsługą

**Projekt używa JskToolBox:**

```python
# Projekt używa jsktoolbox z własnym mechanizmem obsługi błędów:
from jsktoolbox.raisetool import Raise
raise Raise.error(message, exception_type, class_name, frame)
```

### Kontrola wersji (Git)

**Konwencje commitów:**

- Format: `type(scope): subject` (Conventional Commits)
- Typy: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Przykład: `feat(parser): add support for JSON input`
- Długość subject: max 50 znaków
- Body (opcjonalnie): szczegółowy opis po pustej linii

**Branche:**

- `main` - stabilna wersja produkcyjna
- `develop` - główna gałąź rozwojowa
- `feature/*` - nowe funkcjonalności
- `bugfix/*` - poprawki błędów
- `hotfix/*` - pilne poprawki do produkcji

### Dokumentacja

**Struktura dokumentacji:**

- `README.md` - główny plik projektu (co, dlaczego, jak używać)
- `docs/` - szczegółowa dokumentacja techniczna
- `CHANGELOG.md` - historia zmian (Keep a Changelog format)
- `LICENSE` - licencja projektu
- `AGENTS.md` - konfiguracja AI

**Format dokumentacji kodu:**

- API: Generuj ze źródeł (Sphinx dla Python)
- Przykłady użycia w `examples/` lub `samples/`

### Ogólne zalecenia

**Komunikacja z AI Assistant:**

- **Język odpowiedzi**: Polski
- **Język kodu**: Angielski (komentarze, nazwy zmiennych, dokumentacja)
- **Język dokumentacji projektu**: Angielski (README, docs)
- **Język konfiguracji**: Polski (AGENTS.md)

**Podejście do zmian:**

- Zachowuj zwięzłą, techniczną formę odpowiedzi
- Przy zmianach obejmujących wiele plików przedstaw plan i poproś o akceptację
- Testuj zmiany przed commitem
- Dokumentuj nieoczywiste decyzje projektowe
- Refaktoryzuj kod zgodnie z DRY (Don't Repeat Yourself)
- Preferuj czytelność nad "sprytne" rozwiązania

**Code Review Checklist:**

- [ ] Kod jest zgodny z konwencjami projektu
- [ ] Testy zostały dodane/zaktualizowane
- [ ] Dokumentacja jest aktualna
- [ ] Brak ostrzeżeń z linterów
- [ ] Zmiany nie psują istniejącej funkcjonalności
- [ ] Obsługa błędów jest poprawna
- [ ] Kod jest czytelny i zrozumiały

---

## Narzędzia deweloperskie

**Podstawowe:**

- `black` - code formatter
- `pytest` - testing framework

**Rozszerzone (zalecane):**

- `pycodestyle` lub `flake8` - linting
- `mypy` - type checking
- `pytest-cov` - code coverage
- `isort` - import sorting

**Poetry dependencies:**

```toml
[tool.poetry.group.dev.dependencies]
black = "^26.1.0"
pytest = "^9.0.2"
```

---

## Dodatkowe zasoby

### Style Guides

- **Python**: [PEP 8](https://peps.python.org/pep-0008/), [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

### Narzędzia i dokumentacja

- **Poetry**: https://python-poetry.org/
- **JskToolBox**: https://github.com/Szumak75/JskToolBox
- **Conventional Commits**: https://www.conventionalcommits.org/

---

## Wersjonowanie

- **Wersja**: 1.0.0
- **Data utworzenia**: 2026-01-21
- **Autor**: Jacek 'Szumak' Kotlarski
- **Ostatnia aktualizacja**: 2026-01-21

### Historia zmian

- `1.0.0` (2026-01-21): Wersja wygenerowana z AGENTS-TEMPLATE.md dla projektu qnap-img-shrink
