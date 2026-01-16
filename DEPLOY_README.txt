================================================================================
  OFERTOMAT 2.0 - SZYBKA INSTRUKCJA WDROŻENIA
================================================================================

🚀 NAJSZYBSZA METODA (dla Windows):

1. Otwórz PowerShell w folderze projektu
2. Zainstaluj PyInstaller:
   pip install pyinstaller

3. Zbuduj aplikację:
   python build_exe.py

4. Znajdź plik:
   dist\Ofertomat2.0.exe

5. Prześlij użytkownikowi - GOTOWE!

================================================================================

📦 CO OTRZYMA UŻYTKOWNIK:

- Pojedynczy plik .exe (100-150 MB)
- Nie wymaga instalacji Pythona
- Działa od razu po uruchomieniu
- Tworzy swoją bazę danych automatycznie

================================================================================

⚠️ WAŻNE UWAGI:

1. WINDOWS DEFENDER: Może oznaczyć plik jako podejrzany (fałszywy alarm).
   Rozwiązanie: Dodaj wyjątek lub podpisz cyfrowo aplikację.

2. PIERWSZE URUCHOMIENIE: Może potrwać 10-30 sekund (rozpakowywanie).
   Kolejne uruchomienia będą szybsze.

3. TESTOWANIE: Zawsze przetestuj .exe na czystym komputerze przed wysłaniem!

================================================================================

📋 ALTERNATYWNE METODY:

A) FOLDER Z PLIKAMI (szybsze uruchamianie):
   pyinstaller main.py --windowed --collect-all=customtkinter

B) INSTALATOR INNO SETUP (najbardziej profesjonalne):
   1. Pobierz Inno Setup: https://jrsoftware.org/isinfo.php
   2. Otwórz ofertomat_installer.iss
   3. Skompiluj (Build > Compile)
   4. Znajdź: Output\Ofertomat2.0_Setup.exe

================================================================================

🔧 ROZWIĄZYWANIE PROBLEMÓW:

Problem: PyInstaller nie jest zainstalowany
Rozwiązanie: pip install pyinstaller

Problem: Błąd podczas budowania
Rozwiązanie: pip install --upgrade -r requirements.txt

Problem: .exe nie uruchamia się
Rozwiązanie: Sprawdź logi w: dist\Ofertomat2.0\_internal\

================================================================================

📞 POTRZEBUJESZ POMOCY?

Zobacz szczegółową dokumentację w pliku: build_instructions.md

================================================================================
