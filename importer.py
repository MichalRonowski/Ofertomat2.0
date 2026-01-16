import pandas as pd
from typing import List, Dict, Optional
import re

class DataImporter:
    """Klasa do importu danych z plików CSV/Excel"""
    
    @staticmethod
    def parse_price_value(price_string) -> float:
        """
        Parsuje cenę obsługując polski format z przecinkiem
        Przykłady: "123,45", "123.45", "123"
        """
        if pd.isna(price_string):
            return 0.0
        
        price_str = str(price_string).strip()
        
        # Zamień przecinek na kropkę (polski format)
        price_str = price_str.replace(',', '.')
        
        try:
            return float(price_str)
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def parse_vat_rate(vat_string: str) -> float:
        """
        Parsuje stawkę VAT z różnych formatów
        Przykłady: "23%", "5 %", "0.23", "23"
        """
        if pd.isna(vat_string):
            return 23.0
        
        vat_str = str(vat_string).strip()
        
        # Usuń znak %
        vat_str = vat_str.replace('%', '').strip()
        
        try:
            vat_value = float(vat_str)
            
            # Sprawdź czy wartość jest NaN
            if pd.isna(vat_value):
                return 23.0
            
            # Jeśli wartość jest między 0 a 1 (włącznie), to jest w formacie dziesiętnym
            if 0 < vat_value <= 1:
                vat_value *= 100
            
            return vat_value
        except (ValueError, TypeError):
            return 23.0  # Domyślna stawka VAT
    
    @staticmethod
    def import_from_file(file_path: str, category_id: Optional[int] = None) -> List[Dict]:
        """
        Importuje produkty z pliku CSV lub Excel
        
        Mapowanie kolumn:
        - Nr -> code (indeks produktu)
        - Opis -> name (nazwa produktu)
        - Podst. jednostka miary -> unit
        - Ostatni koszt bezpośredni -> purchase_price_net
        - Tow. grupa księgowa VAT -> vat_rate
        
        Args:
            file_path: Ścieżka do pliku
            category_id: ID kategorii do przypisania (opcjonalne)
        
        Returns:
            Lista słowników z danymi produktów
        """
        # Wykryj typ pliku i wczytaj dane
        if file_path.endswith('.csv'):
            # Próbuj najpierw z separatorem średnik
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig', sep=';')
                # Jeśli mamy tylko jedną kolumnę, spróbuj z przecinkiem
                if len(df.columns) == 1:
                    df = pd.read_csv(file_path, encoding='utf-8-sig', sep=',')
            except:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
        elif file_path.endswith(('.xlsx', '.xls')):
            # Obsługa plików Excel z różnymi silnikami
            try:
                # Dla .xlsx używamy openpyxl (domyślnie)
                if file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path, engine='openpyxl')
                else:
                    # Dla starszych .xls próbujemy różnych silników
                    try:
                        df = pd.read_excel(file_path, engine='xlrd')
                    except:
                        # Jeśli xlrd nie zadziała, spróbuj openpyxl (może być .xls zapisany jako .xlsx)
                        df = pd.read_excel(file_path, engine='openpyxl')
            except Exception as e:
                raise ValueError(f"Nie można odczytać pliku Excel: {str(e)}\n"
                               f"Upewnij się, że plik nie jest otwarty w innym programie.")
        else:
            raise ValueError("Nieobsługiwany format pliku. Użyj CSV, XLS lub XLSX.")
        
        # Mapowanie nazw kolumn (elastyczne dopasowanie)
        column_mapping = {
            'Nr': 'code',
            'nr': 'code',
            'Indeks': 'code',
            'Kod': 'code',
            'kod': 'code',
            'Opis': 'name',
            'opis': 'name',
            'Nazwa': 'name',
            'nazwa': 'name',
            'Podst. jednostka miary': 'unit',
            'Jednostka': 'unit',
            'jednostka': 'unit',
            'JM': 'unit',
            'Ostatni koszt bezpośredni': 'purchase_price_net',
            'Cena zakupu': 'purchase_price_net',
            'Cena zakupu netto': 'purchase_price_net',
            'cena zakupu': 'purchase_price_net',
            'cena zakupu netto': 'purchase_price_net',
            'Cena': 'purchase_price_net',
            'cena': 'purchase_price_net',
            'Koszt': 'purchase_price_net',
            'koszt': 'purchase_price_net',
            'Koszt jednostkowy': 'purchase_price_net',
            'koszt jednostkowy': 'purchase_price_net',
            'Cena netto': 'purchase_price_net',
            'cena netto': 'purchase_price_net',
            'Wartość': 'purchase_price_net',
            'wartość': 'purchase_price_net',
            'Tow. grupa księgowa VAT': 'vat_rate',
            'VAT': 'vat_rate',
            'Vat': 'vat_rate',
            'vat': 'vat_rate',
            'Stawka VAT': 'vat_rate',
            'stawka vat': 'vat_rate'
        }
        
        # Znajdź i zmapuj kolumny
        renamed_columns = {}
        original_columns = list(df.columns)
        
        for col in df.columns:
            col_clean = col.strip()
            if col_clean in column_mapping:
                renamed_columns[col] = column_mapping[col_clean]
        
        df = df.rename(columns=renamed_columns)
        
        # Sprawdź czy mamy wymagane kolumny
        required_columns = ['code', 'name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            # Pokaż bardziej szczegółowy błąd z listą dostępnych kolumn
            available_cols = ', '.join([f'"{col}"' for col in original_columns])
            mapped_cols = ', '.join([f'"{k}" -> "{v}"' for k, v in renamed_columns.items()])
            error_msg = (
                f"Brak wymaganych kolumn: {', '.join(missing_columns)}\n\n"
                f"Kolumny w pliku: {available_cols}\n"
                f"Zmapowane kolumny: {mapped_cols if mapped_cols else 'brak'}"
            )
            raise ValueError(error_msg)
        
        # Informacja diagnostyczna - jeśli nie znaleziono kolumny z ceną
        if 'purchase_price_net' not in df.columns:
            import warnings
            available_cols = ', '.join([f'"{col}"' for col in original_columns])
            warnings.warn(
                f"Nie znaleziono kolumny z ceną!\n"
                f"Kolumny w pliku: {available_cols}\n"
                f"Ceny zostaną ustawione na 0.0"
            )
        
        # Ustaw domyślne wartości dla brakujących kolumn
        if 'unit' not in df.columns:
            df['unit'] = 'szt.'
        if 'purchase_price_net' not in df.columns:
            df['purchase_price_net'] = 0.0
        if 'vat_rate' not in df.columns:
            df['vat_rate'] = 23.0
        
        # Przetwórz dane
        products = []
        for _, row in df.iterrows():
            # Pomiń puste wiersze
            if pd.isna(row['code']) or str(row['code']).strip() == '':
                continue
            
            product = {
                'code': str(row['code']).strip(),
                'name': str(row['name']).strip() if not pd.isna(row['name']) else '',
                'unit': str(row['unit']).strip() if not pd.isna(row['unit']) else 'szt.',
                'purchase_price_net': DataImporter.parse_price_value(row['purchase_price_net']),
                'vat_rate': DataImporter.parse_vat_rate(row['vat_rate']),
                'category_id': category_id
            }
            
            products.append(product)
        
        return products
    
    @staticmethod
    def validate_import_file(file_path: str) -> Dict[str, any]:
        """
        Waliduje plik przed importem
        
        Returns:
            Słownik z informacjami: 
            - valid: bool
            - message: str
            - preview: List[Dict] (pierwsze 5 rekordów)
            - total_rows: int
        """
        try:
            # Sprawdź czy plik istnieje
            import os
            if not os.path.exists(file_path):
                return {
                    'valid': False,
                    'message': 'Plik nie istnieje',
                    'preview': [],
                    'total_rows': 0
                }
            
            # Wczytaj plik w zależności od rozszerzenia
            if file_path.endswith('.csv'):
                try:
                    df = pd.read_csv(file_path, encoding='utf-8-sig', sep=';')
                    if len(df.columns) == 1:
                        df = pd.read_csv(file_path, encoding='utf-8-sig', sep=',')
                except:
                    df = pd.read_csv(file_path, encoding='utf-8-sig')
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path, engine='openpyxl')
            elif file_path.endswith('.xls'):
                try:
                    df = pd.read_excel(file_path, engine='xlrd')
                except:
                    df = pd.read_excel(file_path, engine='openpyxl')
            else:
                return {
                    'valid': False,
                    'message': 'Nieobsługiwany format pliku',
                    'preview': [],
                    'total_rows': 0
                }
            
            # Sprawdź czy są jakieś dane
            if len(df) == 0:
                return {
                    'valid': False,
                    'message': 'Plik jest pusty',
                    'preview': [],
                    'total_rows': 0
                }
            
            # Podgląd pierwszych 5 wierszy
            preview = df.head(5).to_dict('records')
            
            return {
                'valid': True,
                'message': f'Plik zawiera {len(df)} wierszy',
                'preview': preview,
                'total_rows': len(df),
                'columns': list(df.columns)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'message': f'Błąd odczytu pliku: {str(e)}',
                'preview': [],
                'total_rows': 0
            }
