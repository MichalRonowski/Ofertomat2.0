from datetime import datetime
from typing import List, Dict, Optional, Tuple
import sqlite3
import json

class Database:
    def __init__(self, db_path: str = "ofertomat.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Tworzy połączenie z bazą danych"""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        
        # Dodaj funkcję do obsługi polskich znaków w wyszukiwaniu
        def polish_lower(text):
            if text is None:
                return ""
            return text.lower()
        
        conn.create_function("POLISH_LOWER", 1, polish_lower)
        return conn
    
    def init_database(self):
        """Inicjalizuje bazę danych z tabelami"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela Categories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                default_margin REAL DEFAULT 0.0
            )
        ''')
        
        # Tabela Products
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT,
                name TEXT NOT NULL,
                unit TEXT DEFAULT 'szt.',
                purchase_price_net REAL DEFAULT 0.0,
                price_update_date TEXT,
                vat_rate REAL DEFAULT 23.0,
                category_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES Categories(id)
            )
        ''')
        
        # Indeksy dla optymalizacji wydajności
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_category ON Products(category_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_code ON Products(code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_name ON Products(name COLLATE NOCASE)')
        
        # Tabela BusinessCard
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS BusinessCard (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                full_name TEXT,
                phone TEXT,
                email TEXT
            )
        ''')
        
        # Migracja: dodaj kolumnę company jeśli nie istnieje
        cursor.execute("PRAGMA table_info(BusinessCard)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'company' not in columns:
            cursor.execute("ALTER TABLE BusinessCard ADD COLUMN company TEXT")
            print("Dodano kolumnę 'company' do tabeli BusinessCard")
        
        # Migracja: usuń constraint UNIQUE i NOT NULL z kolumny code w Products
        # SQLite nie pozwala na bezpośrednią modyfikację constraints, więc musimy przebudować tabelę
        cursor.execute("PRAGMA table_info(Products)")
        products_columns = cursor.fetchall()
        
        # Sprawdź czy trzeba wykonać migrację (sprawdzamy czy code ma NOT NULL)
        code_column = [col for col in products_columns if col[1] == 'code']
        if code_column and code_column[0][3] == 1:  # notnull == 1
            print("Wykonuję migrację: usuwanie wymagania pola 'code' w Products...")
            
            # Utwórz tabelę tymczasową z nową strukturą
            cursor.execute('''
                CREATE TABLE Products_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT,
                    name TEXT NOT NULL,
                    unit TEXT DEFAULT 'szt.',
                    purchase_price_net REAL DEFAULT 0.0,
                    price_update_date TEXT,
                    vat_rate REAL DEFAULT 23.0,
                    category_id INTEGER,
                    FOREIGN KEY (category_id) REFERENCES Categories(id)
                )
            ''')
            
            # Skopiuj dane
            cursor.execute('''
                INSERT INTO Products_new (id, code, name, unit, purchase_price_net, 
                                         price_update_date, vat_rate, category_id)
                SELECT id, code, name, unit, purchase_price_net, 
                       price_update_date, vat_rate, category_id
                FROM Products
            ''')
            
            # Usuń starą tabelę i przemianuj nową
            cursor.execute('DROP TABLE Products')
            cursor.execute('ALTER TABLE Products_new RENAME TO Products')
            
            # Odtwórz indeksy
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_category ON Products(category_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_code ON Products(code)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_name ON Products(name COLLATE NOCASE)')
            
            print("Migracja zakończona: pole 'code' jest teraz opcjonalne")
        
        # Tabela SavedOffers - zapisane oferty
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS SavedOffers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_date TEXT NOT NULL,
                modified_date TEXT NOT NULL,
                category_order TEXT
            )
        ''')
        
        # Tabela SavedOfferItems - pozycje w zapisanych ofertach
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS SavedOfferItems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                offer_id INTEGER NOT NULL,
                product_id INTEGER,
                name TEXT NOT NULL,
                category_name TEXT,
                unit TEXT,
                purchase_price_net REAL,
                vat_rate REAL,
                margin REAL,
                FOREIGN KEY (offer_id) REFERENCES SavedOffers(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_offer_items_offer ON SavedOfferItems(offer_id)')
        
        # Migracja: dodaj kolumnę quantity jeśli nie istnieje
        cursor.execute("PRAGMA table_info(SavedOfferItems)")
        offer_items_columns = [row[1] for row in cursor.fetchall()]
        if 'quantity' not in offer_items_columns:
            cursor.execute("ALTER TABLE SavedOfferItems ADD COLUMN quantity REAL DEFAULT 1.0")
            print("Dodano kolumnę 'quantity' do tabeli SavedOfferItems")
        
        # Dodaj domyślną kategorię jeśli baza jest pusta
        cursor.execute('SELECT COUNT(*) as count FROM Categories')
        if cursor.fetchone()['count'] == 0:
            cursor.execute('INSERT INTO Categories (name, default_margin) VALUES (?, ?)', 
                         ('Bez kategorii', 30.0))
        
        conn.commit()
        conn.close()
    
    # === KATEGORIE ===
    
    def add_category(self, name: str, default_margin: float) -> Optional[int]:
        """Dodaje nową kategorię i zwraca jej ID"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO Categories (name, default_margin) VALUES (?, ?)', 
                         (name, default_margin))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            if conn:
                conn.close()
    
    def get_categories(self) -> List[Dict]:
        """Pobiera wszystkie kategorie"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Categories ORDER BY name')
            categories = [dict(row) for row in cursor.fetchall()]
        return categories
    
    def update_category(self, category_id: int, name: str, default_margin: float) -> bool:
        """Aktualizuje kategorię"""
        conn = None
        retries = 3
        for attempt in range(retries):
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute('UPDATE Categories SET name = ?, default_margin = ? WHERE id = ?', 
                             (name, default_margin, category_id))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
            except sqlite3.OperationalError as e:
                if attempt < retries - 1:
                    continue
                return False
            finally:
                if conn:
                    conn.close()
        return False
    
    def delete_category(self, category_id: int) -> bool:
        """Usuwa kategorię - produkty z tej kategorii otrzymują kategorię 'Bez kategorii'"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Znajdź lub utwórz kategorię "Bez kategorii"
            cursor.execute('SELECT id FROM Categories WHERE name = ?', ('Bez kategorii',))
            default_cat = cursor.fetchone()
            
            if not default_cat:
                # Utwórz kategorię "Bez kategorii" jeśli nie istnieje
                cursor.execute('INSERT INTO Categories (name, default_margin) VALUES (?, ?)', 
                             ('Bez kategorii', 30.0))
                default_cat_id = cursor.lastrowid
            else:
                default_cat_id = default_cat['id']
            
            # Nie pozwól usunąć kategorii "Bez kategorii"
            cursor.execute('SELECT name FROM Categories WHERE id = ?', (category_id,))
            cat_name = cursor.fetchone()
            if cat_name and cat_name['name'] == 'Bez kategorii':
                return False
            
            # Przepisz produkty do kategorii "Bez kategorii"
            cursor.execute('UPDATE Products SET category_id = ? WHERE category_id = ?', 
                         (default_cat_id, category_id))
            
            # Usuń kategorię
            cursor.execute('DELETE FROM Categories WHERE id = ?', (category_id,))
            conn.commit()
            return True
        finally:
            if conn:
                conn.close()
    
    # === PRODUKTY ===
    
    def add_product(self, code: Optional[str], name: str, unit: str, purchase_price_net: float, 
                   vat_rate: float, category_id: Optional[int] = None) -> Optional[int]:
        """Dodaje nowy produkt, zwraca ID produktu lub None w przypadku błędu"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO Products (code, name, unit, purchase_price_net, price_update_date, vat_rate, category_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (code, name, unit, purchase_price_net, now, vat_rate, category_id))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            if conn:
                conn.close()
    
    def update_product(self, product_id: int, code: Optional[str], name: str, unit: str, 
                      purchase_price_net: float, vat_rate: float, category_id: Optional[int]) -> bool:
        """Aktualizuje produkt"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Sprawdź czy kod nie jest używany przez inny produkt (jeśli kod jest podany)
            if code:
                cursor.execute('SELECT id FROM Products WHERE code = ? AND id != ?', (code, product_id))
                if cursor.fetchone():
                    return False
            
            # Pobierz starą cenę
            cursor.execute('SELECT purchase_price_net FROM Products WHERE id = ?', (product_id,))
            old_price_row = cursor.fetchone()
            if not old_price_row:
                return False
            
            old_price = old_price_row['purchase_price_net']
            
            # Jeśli cena się zmieniła, zaktualizuj datę
            if abs(old_price - purchase_price_net) > 0.001:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('''
                    UPDATE Products SET code = ?, name = ?, unit = ?, purchase_price_net = ?, 
                                       price_update_date = ?, vat_rate = ?, category_id = ?
                    WHERE id = ?
                ''', (code, name, unit, purchase_price_net, now, vat_rate, category_id, product_id))
            else:
                cursor.execute('''
                    UPDATE Products SET code = ?, name = ?, unit = ?, vat_rate = ?, category_id = ?
                    WHERE id = ?
                ''', (code, name, unit, vat_rate, category_id, product_id))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            if conn:
                conn.close()
    
    def delete_product(self, product_id: int) -> bool:
        """Usuwa produkt"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM Products WHERE id = ?', (product_id,))
            conn.commit()
            return True
        finally:
            if conn:
                conn.close()
    
    def get_products(self, category_id: Optional[int] = None) -> List[Dict]:
        """Pobiera produkty (opcjonalnie filtrowane po kategorii)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if category_id is not None:
            cursor.execute('''
                SELECT p.*, c.name as category_name, c.default_margin
                FROM Products p
                LEFT JOIN Categories c ON p.category_id = c.id
                WHERE p.category_id = ?
                ORDER BY p.name
            ''', (category_id,))
        else:
            cursor.execute('''
                SELECT p.*, c.name as category_name, c.default_margin
                FROM Products p
                LEFT JOIN Categories c ON p.category_id = c.id
                ORDER BY p.name
            ''')
        
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return products
    
    def get_products_paginated(self, category_id: Optional[int] = None, 
                              search_query: str = "", page: int = 1, 
                              page_size: int = 50) -> Tuple[List[Dict], int]:
        """Pobiera produkty z paginacją
        Returns: (lista produktów, całkowita liczba produktów)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        offset = (page - 1) * page_size
        
        # Buduj zapytanie dynamicznie
        where_clauses = []
        params = []
        
        if category_id is not None:
            where_clauses.append('p.category_id = ?')
            params.append(category_id)
        
        if search_query:
            where_clauses.append('(POLISH_LOWER(p.name) LIKE POLISH_LOWER(?) OR POLISH_LOWER(p.code) LIKE POLISH_LOWER(?))')
            search_pattern = f'%{search_query}%'
            params.extend([search_pattern, search_pattern])
        
        where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'
        
        # Zlicz całkowitą liczbę
        count_query = f'SELECT COUNT(*) as total FROM Products p WHERE {where_sql}'
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        # Pobierz stronę danych
        query = f'''
            SELECT p.*, c.name as category_name, c.default_margin
            FROM Products p
            LEFT JOIN Categories c ON p.category_id = c.id
            WHERE {where_sql}
            ORDER BY p.name
            LIMIT ? OFFSET ?
        '''
        cursor.execute(query, params + [page_size, offset])
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return products, total
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Pobiera produkt po ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, c.name as category_name, c.default_margin
            FROM Products p
            LEFT JOIN Categories c ON p.category_id = c.id
            WHERE p.id = ?
        ''', (product_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def search_products(self, query: str) -> List[Dict]:
        """Wyszukuje produkty po nazwie lub kodzie"""
        conn = self.get_connection()
        cursor = conn.cursor()
        search_pattern = f'%{query}%'
        cursor.execute('''
            SELECT p.*, c.name as category_name, c.default_margin
            FROM Products p
            LEFT JOIN Categories c ON p.category_id = c.id
            WHERE p.name LIKE ? OR p.code LIKE ?
            ORDER BY p.name
        ''', (search_pattern, search_pattern))
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return products
    
    def import_products_batch(self, products: List[Dict]) -> Tuple[int, int]:
        """
        Importuje wiele produktów naraz
        Zwraca (liczba dodanych, liczba zaktualizowanych)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        added = 0
        updated = 0
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for product in products:
            # Sprawdź czy produkt już istnieje
            cursor.execute('SELECT id, purchase_price_net FROM Products WHERE code = ?', 
                         (product['code'],))
            existing = cursor.fetchone()
            
            if existing:
                # Aktualizuj istniejący produkt
                cursor.execute('''
                    UPDATE Products 
                    SET name = ?, unit = ?, purchase_price_net = ?, price_update_date = ?, 
                        vat_rate = ?, category_id = ?
                    WHERE id = ?
                ''', (product['name'], product['unit'], product['purchase_price_net'], 
                     now, product['vat_rate'], product.get('category_id'), existing['id']))
                updated += 1
            else:
                # Dodaj nowy produkt
                cursor.execute('''
                    INSERT INTO Products (code, name, unit, purchase_price_net, price_update_date, vat_rate, category_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (product['code'], product['name'], product['unit'], product['purchase_price_net'],
                     now, product['vat_rate'], product.get('category_id')))
                added += 1
        
        conn.commit()
        conn.close()
        return added, updated
    
    # === WIZYTÓWKA ===
    
    def get_business_card(self) -> Optional[Dict]:
        """Pobiera wizytówkę użytkownika"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM BusinessCard WHERE id = 1')
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def save_business_card(self, company: str, full_name: str, phone: str, email: str) -> bool:
        """Zapisuje lub aktualizuje wizytówkę użytkownika"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO BusinessCard (id, company, full_name, phone, email)
                    VALUES (1, ?, ?, ?, ?)
                ''', (company, full_name, phone, email))
                conn.commit()
            return True
        except Exception as e:
            print(f"Błąd zapisywania wizytówki: {e}")
            return False
    
    # === ZAPISANE OFERTY ===
    
    def save_offer(self, title: str, items: List[Dict], category_order: Dict) -> int:
        """Zapisuje nową ofertę i zwraca jej ID"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Zapisz ofertę
            cursor.execute('''
                INSERT INTO SavedOffers (title, created_date, modified_date, category_order)
                VALUES (?, ?, ?, ?)
            ''', (title, now, now, json.dumps(category_order)))
            
            offer_id = cursor.lastrowid
            
            # Zapisz pozycje oferty
            for item in items:
                cursor.execute('''
                    INSERT INTO SavedOfferItems (offer_id, product_id, name, category_name, unit, 
                                                purchase_price_net, vat_rate, margin, quantity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (offer_id, item.get('product_id'), item['name'], item.get('category_name'),
                     item.get('unit'), item.get('purchase_price_net'), item.get('vat_rate'),
                     item.get('margin'), item.get('quantity', 1.0)))
            
            conn.commit()
            return offer_id
        except Exception as e:
            print(f"Błąd zapisywania oferty: {e}")
            if conn:
                conn.rollback()
            return 0
        finally:
            if conn:
                conn.close()
    
    def update_offer(self, offer_id: int, title: str, items: List[Dict], category_order: Dict) -> bool:
        """Aktualizuje istniejącą ofertę"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Aktualizuj ofertę
            cursor.execute('''
                UPDATE SavedOffers 
                SET title = ?, modified_date = ?, category_order = ?
                WHERE id = ?
            ''', (title, now, json.dumps(category_order), offer_id))
            
            # Usuń stare pozycje
            cursor.execute('DELETE FROM SavedOfferItems WHERE offer_id = ?', (offer_id,))
            
            # Dodaj nowe pozycje
            for item in items:
                cursor.execute('''
                    INSERT INTO SavedOfferItems (offer_id, product_id, name, category_name, unit,
                                                purchase_price_net, vat_rate, margin, quantity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (offer_id, item.get('product_id'), item['name'], item.get('category_name'),
                     item.get('unit'), item.get('purchase_price_net'), item.get('vat_rate'),
                     item.get('margin'), item.get('quantity', 1.0)))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Błąd aktualizacji oferty: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def get_saved_offers(self) -> List[Dict]:
        """Pobiera listę wszystkich zapisanych ofert"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM SavedOffers ORDER BY modified_date DESC')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_offer_by_id(self, offer_id: int) -> Optional[Dict]:
        """Pobiera szczegóły oferty po ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Pobierz ofertę
        cursor.execute('SELECT * FROM SavedOffers WHERE id = ?', (offer_id,))
        offer_row = cursor.fetchone()
        
        if not offer_row:
            conn.close()
            return None
        
        offer = dict(offer_row)
        
        # Parsuj category_order z JSON
        try:
            offer['category_order'] = json.loads(offer['category_order']) if offer['category_order'] else {}
        except:
            offer['category_order'] = {}
        
        # Pobierz pozycje oferty
        cursor.execute('''
            SELECT * FROM SavedOfferItems 
            WHERE offer_id = ?
            ORDER BY id
        ''', (offer_id,))
        
        offer['items'] = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return offer
    
    def delete_offer(self, offer_id: int) -> bool:
        """Usuwa ofertę"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM SavedOffers WHERE id = ?', (offer_id,))
                conn.commit()
            return True
        except Exception as e:
            print(f"Błąd usuwania oferty: {e}")
            return False
    
    def bulk_update_prices(self, updates: List[Dict]) -> bool:
        """
        Masowa aktualizacja cen produktów
        
        Args:
            updates: Lista słowników z kluczami 'id' i 'purchase_price_net'
        
        Returns:
            bool - True jeśli sukces
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            for update in updates:
                cursor.execute('''
                    UPDATE Products 
                    SET purchase_price_net = ?, price_update_date = ?
                    WHERE id = ?
                ''', (update['purchase_price_net'], now, update['id']))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Błąd aktualizacji cen: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def close(self):
        """Zamyka wszystkie połączenia z bazą danych"""
        # SQLite nie wymaga jawnego zamykania trwałego połączenia
        # Wszystkie połączenia są tworzone per-operacja w get_connection()
        pass
