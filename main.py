"""
Ofertomat 2.0 - Aplikacja do zarządzania ofertami handlowymi
Interfejs GUI w CustomTkinter
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
from typing import List, Dict, Optional
from datetime import datetime

# Importy modułów backendu
from database import Database
from importer import DataImporter
from pdf_generator import PDFGenerator


class App(ctk.CTk):
    """Główna klasa aplikacji Ofertomat 2.0"""
    
    def __init__(self):
        super().__init__()
        
        # Inicjalizacja backendu
        self.db = Database("ofertomat.db")
        self.importer = DataImporter()
        self.pdf_gen = PDFGenerator()
        
        # Konfiguracja okna głównego
        self.title("Ofertomat 2.0 - Zarządzanie Ofertami")
        self.geometry("1400x800")
        
        # Ustawienie motywu Dark Mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Zmienne stanu
        self.current_products = []
        self.selected_items = []
        self.search_var = ctk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        
        # Budowanie interfejsu
        self.setup_ui()
        
        # Ładowanie początkowych danych
        self.load_products()
    
    def setup_ui(self):
        """Buduje kompletny interfejs użytkownika"""
        
        # Konfiguracja layoutu głównego - 2 kolumny
        self.grid_columnconfigure(0, weight=0, minsize=250)  # Lewy panel (stała szerokość)
        self.grid_columnconfigure(1, weight=1)  # Prawy panel (elastyczny)
        self.grid_rowconfigure(0, weight=1)
        
        # === LEWY PANEL - Menu / Akcje ===
        self.create_left_panel()
        
        # === PRAWY PANEL - Widok Danych ===
        self.create_right_panel()
    
    def create_left_panel(self):
        """Tworzy lewy panel z przyciskami akcji"""
        
        # Ramka lewego panelu
        self.left_frame = ctk.CTkFrame(self, corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Logo / Tytuł aplikacji
        title_label = ctk.CTkLabel(
            self.left_frame,
            text="OFERTOMAT\n2.0",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("#C8102E", "#C8102E")  # Czerwony kolor z PDF
        )
        title_label.pack(pady=(30, 10))
        
        subtitle_label = ctk.CTkLabel(
            self.left_frame,
            text="System Zarządzania\nOfertami",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        subtitle_label.pack(pady=(0, 40))
        
        # Separator
        separator1 = ctk.CTkFrame(self.left_frame, height=2, fg_color="gray30")
        separator1.pack(fill="x", padx=20, pady=10)
        
        # === PRZYCISKI AKCJI ===
        
        # Przycisk: Załaduj Bazę (CSV)
        self.btn_load_csv = ctk.CTkButton(
            self.left_frame,
            text="📥 Załaduj Bazę (CSV)",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            corner_radius=8,
            fg_color=("#3B8ED0", "#1F6AA5"),
            hover_color=("#2E7AB8", "#144870"),
            command=self.load_csv_file
        )
        self.btn_load_csv.pack(pady=10, padx=20, fill="x")
        
        # Przycisk: Odśwież Dane
        self.btn_refresh = ctk.CTkButton(
            self.left_frame,
            text="🔄 Odśwież Dane",
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=8,
            fg_color="gray40",
            hover_color="gray50",
            command=self.load_products
        )
        self.btn_refresh.pack(pady=10, padx=20, fill="x")
        
        # Separator
        separator2 = ctk.CTkFrame(self.left_frame, height=2, fg_color="gray30")
        separator2.pack(fill="x", padx=20, pady=20)
        
        # Przycisk: Generuj Ofertę PDF
        self.btn_generate_pdf = ctk.CTkButton(
            self.left_frame,
            text="📄 Generuj Ofertę PDF",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            corner_radius=8,
            fg_color=("#C8102E", "#A00E26"),
            hover_color=("#B00D24", "#8A0B1E"),
            command=self.generate_offer_pdf
        )
        self.btn_generate_pdf.pack(pady=10, padx=20, fill="x")
        
        # Przycisk: Zarządzaj Kategoriami
        self.btn_categories = ctk.CTkButton(
            self.left_frame,
            text="📁 Kategorie",
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=8,
            fg_color="gray40",
            hover_color="gray50",
            command=self.open_categories_window
        )
        self.btn_categories.pack(pady=10, padx=20, fill="x")
        
        # Przycisk: Zapisane Oferty
        self.btn_saved_offers = ctk.CTkButton(
            self.left_frame,
            text="💾 Zapisane Oferty",
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=8,
            fg_color="gray40",
            hover_color="gray50",
            command=self.open_saved_offers_window
        )
        self.btn_saved_offers.pack(pady=10, padx=20, fill="x")
        
        # Przycisk: Wizytówka
        self.btn_business_card = ctk.CTkButton(
            self.left_frame,
            text="👤 Wizytówka",
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=8,
            fg_color="gray40",
            hover_color="gray50",
            command=self.open_business_card_window
        )
        self.btn_business_card.pack(pady=10, padx=20, fill="x")
        
        # Separator dolny
        separator3 = ctk.CTkFrame(self.left_frame, height=2, fg_color="gray30")
        separator3.pack(fill="x", padx=20, pady=(30, 10))
        
        # Informacje o ilości produktów
        self.info_label = ctk.CTkLabel(
            self.left_frame,
            text="Produkty: 0",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.info_label.pack(pady=5)
        
        # Spacer - wypełnia pozostałą przestrzeń
        spacer = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        spacer.pack(expand=True, fill="both")
        
        # Stopka z wersją
        version_label = ctk.CTkLabel(
            self.left_frame,
            text="v2.0.0",
            font=ctk.CTkFont(size=10),
            text_color="gray50"
        )
        version_label.pack(pady=(10, 20))
    
    def create_right_panel(self):
        """Tworzy prawy panel z tabelą danych"""
        
        # Ramka prawego panelu
        self.right_frame = ctk.CTkFrame(self, corner_radius=10)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Konfiguracja layoutu
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        # === GÓRNA SEKCJA: Pasek wyszukiwania i filtry ===
        search_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        search_frame.grid_columnconfigure(1, weight=1)
        
        # Label "Wyszukaj"
        search_label = ctk.CTkLabel(
            search_frame,
            text="🔍 Wyszukaj:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        search_label.grid(row=0, column=0, padx=(0, 10))
        
        # Pole tekstowe wyszukiwania
        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Wpisz nazwę lub kod produktu...",
            height=35,
            font=ctk.CTkFont(size=13)
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        # Przycisk wyczyść wyszukiwanie
        clear_btn = ctk.CTkButton(
            search_frame,
            text="✖",
            width=35,
            height=35,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="gray40",
            hover_color="gray50",
            command=self.clear_search
        )
        clear_btn.grid(row=0, column=2)
        
        # === ŚRODKOWA SEKCJA: Tabela danych ===
        table_frame = ctk.CTkFrame(self.right_frame)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Tworzenie scrollowalnej ramki dla tabeli
        self.table_scroll = ctk.CTkScrollableFrame(
            table_frame,
            fg_color="gray20"
        )
        self.table_scroll.grid(row=0, column=0, sticky="nsew")
        self.table_scroll.grid_columnconfigure(0, weight=1)
        
        # Nagłówek tabeli
        self.create_table_header()
        
        # Kontener na wiersze danych
        self.table_content_frame = ctk.CTkFrame(
            self.table_scroll,
            fg_color="transparent"
        )
        self.table_content_frame.grid(row=1, column=0, sticky="ew", padx=5)
        self.table_content_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
    
    def create_table_header(self):
        """Tworzy nagłówek tabeli produktów"""
        
        header_frame = ctk.CTkFrame(
            self.table_scroll,
            fg_color="#C8102E",
            corner_radius=5
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 10))
        header_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        
        headers = ["☑", "Kod", "Nazwa", "Jednostka", "Cena netto", "VAT %", "Kategoria"]
        widths = [50, 100, 300, 80, 100, 70, 150]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="white",
                width=width
            )
            label.grid(row=0, column=i, padx=5, pady=10, sticky="w")
    
    def load_products(self):
        """Ładuje produkty z bazy danych i wyświetla w tabeli"""
        
        try:
            # Pobierz produkty z bazy
            self.current_products = self.db.get_products()
            
            # Zaktualizuj licznik
            self.info_label.configure(text=f"Produkty: {len(self.current_products)}")
            
            # Wyświetl w tabeli
            self.display_products(self.current_products)
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można załadować produktów:\n{str(e)}")
    
    def display_products(self, products: List[Dict]):
        """Wyświetla produkty w tabeli"""
        
        # Wyczyść obecne wiersze
        for widget in self.table_content_frame.winfo_children():
            widget.destroy()
        
        self.selected_items = []
        
        # Stwórz wiersz dla każdego produktu
        for idx, product in enumerate(products):
            self.create_product_row(idx, product)
    
    def create_product_row(self, idx: int, product: Dict):
        """Tworzy pojedynczy wiersz produktu w tabeli"""
        
        # Ramka wiersza z naprzemiennym kolorem
        bg_color = "gray25" if idx % 2 == 0 else "gray20"
        row_frame = ctk.CTkFrame(
            self.table_content_frame,
            fg_color=bg_color,
            corner_radius=3
        )
        row_frame.grid(row=idx, column=0, sticky="ew", pady=2, padx=2)
        row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        
        # Checkbox do zaznaczania
        checkbox_var = ctk.BooleanVar()
        checkbox = ctk.CTkCheckBox(
            row_frame,
            text="",
            variable=checkbox_var,
            width=30,
            command=lambda: self.on_product_select(product, checkbox_var.get())
        )
        checkbox.grid(row=0, column=0, padx=10, pady=8)
        
        # Kolumny danych
        columns = [
            ("code", 100, product.get('code', 'N/A')),
            ("name", 300, product.get('name', 'N/A')),
            ("unit", 80, product.get('unit', 'szt.')),
            ("price", 100, f"{product.get('purchase_price_net', 0):.2f} zł"),
            ("vat", 70, f"{product.get('vat_rate', 23):.0f}%"),
            ("category", 150, product.get('category_name', 'Bez kategorii'))
        ]
        
        for col_idx, (key, width, value) in enumerate(columns, start=1):
            label = ctk.CTkLabel(
                row_frame,
                text=str(value),
                font=ctk.CTkFont(size=12),
                width=width,
                anchor="w"
            )
            label.grid(row=0, column=col_idx, padx=5, pady=8, sticky="w")
    
    def on_product_select(self, product: Dict, is_selected: bool):
        """Obsługuje zaznaczanie/odznaczanie produktu"""
        
        if is_selected:
            if product not in self.selected_items:
                self.selected_items.append(product)
        else:
            if product in self.selected_items:
                self.selected_items.remove(product)
    
    def on_search_change(self, *args):
        """Obsługuje zmianę tekstu w polu wyszukiwania"""
        
        search_text = self.search_var.get().lower().strip()
        
        if not search_text:
            # Pokaż wszystkie produkty
            self.display_products(self.current_products)
        else:
            # Filtruj produkty
            filtered = [
                p for p in self.current_products
                if search_text in str(p.get('name', '')).lower() or
                   search_text in str(p.get('code', '')).lower()
            ]
            self.display_products(filtered)
    
    def clear_search(self):
        """Czyści pole wyszukiwania"""
        self.search_var.set("")
    
    # === FUNKCJE AKCJI (PRZYCISKI) ===
    
    def load_csv_file(self):
        """Otwiera okno wyboru pliku CSV i importuje dane"""
        
        # Otwórz dialog wyboru pliku
        file_path = filedialog.askopenfilename(
            title="Wybierz plik CSV lub Excel",
            filetypes=[
                ("Pliki CSV", "*.csv"),
                ("Pliki Excel", "*.xlsx *.xls"),
                ("Wszystkie pliki", "*.*")
            ]
        )
        
        if not file_path:
            return  # Użytkownik anulował
        
        try:
            # Okno dialogowe z opcjami importu
            import_dialog = ctk.CTkToplevel(self)
            import_dialog.title("Import danych")
            import_dialog.geometry("400x250")
            import_dialog.transient(self)
            import_dialog.grab_set()
            
            # Centrowanie okna
            import_dialog.update_idletasks()
            x = (import_dialog.winfo_screenwidth() // 2) - (400 // 2)
            y = (import_dialog.winfo_screenheight() // 2) - (250 // 2)
            import_dialog.geometry(f"400x250+{x}+{y}")
            
            # Zawartość
            ctk.CTkLabel(
                import_dialog,
                text="Wybierz kategorię dla importowanych produktów:",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(pady=20)
            
            # Lista kategorii
            categories = self.db.get_categories()
            category_names = [cat['name'] for cat in categories]
            
            category_var = ctk.StringVar(value=category_names[0] if category_names else "Bez kategorii")
            
            category_menu = ctk.CTkOptionMenu(
                import_dialog,
                variable=category_var,
                values=category_names,
                width=300,
                height=35,
                font=ctk.CTkFont(size=13)
            )
            category_menu.pack(pady=10)
            
            # Przycisk importu
            def do_import():
                selected_category = category_var.get()
                category_id = next(
                    (cat['id'] for cat in categories if cat['name'] == selected_category),
                    None
                )
                
                try:
                    # Import danych
                    products = self.importer.import_from_file(file_path, category_id)
                    
                    if not products:
                        messagebox.showwarning("Uwaga", "Nie znaleziono produktów do importu.")
                        import_dialog.destroy()
                        return
                    
                    # Zapisz do bazy
                    added, updated = self.db.import_products_batch(products)
                    
                    # Komunikat sukcesu
                    messagebox.showinfo(
                        "Sukces",
                        f"Import zakończony!\n\n"
                        f"Dodano: {added} produktów\n"
                        f"Zaktualizowano: {updated} produktów"
                    )
                    
                    # Odśwież tabelę
                    self.load_products()
                    
                    import_dialog.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Błąd importu", f"Wystąpił błąd:\n{str(e)}")
                    import_dialog.destroy()
            
            btn_import = ctk.CTkButton(
                import_dialog,
                text="Importuj",
                font=ctk.CTkFont(size=14, weight="bold"),
                height=40,
                fg_color="#3B8ED0",
                hover_color="#2E7AB8",
                command=do_import
            )
            btn_import.pack(pady=20)
            
            btn_cancel = ctk.CTkButton(
                import_dialog,
                text="Anuluj",
                font=ctk.CTkFont(size=13),
                height=35,
                fg_color="gray40",
                hover_color="gray50",
                command=import_dialog.destroy
            )
            btn_cancel.pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można otworzyć pliku:\n{str(e)}")
    
    def generate_offer_pdf(self):
        """Generuje ofertę PDF z zaznaczonych produktów"""
        
        if not self.selected_items:
            messagebox.showwarning(
                "Brak zaznaczenia",
                "Zaznacz co najmniej jeden produkt, aby wygenerować ofertę."
            )
            return
        
        # Okno dialogowe ustawień oferty
        pdf_dialog = ctk.CTkToplevel(self)
        pdf_dialog.title("Generowanie Oferty PDF")
        pdf_dialog.geometry("500x400")
        pdf_dialog.transient(self)
        pdf_dialog.grab_set()
        
        # Centrowanie
        pdf_dialog.update_idletasks()
        x = (pdf_dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (pdf_dialog.winfo_screenheight() // 2) - (400 // 2)
        pdf_dialog.geometry(f"500x400+{x}+{y}")
        
        # Tytuł
        ctk.CTkLabel(
            pdf_dialog,
            text="Ustawienia Oferty",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        # Nazwa oferty
        ctk.CTkLabel(pdf_dialog, text="Tytuł oferty:", font=ctk.CTkFont(size=13)).pack(pady=(10, 5))
        title_entry = ctk.CTkEntry(
            pdf_dialog,
            width=400,
            height=35,
            font=ctk.CTkFont(size=13),
            placeholder_text="Np. Oferta handlowa"
        )
        title_entry.insert(0, "Oferta handlowa")
        title_entry.pack(pady=5)
        
        # Wizytówka
        business_card = self.db.get_business_card()
        
        # Nazwa pliku
        ctk.CTkLabel(pdf_dialog, text="Nazwa pliku:", font=ctk.CTkFont(size=13)).pack(pady=(15, 5))
        filename_entry = ctk.CTkEntry(
            pdf_dialog,
            width=400,
            height=35,
            font=ctk.CTkFont(size=13),
            placeholder_text="oferta"
        )
        filename_entry.insert(0, f"oferta_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        filename_entry.pack(pady=5)
        
        # Przycisk generuj
        def do_generate():
            title = title_entry.get().strip() or "Oferta handlowa"
            filename = filename_entry.get().strip() or "oferta"
            
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            # Wybór lokalizacji zapisu
            save_path = filedialog.asksaveasfilename(
                title="Zapisz ofertę jako",
                defaultextension=".pdf",
                initialfile=filename,
                filetypes=[("Plik PDF", "*.pdf")]
            )
            
            if not save_path:
                return
            
            try:
                # Przygotuj dane oferty
                offer_data = {
                    'title': title,
                    'date': datetime.now().strftime('%d.%m.%Y'),
                    'items': self.selected_items,
                    'business_card': business_card
                }
                
                # Generuj PDF
                success = self.pdf_gen.generate_offer_pdf(offer_data, save_path)
                
                if success:
                    messagebox.showinfo(
                        "Sukces",
                        f"Oferta PDF została wygenerowana!\n\nZapisano jako:\n{save_path}"
                    )
                    pdf_dialog.destroy()
                else:
                    messagebox.showerror("Błąd", "Nie udało się wygenerować PDF.")
                
            except Exception as e:
                messagebox.showerror("Błąd", f"Wystąpił błąd:\n{str(e)}")
        
        btn_generate = ctk.CTkButton(
            pdf_dialog,
            text="Generuj PDF",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            width=200,
            fg_color="#C8102E",
            hover_color="#B00D24",
            command=do_generate
        )
        btn_generate.pack(pady=30)
        
        btn_cancel = ctk.CTkButton(
            pdf_dialog,
            text="Anuluj",
            font=ctk.CTkFont(size=13),
            height=35,
            width=150,
            fg_color="gray40",
            hover_color="gray50",
            command=pdf_dialog.destroy
        )
        btn_cancel.pack(pady=5)
    
    def open_categories_window(self):
        """Otwiera okno zarządzania kategoriami"""
        messagebox.showinfo(
            "W przygotowaniu",
            "Funkcja zarządzania kategoriami będzie dostępna w następnej wersji."
        )
    
    def open_saved_offers_window(self):
        """Otwiera okno z zapisanymi ofertami"""
        messagebox.showinfo(
            "W przygotowaniu",
            "Funkcja przeglądania zapisanych ofert będzie dostępna w następnej wersji."
        )
    
    def open_business_card_window(self):
        """Otwiera okno edycji wizytówki użytkownika"""
        
        # Okno dialogowe
        card_dialog = ctk.CTkToplevel(self)
        card_dialog.title("Edycja Wizytówki")
        card_dialog.geometry("500x550")
        card_dialog.transient(self)
        card_dialog.grab_set()
        
        # Centrowanie
        card_dialog.update_idletasks()
        x = (card_dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (card_dialog.winfo_screenheight() // 2) - (550 // 2)
        card_dialog.geometry(f"500x550+{x}+{y}")
        
        # Tytuł
        title_label = ctk.CTkLabel(
            card_dialog,
            text="Twoja Wizytówka",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Pobierz obecne dane wizytówki
        current_card = self.db.get_business_card() or {}
        
        # Ramka formularza
        form_frame = ctk.CTkFrame(card_dialog, fg_color="transparent")
        form_frame.pack(pady=5, padx=30, fill="both")
        
        # Pole: Firma
        ctk.CTkLabel(
            form_frame,
            text="Nazwa firmy:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(pady=(5, 3), fill="x")
        
        company_entry = ctk.CTkEntry(
            form_frame,
            height=35,
            font=ctk.CTkFont(size=13),
            placeholder_text="Np. FIRMA SP. Z O.O."
        )
        company_entry.insert(0, current_card.get('company', ''))
        company_entry.pack(fill="x")
        
        # Pole: Imię i nazwisko
        ctk.CTkLabel(
            form_frame,
            text="Imię i nazwisko:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(pady=(10, 3), fill="x")
        
        fullname_entry = ctk.CTkEntry(
            form_frame,
            height=35,
            font=ctk.CTkFont(size=13),
            placeholder_text="Np. Jan Kowalski"
        )
        fullname_entry.insert(0, current_card.get('full_name', ''))
        fullname_entry.pack(fill="x")
        
        # Pole: Telefon
        ctk.CTkLabel(
            form_frame,
            text="Telefon:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(pady=(10, 3), fill="x")
        
        phone_entry = ctk.CTkEntry(
            form_frame,
            height=35,
            font=ctk.CTkFont(size=13),
            placeholder_text="Np. +48 123 456 789"
        )
        phone_entry.insert(0, current_card.get('phone', ''))
        phone_entry.pack(fill="x")
        
        # Pole: E-mail
        ctk.CTkLabel(
            form_frame,
            text="E-mail:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(pady=(10, 3), fill="x")
        
        email_entry = ctk.CTkEntry(
            form_frame,
            height=35,
            font=ctk.CTkFont(size=13),
            placeholder_text="Np. kontakt@firma.pl"
        )
        email_entry.insert(0, current_card.get('email', ''))
        email_entry.pack(fill="x")
        
        # Funkcja zapisywania
        def save_card():
            company = company_entry.get().strip()
            full_name = fullname_entry.get().strip()
            phone = phone_entry.get().strip()
            email = email_entry.get().strip()
            
            # Walidacja podstawowa
            if not company and not full_name:
                messagebox.showwarning(
                    "Brak danych",
                    "Wypełnij przynajmniej nazwę firmy lub imię i nazwisko."
                )
                return
            
            # Zapisz do bazy
            success = self.db.save_business_card(company, full_name, phone, email)
            
            if success:
                messagebox.showinfo(
                    "Sukces",
                    "Wizytówka została zapisana!"
                )
                card_dialog.destroy()
            else:
                messagebox.showerror(
                    "Błąd",
                    "Nie udało się zapisać wizytówki."
                )
        
        # Przyciski akcji
        buttons_frame = ctk.CTkFrame(card_dialog, fg_color="transparent")
        buttons_frame.pack(pady=15)
        
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Zapisz",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            width=180,
            fg_color="#3B8ED0",
            hover_color="#2E7AB8",
            command=save_card
        )
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Anuluj",
            font=ctk.CTkFont(size=14),
            height=45,
            width=180,
            fg_color="gray40",
            hover_color="gray50",
            command=card_dialog.destroy
        )
        cancel_btn.pack(side="left", padx=10)


def main():
    """Główna funkcja uruchamiająca aplikację"""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
