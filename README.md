# Ofertomat 2.0

**Nowoczesna aplikacja desktopowa do zarządzania ofertami handlowymi**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-green.svg)
![License](https://img.shields.io/badge/License-Proprietary-red.svg)

---

## 📋 Opis

Ofertomat 2.0 to profesjonalne narzędzie stworzone w Python z nowoczesnym interfejsem graficznym (Dark Mode) opartym na bibliotece **CustomTkinter**. Aplikacja umożliwia:

- ✅ Zarządzanie bazą produktów
- ✅ Import danych z plików CSV/Excel
- ✅ Generowanie profesjonalnych ofert handlowych w formacie PDF
- ✅ Wyszukiwanie i filtrowanie produktów
- ✅ Zarządzanie kategoriami i cenami

---

## 🚀 Szybki Start

### Wymagania wstępne

- **Python 3.8 lub nowszy**
- System operacyjny: Windows 10/11, Linux, macOS

### Instalacja

1. **Sklonuj lub pobierz projekt:**
   ```bash
   cd Ofertomat2.0
   ```

2. **Struktura projektu:**
   
   Wszystkie niezbędne pliki znajdują się w folderze projektu:
   ```
   Ofertomat2.0/
   ├── main.py              # Główny plik aplikacji (GUI)
   ├── database.py          # Moduł zarządzania bazą danych
   ├── importer.py          # Moduł importu CSV/Excel
   ├── pdf_generator.py     # Generator PDF
   ├── requirements.txt     # Wymagane biblioteki
   └── README.md            # Dokumentacja
   ```

3. **Zainstaluj wymagane biblioteki:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Uruchom aplikację:**
   ```bash
   python main.py
   ```

---

## 🖥️ Interfejs Użytkownika

### Lewy Panel (Menu Akcji)

- **📥 Załaduj Bazę (CSV)** - Importuj produkty z pliku CSV lub Excel
- **🔄 Odśwież Dane** - Przeładuj listę produktów z bazy danych
- **📄 Generuj Ofertę PDF** - Stwórz profesjonalną ofertę z zaznaczonych produktów
- **📁 Kategorie** - Zarządzaj kategoriami produktów *(w przygotowaniu)*
- **💾 Zapisane Oferty** - Przeglądaj wcześniej utworzone oferty *(w przygotowaniu)*

### Prawy Panel (Widok Danych)

- **Pasek wyszukiwania** - Szybkie filtrowanie po nazwie lub kodzie produktu
- **Tabela produktów** - Wyświetla:
  - Checkbox do zaznaczania
  - Kod produktu
  - Nazwa
  - Jednostka miary
  - Cena zakupu netto
  - Stawka VAT
  - Kategoria

---

## 📦 Funkcjonalności

### 1. Import danych

Aplikacja obsługuje import z plików:
- **CSV** (separator: `;` lub `,`)
- **Excel** (`.xlsx`, `.xls`)

Rozpoznawane kolumny:
- `Nr` / `Kod` → kod produktu
- `Opis` / `Nazwa` → nazwa produktu
- `Podst. jednostka miary` / `Jednostka` → jednostka
- `Ostatni koszt bezpośredni` / `Cena zakupu` → cena netto
- `Tow. grupa księgowa VAT` / `VAT` → stawka VAT

### 2. Generowanie PDF

Oferty są generowane z:
- Logo firmy (jeśli istnieje `logo_piwowar.png`)
- Danymi kontaktowymi z wizytówki
- Produktami pogrupowanymi według kategorii
- Automatycznym obliczaniem cen brutto
- Profesjonalnym formatowaniem

### 3. Baza danych SQLite

Aplikacja automatycznie tworzy i zarządza bazą `ofertomat.db` zawierającą:
- Produkty
- Kategorie
- Zapisane oferty
- Wizytówkę użytkownika

---

## 🛠️ Architektura

```
main.py (GUI - CustomTkinter)
    ↓
    ├── database.py (Warstwa danych - SQLite)
    ├── importer.py (Import CSV/Excel)
    └── pdf_generator.py (Generowanie PDF - ReportLab)
```

### Klasa główna: `App(ctk.CTk)`

- **`setup_ui()`** - Buduje kompletny interfejs
- **`create_left_panel()`** - Tworzy menu akcji
- **`create_right_panel()`** - Tworzy tabelę danych
- **`load_products()`** - Ładuje produkty z bazy
- **`load_csv_file()`** - Obsługuje import
- **`generate_offer_pdf()`** - Tworzy dokumenty PDF

---

## 🎨 Customizacja

### Kolory motywu

Główne kolory aplikacji (zgodne z identyfikacją wizualną):
- **Czerwony**: `#C8102E` (przyciski główne, nagłówki kategorii)
- **Niebieski**: `#3B8ED0` (przyciski akcji)
- **Dark Mode**: Automatycznie włączony

### Zmiana motywu

W pliku `main.py`, metoda `__init__()`:
```python
ctk.set_appearance_mode("dark")  # "light", "dark", "system"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
```

---

## 🔧 Rozwiązywanie problemów

### Błąd: "No module named 'customtkinter'"
```bash
pip install customtkinter
```

### Błąd: "No module named 'database'" lub podobny
Upewnij się, że uruchamiasz aplikację z katalogu Ofertomat2.0, który zawiera wszystkie moduły.

### Brak czcionek w PDF
Aplikacja automatycznie używa czcionki Arial z systemu Windows. Na Linux/macOS może użyć Helvetica.

---

## 📝 Licencja

Proprietary - Wszystkie prawa zastrzeżone

---

## 👨‍💻 Autor

Stworzone przez Senior Python Developera  
Wersja: **2.0.0**  
Data: Styczeń 2026

---

## 🚧 Roadmapa

- [x] Interfejs CustomTkinter z Dark Mode
- [x] Import CSV/Excel
- [x] Generowanie PDF
- [x] Wyszukiwanie produktów
- [ ] Zarządzanie kategoriami (GUI)
- [ ] Przeglądanie zapisanych ofert
- [ ] Edycja wizytówki użytkownika
- [ ] Eksport danych do Excel
- [ ] Historia zmian cen
- [ ] Raporty sprzedażowe

---

**Miłego użytkowania! 🎉**
