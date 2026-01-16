"""
Skrypt do budowania aplikacji Ofertomat 2.0 jako samodzielny plik .exe
Używa PyInstaller do stworzenia standalone aplikacji
"""

import PyInstaller.__main__
import os
import shutil
from pathlib import Path

def build_application():
    """Buduje aplikację jako .exe"""
    
    # Ścieżki
    project_dir = Path(__file__).parent
    dist_dir = project_dir / "dist"
    build_dir = project_dir / "build"
    
    # Czyszczenie poprzednich buildów
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    print("🔨 Budowanie Ofertomat 2.0...")
    
    # Parametry PyInstaller
    PyInstaller.__main__.run([
        'main.py',                          # Główny plik
        '--name=Ofertomat2.0',              # Nazwa aplikacji
        '--onefile',                        # Jeden plik .exe
        '--windowed',                       # Bez okna konsoli
        '--icon=NONE',                      # Możesz dodać .ico
        '--add-data=produkty_gastronomia_przyklad.csv;.',  # Przykładowe dane
        '--hidden-import=customtkinter',
        '--hidden-import=PIL._tkinter_finder',
        '--collect-all=customtkinter',
        '--noconfirm',                      # Bez pytania o nadpisanie
    ])
    
    print("\n✅ Budowanie zakończone!")
    print(f"📦 Plik .exe znajduje się w: {dist_dir / 'Ofertomat2.0.exe'}")
    
    # Kopiowanie dodatkowych plików
    dist_ofertomat = dist_dir / "Ofertomat2.0"
    if dist_ofertomat.exists():
        readme_dest = dist_ofertomat / "README.txt"
        with open(readme_dest, 'w', encoding='utf-8') as f:
            f.write("""
Ofertomat 2.0 - Instrukcja użytkowania

1. Uruchom Ofertomat2.0.exe
2. Importuj produkty z pliku CSV/Excel (Zarządzaj produktami > Import)
3. Stwórz ofertę wybierając produkty
4. Wygeneruj PDF

Wsparcie: kontakt@ofertomat.pl
            """)
        print(f"📄 Dodano README.txt")

if __name__ == "__main__":
    build_application()
