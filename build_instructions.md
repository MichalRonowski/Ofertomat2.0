# Instrukcja Budowania i Dystrybucji Ofertomat 2.0

## 🎯 Przygotowanie do produkcji

### Opcja 1: Pojedynczy plik EXE (Zalecane dla Windows)

**Krok 1: Zainstaluj PyInstaller**
```powershell
pip install pyinstaller
```

**Krok 2: Zbuduj aplikację**
```powershell
python build_exe.py
```

**Wynik:**
- Plik `dist/Ofertomat2.0.exe` - gotowy do dystrybucji
- Rozmiar: ~100-150 MB (zawiera interpreter Python i wszystkie biblioteki)
- Nie wymaga instalacji Pythona u użytkownika

**Krok 3: Testowanie**
```powershell
cd dist
./Ofertomat2.0.exe
```

---

### Opcja 2: Folder z zależnościami (mniejszy rozmiar)

Jeśli chcesz mniejszy plik i szybsze uruchamianie:

```powershell
pyinstaller main.py ^
  --name=Ofertomat2.0 ^
  --windowed ^
  --add-data="produkty_gastronomia_przyklad.csv;." ^
  --collect-all=customtkinter ^
  --hidden-import=PIL._tkinter_finder ^
  --noconfirm
```

Wynik: folder `dist/Ofertomat2.0/` z plikiem .exe i bibliotekami

---

### Opcja 3: Instalator dla użytkowników końcowych

**Krok 1: Pobierz Inno Setup**
- Strona: https://jrsoftware.org/isinfo.php
- Zainstaluj Inno Setup Compiler

**Krok 2: Użyj skryptu instalatora**
```powershell
# Najpierw zbuduj .exe
python build_exe.py

# Potem uruchom:
iscc ofertomat_installer.iss
```

Wynik: `Output/Ofertomat2.0_Setup.exe` - profesjonalny instalator

---

## 📦 Co zawiera paczka dystrybucyjna?

- ✅ Ofertomat2.0.exe (aplikacja)
- ✅ Wszystkie biblioteki (wbudowane)
- ✅ Przykładowy plik CSV
- ✅ Baza danych (tworzona przy pierwszym uruchomieniu)

---

## 🚀 Dystrybucja dla użytkownika końcowego

### Metoda 1: Plik ZIP
```powershell
# Po zbudowaniu:
Compress-Archive -Path dist/Ofertomat2.0.exe -DestinationPath Ofertomat2.0_v1.0.zip
```

**Instrukcja dla użytkownika:**
1. Rozpakuj ZIP
2. Uruchom Ofertomat2.0.exe
3. Gotowe!

### Metoda 2: Instalator
- Uruchom Ofertomat2.0_Setup.exe
- Postępuj zgodnie z instrukcjami
- Aplikacja zostanie zainstalowana w Program Files
- Zostanie dodana ikona na pulpicie i w menu Start

---

## ⚠️ Ważne uwagi

### Antywirus/Windows Defender
Aplikacje .exe stworzone PyInstallerem mogą być oznaczane jako "podejrzane" przez niektóre antywirusy (fałszywe alarmy).

**Rozwiązania:**
1. **Podpisz cyfrowo aplikację** (wymaga certyfikatu Code Signing)
2. **Dodaj wyjątek w Windows Defender** (dla testów)
3. **Zgłoś fałszywy alarm** do Microsoft

### Podpis cyfrowy (opcjonalnie)
Dla profesjonalnej dystrybucji:
```powershell
signtool sign /f certyfikat.pfx /p hasło /t http://timestamp.digicert.com Ofertomat2.0.exe
```

---

## 🔧 Rozwiązywanie problemów

### Problem: "Nie można uruchomić - brakuje DLL"
**Rozwiązanie:** Użyj `--onefile` lub dołącz Visual C++ Redistributable

### Problem: Aplikacja uruchamia się wolno
**Rozwiązanie:** Użyj opcji bez `--onefile` (szybsze, ale więcej plików)

### Problem: Baza danych nie działa
**Rozwiązanie:** Sprawdź, czy `ofertomat.db` ma uprawnienia do zapisu

### Problem: Duży rozmiar pliku
**Rozwiązanie:** Użyj UPX do kompresji:
```powershell
pyinstaller ... --upx-dir=C:\path\to\upx
```

---

## 📊 Porównanie metod

| Metoda | Rozmiar | Szybkość | Łatwość | Profesjonalizm |
|--------|---------|----------|---------|----------------|
| --onefile | 100-150 MB | Wolne uruchomienie | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| --onedir | 150-200 MB | Szybkie | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Instalator | ~100 MB | Szybkie | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## ✅ Checklist przed wydaniem

- [ ] Przetestuj .exe na czystym systemie Windows
- [ ] Sprawdź, czy wszystkie funkcje działają
- [ ] Przetestuj import CSV/Excel
- [ ] Sprawdź generowanie PDF
- [ ] Zweryfikuj bazę danych
- [ ] Przygotuj dokumentację dla użytkownika
- [ ] Utwórz notes wersji (changelog)

---

## 📞 Wsparcie

W razie problemów skontaktuj się z deweloperem lub sprawdź dokumentację:
- PyInstaller: https://pyinstaller.org/
- CustomTkinter: https://customtkinter.tomschimansky.com/
