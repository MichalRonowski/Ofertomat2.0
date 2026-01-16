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
        self.filtered_products = []  # Produkty po filtrowaniu
        self.selected_items = []
        self.search_var = ctk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        
        # Paginacja
        self.current_page = 0
        self.items_per_page = 100
        self.total_pages = 0
        
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
        
        # Separator
        separator2 = ctk.CTkFrame(self.left_frame, height=2, fg_color="gray30")
        separator2.pack(fill="x", padx=20, pady=20)
        
        # Przycisk: Generator Ofert
        self.btn_generate_pdf = ctk.CTkButton(
            self.left_frame,
            text="📄 Generator Ofert",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            corner_radius=8,
            fg_color=("#C8102E", "#A00E26"),
            hover_color=("#B00D24", "#8A0B1E"),
            command=self.open_offer_creator
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
        
        # Przycisk: Dodaj Produkt
        self.btn_add_product = ctk.CTkButton(
            self.left_frame,
            text="➕ Dodaj Produkt",
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=8,
            fg_color="#28A745",
            hover_color="#218838",
            command=self.add_product
        )
        self.btn_add_product.pack(pady=10, padx=20, fill="x")
        
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
            placeholder_text="Wpisz nazwę produktu...",
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
        
        # Przycisk zmiany kategorii dla zaznaczonych
        change_cat_btn = ctk.CTkButton(
            search_frame,
            text="🔄 Zmień kategorię zaznaczonym",
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color="#6C757D",
            hover_color="#5A6268",
            command=self.change_category_for_selected_products
        )
        change_cat_btn.grid(row=0, column=3, padx=(10, 0))
        
        # Kontrolki paginacji
        pagination_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        pagination_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        pagination_frame.grid_columnconfigure(1, weight=1)
        
        self.page_info_label = ctk.CTkLabel(
            pagination_frame,
            text="Strona 1 z 1",
            font=ctk.CTkFont(size=12)
        )
        self.page_info_label.grid(row=0, column=1, padx=10)
        
        self.prev_btn = ctk.CTkButton(
            pagination_frame,
            text="← Poprzednia",
            width=120,
            height=30,
            command=self.previous_page,
            state="disabled"
        )
        self.prev_btn.grid(row=0, column=0, padx=5)
        
        self.next_btn = ctk.CTkButton(
            pagination_frame,
            text="Następna →",
            width=120,
            height=30,
            command=self.next_page,
            state="disabled"
        )
        self.next_btn.grid(row=0, column=2, padx=5)
        
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
        self.table_content_frame.grid(row=1, column=0, sticky="ew", padx=0)
        
        # Ustawienie stałych szerokości kolumn (takich samych jak w nagłówku)
        self.table_content_frame.grid_columnconfigure(0, minsize=60, weight=0)   # Checkbox
        self.table_content_frame.grid_columnconfigure(1, minsize=350, weight=0)  # Nazwa
        self.table_content_frame.grid_columnconfigure(2, minsize=100, weight=0)  # Jednostka
        self.table_content_frame.grid_columnconfigure(3, minsize=120, weight=0)  # Cena netto
        self.table_content_frame.grid_columnconfigure(4, minsize=80, weight=0)   # VAT
        self.table_content_frame.grid_columnconfigure(5, minsize=180, weight=0)  # Kategoria
    
    def create_table_header(self):
        """Tworzy nagłówek tabeli produktów"""
        
        header_frame = ctk.CTkFrame(
            self.table_scroll,
            fg_color="#C8102E",
            corner_radius=5
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(5, 10))
        
        # Ustawienie stałych szerokości kolumn
        header_frame.grid_columnconfigure(0, minsize=60, weight=0)   # Checkbox
        header_frame.grid_columnconfigure(1, minsize=300, weight=0)  # Nazwa
        header_frame.grid_columnconfigure(2, minsize=100, weight=0)  # Jednostka
        header_frame.grid_columnconfigure(3, minsize=120, weight=0)  # Cena netto
        header_frame.grid_columnconfigure(4, minsize=80, weight=0)   # VAT
        header_frame.grid_columnconfigure(5, minsize=150, weight=0)  # Kategoria
        header_frame.grid_columnconfigure(6, minsize=120, weight=0)  # Akcje
        
        headers = ["☑", "Nazwa", "Jednostka", "Cena netto", "VAT %", "Kategoria", "Akcje"]
        
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="white"
            )
            if i == 0:
                # Checkbox - wyśrodkowany
                label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
            else:
                label.grid(row=0, column=i, padx=5, pady=10, sticky="w")
    
    def load_products(self):
        """Ładuje produkty z bazy danych i wyświetla w tabeli"""
        
        try:
            # Pobierz produkty z bazy
            self.current_products = self.db.get_products()
            self.filtered_products = self.current_products
            
            # Zaktualizuj licznik
            self.info_label.configure(text=f"Produkty: {len(self.current_products)}")
            
            # Reset paginacji i wyświetl pierwszą stronę
            self.current_page = 0
            self.update_pagination()
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można załadować produktów:\n{str(e)}")
    
    def update_pagination(self):
        """Aktualizuje wyświetlanie z paginacją"""
        # Oblicz liczbę stron
        self.total_pages = max(1, (len(self.filtered_products) + self.items_per_page - 1) // self.items_per_page)
        
        # Upewnij się że current_page jest w zakresie
        if self.current_page >= self.total_pages:
            self.current_page = self.total_pages - 1
        if self.current_page < 0:
            self.current_page = 0
        
        # Aktualizuj label
        self.page_info_label.configure(
            text=f"Strona {self.current_page + 1} z {self.total_pages} (wyświetlane: {min(self.items_per_page, len(self.filtered_products) - self.current_page * self.items_per_page)} z {len(self.filtered_products)})"
        )
        
        # Aktualizuj stan przycisków
        self.prev_btn.configure(state="normal" if self.current_page > 0 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < self.total_pages - 1 else "disabled")
        
        # Wyświetl produkty dla bieżącej strony
        start_idx = self.current_page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_products = self.filtered_products[start_idx:end_idx]
        
        self.display_products(page_products, start_idx)
    
    def previous_page(self):
        """Przechodzi do poprzedniej strony"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_pagination()
    
    def next_page(self):
        """Przechodzi do następnej strony"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_pagination()
    
    def display_products(self, products: List[Dict], start_idx: int = 0):
        """Wyświetla produkty w tabeli"""
        
        # Wyczyść obecne wiersze
        for widget in self.table_content_frame.winfo_children():
            widget.destroy()
        
        self.selected_items = []
        
        # Stwórz wiersz dla każdego produktu
        for idx, product in enumerate(products, start=start_idx):
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
        row_frame.grid(row=idx, column=0, sticky="ew", pady=2, padx=0)
        
        # Ustawienie stałych szerokości kolumn (takich samych jak w nagłówku)
        row_frame.grid_columnconfigure(0, minsize=60, weight=0)   # Checkbox
        row_frame.grid_columnconfigure(1, minsize=300, weight=1)  # Nazwa
        row_frame.grid_columnconfigure(2, minsize=100, weight=0)  # Jednostka
        row_frame.grid_columnconfigure(3, minsize=120, weight=0)  # Cena netto
        row_frame.grid_columnconfigure(4, minsize=80, weight=0)   # VAT
        row_frame.grid_columnconfigure(5, minsize=150, weight=0)  # Kategoria
        row_frame.grid_columnconfigure(6, minsize=120, weight=0)  # Akcje
        
        # Checkbox do zaznaczania
        checkbox_var = ctk.BooleanVar()
        checkbox = ctk.CTkCheckBox(
            row_frame,
            text="",
            variable=checkbox_var,
            width=30,
            command=lambda: self.on_product_select(product, checkbox_var.get())
        )
        checkbox.grid(row=0, column=0, padx=10, pady=8, sticky="w")
        
        # Kolumny danych
        columns = [
            ("name", product.get('name', 'N/A')),
            ("unit", product.get('unit', 'szt.')),
            ("price", f"{product.get('purchase_price_net', 0):.2f} zł"),
            ("vat", f"{product.get('vat_rate', 23):.0f}%"),
            ("category", product.get('category_name', 'Bez kategorii'))
        ]
        
        for col_idx, (key, value) in enumerate(columns, start=1):
            label = ctk.CTkLabel(
                row_frame,
                text=str(value),
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            label.grid(row=0, column=col_idx, padx=5, pady=8, sticky="ew")
        
        # Przyciski akcji
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=6, padx=5, pady=5, sticky="ew")
        
        # Przycisk edytuj
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️",
            width=40,
            height=28,
            fg_color="#3B8ED0",
            hover_color="#2E7AB8",
            command=lambda p=product: self.edit_product(p)
        )
        edit_btn.pack(side="left", padx=2)
        
        # Przycisk usuń
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            width=40,
            height=28,
            fg_color="#C8102E",
            hover_color="#B00D24",
            command=lambda p=product: self.delete_product(p)
        )
        delete_btn.pack(side="left", padx=2)
    
    def on_product_select(self, product: Dict, is_selected: bool):
        """Obsługuje zaznaczanie/odznaczanie produktu"""
        
        if is_selected:
            if product not in self.selected_items:
                self.selected_items.append(product)
        else:
            if product in self.selected_items:
                self.selected_items.remove(product)
    
    def change_category_for_selected_products(self):
        """Zmienia kategorię dla zaznaczonych produktów"""
        if not self.selected_items:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz produkty, którym chcesz zmienić kategorię!")
            return
        
        # Dialog wyboru kategorii
        cat_dialog = ctk.CTkToplevel(self)
        cat_dialog.title("Zmiana kategorii")
        cat_dialog.geometry("450x300")
        cat_dialog.transient(self)
        cat_dialog.grab_set()
        
        # Centrowanie
        cat_dialog.update_idletasks()
        x = (cat_dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (cat_dialog.winfo_screenheight() // 2) - (300 // 2)
        cat_dialog.geometry(f"450x300+{x}+{y}")
        
        ctk.CTkLabel(
            cat_dialog,
            text=f"Zmień kategorię dla {len(self.selected_items)} produktów",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=20)
        
        # Lista zaznaczonych produktów
        products_label = ctk.CTkLabel(
            cat_dialog,
            text="Zaznaczone: " + ", ".join([p['name'][:30] + "..." if len(p['name']) > 30 else p['name'] for p in self.selected_items[:3]]) + 
                 (f" i {len(self.selected_items) - 3} więcej" if len(self.selected_items) > 3 else ""),
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=400
        )
        products_label.pack(pady=(0, 15))
        
        ctk.CTkLabel(
            cat_dialog,
            text="Wybierz nową kategorię:",
            font=ctk.CTkFont(size=13)
        ).pack(pady=(10, 5))
        
        categories = self.db.get_categories()
        category_names = [cat['name'] for cat in categories]
        if not category_names:
            category_names = ["Bez kategorii"]
        
        category_menu = ctk.CTkOptionMenu(
            cat_dialog,
            values=category_names,
            height=35,
            width=350,
            font=ctk.CTkFont(size=12)
        )
        if category_names:
            category_menu.set(category_names[0])
        category_menu.pack(pady=10)
        
        def apply_category_change():
            new_category = category_menu.get()
            
            # Znajdź ID kategorii
            category_id = None
            for cat in categories:
                if cat['name'] == new_category:
                    category_id = cat['id']
                    break
            
            # Zmień kategorię dla zaznaczonych produktów w bazie
            success_count = 0
            for product in self.selected_items:
                # Aktualizuj w bazie danych
                success = self.db.update_product(
                    product['id'],
                    None,  # kod
                    product['name'],
                    product['unit'],
                    product['purchase_price_net'],
                    product['vat_rate'],
                    category_id
                )
                if success:
                    success_count += 1
            
            cat_dialog.destroy()
            
            if success_count == len(self.selected_items):
                messagebox.showinfo("Sukces", f"Zmieniono kategorię dla {success_count} produktów!")
            else:
                messagebox.showwarning("Częściowy sukces", f"Zmieniono kategorię dla {success_count} z {len(self.selected_items)} produktów")
            
            # Odśwież listę produktów
            self.selected_items.clear()
            self.load_products()
        
        btn_frame = ctk.CTkFrame(cat_dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="Zastosuj",
            width=140,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3B8ED0",
            hover_color="#2E7AB8",
            command=apply_category_change
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Anuluj",
            width=140,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="gray40",
            hover_color="gray50",
            command=cat_dialog.destroy
        ).pack(side="left", padx=5)
    
    def add_product(self):
        """Otwiera okno dodawania nowego produktu"""
        
        add_window = ctk.CTkToplevel(self)
        add_window.title("Dodaj Nowy Produkt")
        add_window.geometry("550x650")
        add_window.transient(self)
        add_window.grab_set()
        
        # Centrowanie
        add_window.update_idletasks()
        x = (add_window.winfo_screenwidth() // 2) - (550 // 2)
        y = (add_window.winfo_screenheight() // 2) - (650 // 2)
        add_window.geometry(f"550x650+{x}+{y}")
        
        # Tytuł
        ctk.CTkLabel(
            add_window,
            text="Dodaj Nowy Produkt",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        # Formularz
        form_frame = ctk.CTkFrame(add_window, fg_color="transparent")
        form_frame.pack(pady=10, padx=30, fill="both", expand=True)
        
        # Nazwa
        ctk.CTkLabel(form_frame, text="Nazwa produktu:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        name_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=12), placeholder_text="Np. Laptop Dell Latitude")
        name_entry.pack(fill="x", pady=(0, 15))
        
        # Jednostka
        ctk.CTkLabel(form_frame, text="Jednostka:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        unit_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=12), placeholder_text="szt.")
        unit_entry.insert(0, "szt.")
        unit_entry.pack(fill="x", pady=(0, 15))
        
        # Cena zakupu netto
        ctk.CTkLabel(form_frame, text="Cena zakupu netto (zł):", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        price_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=12), placeholder_text="0.00")
        price_entry.pack(fill="x", pady=(0, 15))
        
        # VAT
        ctk.CTkLabel(form_frame, text="VAT (%):", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        vat_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=12), placeholder_text="23")
        vat_entry.insert(0, "23")
        vat_entry.pack(fill="x", pady=(0, 15))
        
        # Kategoria
        ctk.CTkLabel(form_frame, text="Kategoria:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        categories = self.db.get_categories()
        category_names = [cat['name'] for cat in categories]
        if not category_names:
            category_names = ["Bez kategorii"]
        
        category_menu = ctk.CTkOptionMenu(
            form_frame,
            values=category_names,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        if category_names:
            category_menu.set(category_names[0])
        category_menu.pack(fill="x", pady=(0, 15))
        
        def save_product():
            try:
                # Walidacja
                name = name_entry.get().strip()
                if not name:
                    messagebox.showwarning("Błąd", "Nazwa produktu nie może być pusta!")
                    return
                
                unit = unit_entry.get().strip() or 'szt.'
                
                price_str = price_entry.get().strip()
                if not price_str:
                    messagebox.showwarning("Błąd", "Cena nie może być pusta!")
                    return
                # Zamień przecinek na kropkę
                price_str = price_str.replace(',', '.')
                price = float(price_str)
                
                vat_str = vat_entry.get().strip()
                if not vat_str:
                    messagebox.showwarning("Błąd", "VAT nie może być pusty!")
                    return
                # Zamień przecinek na kropkę
                vat_str = vat_str.replace(',', '.')
                vat = float(vat_str)
                
                # Znajdź ID kategorii
                selected_category = category_menu.get()
                category_id = None
                for cat in categories:
                    if cat['name'] == selected_category:
                        category_id = cat['id']
                        break
                
                # Dodaj produkt do bazy
                product_id = self.db.add_product(
                    code=None,
                    name=name,
                    unit=unit,
                    purchase_price_net=price,
                    vat_rate=vat,
                    category_id=category_id
                )
                
                if product_id:
                    messagebox.showinfo("Sukces", "Produkt został dodany!")
                    add_window.destroy()
                    self.load_products()  # Odśwież listę
                else:
                    messagebox.showerror("Błąd", "Nie udało się dodać produktu!")
                    
            except ValueError:
                messagebox.showerror("Błąd", "Nieprawidłowe wartości liczbowe!")
            except Exception as e:
                messagebox.showerror("Błąd", f"Wystąpił błąd:\n{str(e)}")
        
        # Przyciski
        btn_frame = ctk.CTkFrame(add_window, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="Dodaj produkt",
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#28A745",
            hover_color="#218838",
            command=save_product
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Anuluj",
            width=150,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="gray40",
            hover_color="gray50",
            command=add_window.destroy
        ).pack(side="left", padx=10)
    
    def edit_product(self, product: Dict):
        """Otwiera okno edycji produktu"""
        
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Edycja Produktu")
        edit_window.geometry("550x650")
        edit_window.transient(self)
        edit_window.grab_set()
        
        # Centrowanie
        edit_window.update_idletasks()
        x = (edit_window.winfo_screenwidth() // 2) - (550 // 2)
        y = (edit_window.winfo_screenheight() // 2) - (650 // 2)
        edit_window.geometry(f"550x650+{x}+{y}")
        
        # Tytuł
        ctk.CTkLabel(
            edit_window,
            text="Edycja Produktu",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        # Formularz
        form_frame = ctk.CTkFrame(edit_window, fg_color="transparent")
        form_frame.pack(pady=10, padx=30, fill="both", expand=True)
        
        # Nazwa
        ctk.CTkLabel(form_frame, text="Nazwa produktu:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        name_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=12))
        name_entry.insert(0, product.get('name', ''))
        name_entry.pack(fill="x", pady=(0, 15))
        
        # Jednostka
        ctk.CTkLabel(form_frame, text="Jednostka:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        unit_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=12))
        unit_entry.insert(0, product.get('unit', 'szt.'))
        unit_entry.pack(fill="x", pady=(0, 15))
        
        # Cena zakupu netto
        ctk.CTkLabel(form_frame, text="Cena zakupu netto (zł):", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        price_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=12))
        price_entry.insert(0, str(product.get('purchase_price_net', 0)))
        price_entry.pack(fill="x", pady=(0, 15))
        
        # VAT
        ctk.CTkLabel(form_frame, text="VAT (%):", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        vat_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=12))
        vat_entry.insert(0, str(product.get('vat_rate', 23)))
        vat_entry.pack(fill="x", pady=(0, 15))
        
        # Kategoria
        ctk.CTkLabel(form_frame, text="Kategoria:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        categories = self.db.get_categories()
        category_names = [cat['name'] for cat in categories]
        if not category_names:
            category_names = ["Brak kategorii"]
        
        current_category = product.get('category_name', 'Brak kategorii')
        if current_category not in category_names:
            category_names.insert(0, current_category)
        
        category_menu = ctk.CTkOptionMenu(
            form_frame,
            values=category_names,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        category_menu.set(current_category)
        category_menu.pack(fill="x", pady=(0, 15))
        
        def save_changes():
            try:
                # Walidacja
                name = name_entry.get().strip()
                if not name:
                    messagebox.showwarning("Błąd", "Nazwa produktu nie może być pusta!")
                    return
                
                unit = unit_entry.get().strip() or 'szt.'
                # Zamień przecinek na kropkę
                price = float(price_entry.get().strip().replace(',', '.'))
                vat = float(vat_entry.get().strip().replace(',', '.'))
                
                # Znajdź ID kategorii
                selected_category = category_menu.get()
                category_id = None
                for cat in categories:
                    if cat['name'] == selected_category:
                        category_id = cat['id']
                        break
                
                # Zaktualizuj produkt w bazie
                success = self.db.update_product(
                    product['id'],
                    None,  # kod już nie jest używany
                    name,
                    unit,
                    price,
                    vat,
                    category_id
                )
                
                if success:
                    messagebox.showinfo("Sukces", "Produkt został zaktualizowany!")
                    edit_window.destroy()
                    self.load_products()  # Odśwież listę
                else:
                    messagebox.showerror("Błąd", "Nie udało się zaktualizować produktu!")
                    
            except ValueError:
                messagebox.showerror("Błąd", "Nieprawidłowe wartości liczbowe!")
            except Exception as e:
                messagebox.showerror("Błąd", f"Wystąpił błąd:\n{str(e)}")
        
        # Przyciski
        btn_frame = ctk.CTkFrame(edit_window, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="Zapisz zmiany",
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3B8ED0",
            hover_color="#2E7AB8",
            command=save_changes
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Anuluj",
            width=150,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="gray40",
            hover_color="gray50",
            command=edit_window.destroy
        ).pack(side="left", padx=10)
    
    def delete_product(self, product: Dict):
        """Usuwa produkt z bazy danych"""
        
        result = messagebox.askyesno(
            "Potwierdzenie",
            f"Czy na pewno chcesz usunąć produkt:\n\n{product.get('name', 'N/A')}?\n\nTa operacja jest nieodwracalna!"
        )
        
        if result:
            try:
                success = self.db.delete_product(product['id'])
                if success:
                    messagebox.showinfo("Sukces", "Produkt został usunięty!")
                    self.load_products()  # Odśwież listę
                else:
                    messagebox.showerror("Błąd", "Nie udało się usunąć produktu!")
            except Exception as e:
                messagebox.showerror("Błąd", f"Wystąpił błąd:\n{str(e)}")
    
    def on_search_change(self, *args):
        """Obsługuje zmianę tekstu w polu wyszukiwania"""
        
        search_text = self.search_var.get().lower().strip()
        
        if not search_text:
            # Pokaż wszystkie produkty
            self.filtered_products = self.current_products
        else:
            # Filtruj produkty
            self.filtered_products = [
                p for p in self.current_products
                if search_text in str(p.get('name', '')).lower() or 
                   search_text in str(p.get('category_name', '')).lower()
            ]
        
        # Reset do pierwszej strony i aktualizuj
        self.current_page = 0
        self.update_pagination()
    
    def clear_search(self):
        """Czyści pole wyszukiwania"""
        self.search_var.set("")
    
    # === FUNKCJE AKCJI (PRZYCISKI) ===
    
    def open_offer_creator(self, existing_offer_id=None):
        """Otwiera kreator ofert - główne okno do tworzenia/edycji ofert"""
        
        # Duże okno kreatora
        creator = ctk.CTkToplevel(self)
        creator.title("Generator Ofert" if not existing_offer_id else "Edycja Oferty")
        creator.geometry("1400x800")
        creator.transient(self)
        creator.grab_set()
        
        # Centrowanie
        creator.update_idletasks()
        x = (creator.winfo_screenwidth() // 2) - (1400 // 2)
        y = (creator.winfo_screenheight() // 2) - (800 // 2)
        creator.geometry(f"1400x800+{x}+{y}")
        
        # Zmienne stanu
        offer_title_var = ctk.StringVar(value="Oferta handlowa")
        selected_offer_items = []  # Lista wybranych produktów do oferty
        category_order_list = []  # Kolejność kategorii
        
        # === GÓRNY PANEL: Tytuł i przyciski akcji ===
        top_frame = ctk.CTkFrame(creator, fg_color="gray20", height=80)
        top_frame.pack(fill="x", padx=10, pady=10)
        top_frame.pack_propagate(False)
        
        # Lewy panel górny - tytuł oferty
        title_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            title_frame,
            text="Tytuł oferty:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=(0, 10))
        
        title_entry = ctk.CTkEntry(
            title_frame,
            textvariable=offer_title_var,
            height=40,
            font=ctk.CTkFont(size=14),
            placeholder_text="Wprowadź tytuł oferty..."
        )
        title_entry.pack(side="left", fill="x", expand=True)
        
        # Prawy panel górny - przyciski akcji
        actions_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        actions_frame.pack(side="right", padx=10, pady=10)
        
        def save_as_template():
            """Zapisuje ofertę jako szablon bez generowania PDF"""
            title = offer_title_var.get().strip() or "Oferta handlowa"
            
            if not selected_offer_items:
                messagebox.showwarning("Uwaga", "Dodaj produkty do oferty!")
                return
            
            # Przygotuj dane
            items_to_save = []
            cat_order = {cat: idx for idx, cat in enumerate(category_order_list)}
            
            for item in selected_offer_items:
                items_to_save.append({
                    'product_id': item.get('id'),
                    'name': item['name'],
                    'category_name': item.get('category_name', 'Bez kategorii'),
                    'unit': item.get('unit', 'szt.'),
                    'purchase_price_net': item.get('purchase_price_net', 0),
                    'vat_rate': item.get('vat_rate', 23),
                    'margin': item.get('margin', item.get('default_margin', 30.0)),
                    'quantity': 1.0
                })
            
            # Zapisz
            if existing_offer_id:
                success = self.db.update_offer(existing_offer_id, title, items_to_save, cat_order)
                msg = "Szablon został zaktualizowany!"
            else:
                offer_id = self.db.save_offer(title, items_to_save, cat_order)
                success = offer_id > 0
                msg = "Szablon został zapisany!"
            
            if success:
                messagebox.showinfo("Sukces", msg)
            else:
                messagebox.showerror("Błąd", "Nie udało się zapisać szablonu.")
        
        def generate_pdf_from_creator():
            """Generuje PDF z kreatora"""
            title = offer_title_var.get().strip() or "Oferta handlowa"
            
            if not selected_offer_items:
                messagebox.showwarning("Uwaga", "Dodaj produkty do oferty!")
                return
            
            # Wybór lokalizacji zapisu
            filename = f"{title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            save_path = filedialog.asksaveasfilename(
                title="Zapisz ofertę jako",
                defaultextension=".pdf",
                initialfile=filename,
                filetypes=[("Plik PDF", "*.pdf")]
            )
            
            if not save_path:
                return
            
            try:
                business_card = self.db.get_business_card()
                cat_order = {cat: idx for idx, cat in enumerate(category_order_list)}
                
                offer_data = {
                    'title': title,
                    'date': datetime.now().strftime('%d.%m.%Y'),
                    'items': selected_offer_items,
                    'business_card': business_card,
                    'category_order': cat_order
                }
                
                success = self.pdf_gen.generate_offer_pdf(offer_data, save_path)
                
                if success:
                    # Zapytaj czy zapisać jako szablon
                    if messagebox.askyesno("Zapisać szablon?", "PDF wygenerowano!\n\nCzy zapisać tę ofertę jako szablon do bazy?"):
                        save_as_template()
                    messagebox.showinfo("Sukces", f"PDF wygenerowano:\n{save_path}")
                    creator.destroy()
                else:
                    messagebox.showerror("Błąd", "Nie udało się wygenerować PDF.")
            except Exception as e:
                messagebox.showerror("Błąd", f"Wystąpił błąd:\n{str(e)}")
        
        btn_save_template = ctk.CTkButton(
            actions_frame,
            text="💾 Zapisz Szablon",
            width=150,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#3B8ED0",
            hover_color="#2E7AB8",
            command=save_as_template
        )
        btn_save_template.pack(side="left", padx=5)
        
        btn_generate = ctk.CTkButton(
            actions_frame,
            text="📄 Generuj PDF",
            width=150,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#C8102E",
            hover_color="#B00D24",
            command=generate_pdf_from_creator
        )
        btn_generate.pack(side="left", padx=5)
        
        # === ŚRODKOWY PANEL: 3 kolumny ===
        main_frame = ctk.CTkFrame(creator, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Konfiguracja grid dla 3 kolumn
        main_frame.grid_columnconfigure(0, weight=1, minsize=300)  # Lewy: Kategorie
        main_frame.grid_columnconfigure(1, weight=2, minsize=500)  # Środek: Produkty
        main_frame.grid_columnconfigure(2, weight=2, minsize=500)  # Prawy: Wybrane
        main_frame.grid_rowconfigure(0, weight=1)
        
        # === LEWY PANEL: Lista kategorii ===
        left_panel = ctk.CTkFrame(main_frame, fg_color="gray20")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        ctk.CTkLabel(
            left_panel,
            text="📁 Kategorie",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15)
        
        categories_scroll = ctk.CTkScrollableFrame(left_panel, fg_color="gray15")
        categories_scroll.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        selected_category_id = [None]  # Lista do przechowania referencji
        
        def load_categories():
            """Ładuje kategorie do lewego panelu"""
            for widget in categories_scroll.winfo_children():
                widget.destroy()
            
            categories = self.db.get_categories()
            
            for cat in categories:
                cat_btn = ctk.CTkButton(
                    categories_scroll,
                    text=cat['name'],
                    height=40,
                    font=ctk.CTkFont(size=13),
                    fg_color="gray25",
                    hover_color="#3B8ED0",
                    anchor="w",
                    command=lambda c=cat: select_category(c)
                )
                cat_btn.pack(fill="x", pady=2, padx=5)
        
        # === ŚRODKOWY PANEL: Produkty w kategorii ===
        middle_panel = ctk.CTkFrame(main_frame, fg_color="gray20")
        middle_panel.grid(row=0, column=1, sticky="nsew", padx=5)
        
        middle_title_label = ctk.CTkLabel(
            middle_panel,
            text="📦 Wybierz produkty",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        middle_title_label.pack(pady=15)
        
        products_scroll = ctk.CTkScrollableFrame(middle_panel, fg_color="gray15")
        products_scroll.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        def select_category(category):
            """Wyświetla produkty wybranej kategorii"""
            selected_category_id[0] = category['id']
            middle_title_label.configure(text=f"📦 {category['name']}")
            
            # Wyczyść poprzednie produkty
            for widget in products_scroll.winfo_children():
                widget.destroy()
            
            # Pobierz produkty
            products = self.db.get_products(category['id'])
            
            if not products:
                ctk.CTkLabel(
                    products_scroll,
                    text="Brak produktów w tej kategorii",
                    text_color="gray"
                ).pack(pady=20)
                return
            
            # Przycisk "Dodaj całą kategorię"
            add_all_btn = ctk.CTkButton(
                products_scroll,
                text=f"➕ Dodaj wszystkie produkty ({len(products)})",
                height=45,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color="#C8102E",
                hover_color="#B00D24",
                command=lambda: add_all_products_from_category(products)
            )
            add_all_btn.pack(fill="x", pady=10, padx=5)
            
            # Lista produktów
            for product in products:
                product_frame = ctk.CTkFrame(products_scroll, fg_color="gray25")
                product_frame.pack(fill="x", pady=3, padx=5)
                
                # Nazwa produktu
                name_label = ctk.CTkLabel(
                    product_frame,
                    text=product['name'],
                    font=ctk.CTkFont(size=12),
                    anchor="w"
                )
                name_label.pack(side="left", fill="x", expand=True, padx=10, pady=8)
                
                # Cena
                price_label = ctk.CTkLabel(
                    product_frame,
                    text=f"{product['purchase_price_net']:.2f} zł",
                    font=ctk.CTkFont(size=11),
                    text_color="gray"
                )
                price_label.pack(side="left", padx=10)
                
                # Przycisk dodaj
                add_btn = ctk.CTkButton(
                    product_frame,
                    text="➕",
                    width=40,
                    height=30,
                    fg_color="#3B8ED0",
                    hover_color="#2E7AB8",
                    command=lambda p=product: add_product_to_offer(p)
                )
                add_btn.pack(side="right", padx=5, pady=5)
        
        def add_all_products_from_category(products):
            """Dodaje wszystkie produkty z kategorii do oferty"""
            added = []
            already_in = []
            
            for product in products:
                # Sprawdź czy produkt już jest w ofercie
                if any(item.get('id') == product['id'] for item in selected_offer_items):
                    already_in.append(product['name'])
                else:
                    # Dodaj produkt
                    product_copy = product.copy()
                    product_copy['margin'] = product.get('default_margin', 30.0)
                    selected_offer_items.append(product_copy)
                    added.append(product['name'])
                    
                    # Dodaj kategorię do kolejności jeśli jeszcze nie ma
                    cat_name = product.get('category_name', 'Bez kategorii')
                    if cat_name not in category_order_list:
                        category_order_list.append(cat_name)
            
            # Odśwież widok
            refresh_offer_items()
            
            # Pokaż komunikaty zbiorcze
            messages = []
            if added:
                messages.append(f"✅ Dodano ({len(added)}):\n" + "\n".join([f"• {name}" for name in added]))
            if already_in:
                messages.append(f"ℹ️ Już w ofercie ({len(already_in)}):\n" + "\n".join([f"• {name}" for name in already_in]))
            
            if messages:
                messagebox.showinfo("Dodawanie produktów", "\n\n".join(messages))
        
        # === PRAWY PANEL: Wybrane produkty w ofercie ===
        right_panel = ctk.CTkFrame(main_frame, fg_color="gray20")
        right_panel.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        
        ctk.CTkLabel(
            right_panel,
            text="📋 Produkty w ofercie",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15)
        
        # Przycisk zmiany kategorii dla zaznaczonych
        selected_items_for_category_change = []
        
        def change_category_for_selected():
            """Zmienia kategorię dla zaznaczonych produktów"""
            if not selected_items_for_category_change:
                messagebox.showwarning("Brak zaznaczenia", "Zaznacz produkty, którym chcesz zmienić kategorię!")
                return
            
            # Dialog wyboru kategorii
            cat_dialog = ctk.CTkToplevel(creator)
            cat_dialog.title("Zmiana kategorii")
            cat_dialog.geometry("400x250")
            cat_dialog.transient(creator)
            cat_dialog.grab_set()
            
            # Centrowanie
            cat_dialog.update_idletasks()
            x = (cat_dialog.winfo_screenwidth() // 2) - (400 // 2)
            y = (cat_dialog.winfo_screenheight() // 2) - (250 // 2)
            cat_dialog.geometry(f"400x250+{x}+{y}")
            
            ctk.CTkLabel(
                cat_dialog,
                text=f"Zmień kategorię dla {len(selected_items_for_category_change)} produktów",
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(pady=20)
            
            ctk.CTkLabel(
                cat_dialog,
                text="Wybierz nową kategorię:",
                font=ctk.CTkFont(size=13)
            ).pack(pady=(10, 5))
            
            categories = self.db.get_categories()
            category_names = [cat['name'] for cat in categories]
            if not category_names:
                category_names = ["Bez kategorii"]
            
            category_menu = ctk.CTkOptionMenu(
                cat_dialog,
                values=category_names,
                height=35,
                width=300,
                font=ctk.CTkFont(size=12)
            )
            if category_names:
                category_menu.set(category_names[0])
            category_menu.pack(pady=10)
            
            def apply_category_change():
                new_category = category_menu.get()
                
                # Znajdź ID kategorii
                category_id = None
                for cat in categories:
                    if cat['name'] == new_category:
                        category_id = cat['id']
                        break
                
                # Zmień kategorię dla zaznaczonych
                for item in selected_items_for_category_change[:]:
                    # Usuń ze starej kategorii w kolejności
                    old_cat = item.get('category_name', 'Bez kategorii')
                    
                    # Zaktualizuj kategorię
                    item['category_name'] = new_category
                    item['category_id'] = category_id
                    
                    # Dodaj nową kategorię do kolejności jeśli nie ma
                    if new_category not in category_order_list:
                        category_order_list.append(new_category)
                
                # Wyczyść zaznaczenie
                selected_items_for_category_change.clear()
                
                # Odśwież widok
                refresh_offer_items()
                
                cat_dialog.destroy()
                messagebox.showinfo("Sukces", f"Zmieniono kategorię dla zaznaczonych produktów!")
            
            btn_frame = ctk.CTkFrame(cat_dialog, fg_color="transparent")
            btn_frame.pack(pady=20)
            
            ctk.CTkButton(
                btn_frame,
                text="Zastosuj",
                width=120,
                height=35,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color="#3B8ED0",
                hover_color="#2E7AB8",
                command=apply_category_change
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                btn_frame,
                text="Anuluj",
                width=120,
                height=35,
                font=ctk.CTkFont(size=13),
                fg_color="gray40",
                hover_color="gray50",
                command=cat_dialog.destroy
            ).pack(side="left", padx=5)
        
        change_cat_btn = ctk.CTkButton(
            right_panel,
            text="🔄 Zmień kategorię zaznaczonym",
            height=35,
            font=ctk.CTkFont(size=12),
            fg_color="#6C757D",
            hover_color="#5A6268",
            command=change_category_for_selected
        )
        change_cat_btn.pack(pady=(0, 5), padx=5, fill="x")
        
        offer_items_scroll = ctk.CTkScrollableFrame(right_panel, fg_color="gray15")
        offer_items_scroll.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        def add_product_to_offer(product):
            """Dodaje produkt do oferty (prawy panel)"""
            # Sprawdź czy produkt już jest w ofercie
            if any(item.get('id') == product['id'] for item in selected_offer_items):
                messagebox.showinfo("Info", f"Produkt '{product['name']}' już jest w ofercie!")
                return
            
            # Dodaj produkt
            product_copy = product.copy()
            product_copy['margin'] = product.get('default_margin', 30.0)
            selected_offer_items.append(product_copy)
            
            # Dodaj kategorię do kolejności jeśli jeszcze nie ma
            cat_name = product.get('category_name', 'Bez kategorii')
            if cat_name not in category_order_list:
                category_order_list.append(cat_name)
            
            refresh_offer_items()
        
        def remove_product_from_offer(product):
            """Usuwa produkt z oferty"""
            selected_offer_items.remove(product)
            refresh_offer_items()
        
        def refresh_offer_items():
            """Odświeża listę wybranych produktów"""
            for widget in offer_items_scroll.winfo_children():
                widget.destroy()
            
            if not selected_offer_items:
                ctk.CTkLabel(
                    offer_items_scroll,
                    text="Brak produktów\n\nDodaj produkty z lewej strony",
                    text_color="gray",
                    font=ctk.CTkFont(size=13)
                ).pack(pady=50)
                return
            
            # Grupuj po kategoriach
            items_by_category = {}
            for item in selected_offer_items:
                cat = item.get('category_name', 'Bez kategorii')
                if cat not in items_by_category:
                    items_by_category[cat] = []
                items_by_category[cat].append(item)
            
            # Wyświetl według kolejności kategorii
            for cat_name in category_order_list:
                if cat_name not in items_by_category:
                    continue
                
                # Nagłówek kategorii
                cat_header = ctk.CTkFrame(offer_items_scroll, fg_color="#C8102E")
                cat_header.pack(fill="x", pady=(10, 5), padx=5)
                
                ctk.CTkLabel(
                    cat_header,
                    text=cat_name,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="white"
                ).pack(side="left", padx=10, pady=8)
                
                # Przyciski kolejności kategorii
                cat_btn_frame = ctk.CTkFrame(cat_header, fg_color="transparent")
                cat_btn_frame.pack(side="right", padx=5)
                
                idx = category_order_list.index(cat_name)
                if idx > 0:
                    ctk.CTkButton(
                        cat_btn_frame,
                        text="⬆",
                        width=30,
                        height=25,
                        fg_color="gray30",
                        hover_color="gray40",
                        command=lambda c=cat_name: move_category_up(c)
                    ).pack(side="left", padx=2)
                
                if idx < len(category_order_list) - 1:
                    ctk.CTkButton(
                        cat_btn_frame,
                        text="⬇",
                        width=30,
                        height=25,
                        fg_color="gray30",
                        hover_color="gray40",
                        command=lambda c=cat_name: move_category_down(c)
                    ).pack(side="left", padx=2)
                
                # Produkty w kategorii
                for idx, item in enumerate(items_by_category[cat_name]):
                    item_frame = ctk.CTkFrame(offer_items_scroll, fg_color="gray25")
                    item_frame.pack(fill="x", pady=2, padx=5)
                    
                    # Górna część z checkboxem i nazwą
                    top_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                    top_frame.pack(side="top", fill="x", padx=5, pady=(5, 0))
                    
                    # Checkbox do zaznaczania
                    checkbox_var = ctk.BooleanVar(value=item in selected_items_for_category_change)
                    
                    def on_checkbox_change(itm=item, var=checkbox_var):
                        if var.get():
                            if itm not in selected_items_for_category_change:
                                selected_items_for_category_change.append(itm)
                        else:
                            if itm in selected_items_for_category_change:
                                selected_items_for_category_change.remove(itm)
                    
                    checkbox = ctk.CTkCheckBox(
                        top_frame,
                        text="",
                        variable=checkbox_var,
                        width=30,
                        command=on_checkbox_change
                    )
                    checkbox.pack(side="left", padx=(5, 5))
                    
                    # Nazwa
                    name_label = ctk.CTkLabel(
                        top_frame,
                        text=item['name'],
                        font=ctk.CTkFont(size=12),
                        anchor="w"
                    )
                    name_label.pack(side="left", fill="x", expand=True)
                    
                    # Szczegóły: cena, VAT, marża
                    details_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                    details_frame.pack(side="top", fill="x", padx=10, pady=(2, 8))
                    
                    detail_text = f"Cena: {item['purchase_price_net']:.2f} zł | VAT: {item['vat_rate']:.0f}% | Marża: {item.get('margin', 30):.1f}%"
                    ctk.CTkLabel(
                        details_frame,
                        text=detail_text,
                        font=ctk.CTkFont(size=10),
                        text_color="gray"
                    ).pack(side="left")
                    
                    # Przyciski
                    btn_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                    btn_frame.pack(side="right", padx=5, pady=5)
                    
                    # Przyciski kolejności produktu
                    if idx > 0:
                        ctk.CTkButton(
                            btn_frame,
                            text="⬆",
                            width=30,
                            height=30,
                            fg_color="gray30",
                            hover_color="gray40",
                            command=lambda c=cat_name, i=item: move_product_up_in_category(c, i)
                        ).pack(side="left", padx=2)
                    
                    if idx < len(items_by_category[cat_name]) - 1:
                        ctk.CTkButton(
                            btn_frame,
                            text="⬇",
                            width=30,
                            height=30,
                            fg_color="gray30",
                            hover_color="gray40",
                            command=lambda c=cat_name, i=item: move_product_down_in_category(c, i)
                        ).pack(side="left", padx=2)
                    
                    # Przycisk edytuj
                    ctk.CTkButton(
                        btn_frame,
                        text="✏️",
                        width=35,
                        height=30,
                        fg_color="gray30",
                        hover_color="#3B8ED0",
                        command=lambda i=item: edit_item_in_offer(i)
                    ).pack(side="left", padx=2)
                    
                    # Przycisk usuń
                    ctk.CTkButton(
                        btn_frame,
                        text="🗑️",
                        width=35,
                        height=30,
                        fg_color="gray30",
                        hover_color="#C8102E",
                        command=lambda i=item: remove_product_from_offer(i)
                    ).pack(side="left", padx=2)
        
        def move_category_up(cat_name):
            """Przesuwa kategorię w górę"""
            idx = category_order_list.index(cat_name)
            if idx > 0:
                category_order_list[idx], category_order_list[idx - 1] = category_order_list[idx - 1], category_order_list[idx]
                refresh_offer_items()
        
        def move_category_down(cat_name):
            """Przesuwa kategorię w dół"""
            idx = category_order_list.index(cat_name)
            if idx < len(category_order_list) - 1:
                category_order_list[idx], category_order_list[idx + 1] = category_order_list[idx + 1], category_order_list[idx]
                refresh_offer_items()
        
        def move_product_up_in_category(cat_name, item):
            """Przesuwa produkt w górę w ramach kategorii"""
            category_items = [i for i in selected_offer_items if i['category_name'] == cat_name]
            idx = category_items.index(item)
            if idx > 0:
                # Znajdź indeksy w głównej liście
                main_idx = selected_offer_items.index(item)
                main_idx_prev = selected_offer_items.index(category_items[idx - 1])
                # Zamień miejscami
                selected_offer_items[main_idx], selected_offer_items[main_idx_prev] = selected_offer_items[main_idx_prev], selected_offer_items[main_idx]
                refresh_offer_items()
        
        def move_product_down_in_category(cat_name, item):
            """Przesuwa produkt w dół w ramach kategorii"""
            category_items = [i for i in selected_offer_items if i['category_name'] == cat_name]
            idx = category_items.index(item)
            if idx < len(category_items) - 1:
                # Znajdź indeksy w głównej liście
                main_idx = selected_offer_items.index(item)
                main_idx_next = selected_offer_items.index(category_items[idx + 1])
                # Zamień miejscami
                selected_offer_items[main_idx], selected_offer_items[main_idx_next] = selected_offer_items[main_idx_next], selected_offer_items[main_idx]
                refresh_offer_items()
        
        def edit_item_in_offer(item):
            """Edytuje wartości produktu w ofercie"""
            edit_dialog = ctk.CTkToplevel(creator)
            edit_dialog.title("Edycja produktu w ofercie")
            edit_dialog.geometry("450x500")
            edit_dialog.transient(creator)
            edit_dialog.grab_set()
            
            # Centrowanie
            edit_dialog.update_idletasks()
            x = (edit_dialog.winfo_screenwidth() // 2) - (450 // 2)
            y = (edit_dialog.winfo_screenheight() // 2) - (500 // 2)
            edit_dialog.geometry(f"450x500+{x}+{y}")
            
            ctk.CTkLabel(edit_dialog, text="Edycja produktu", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
            
            form_frame = ctk.CTkFrame(edit_dialog, fg_color="transparent")
            form_frame.pack(pady=10, padx=20, fill="both")
            
            # Nazwa
            ctk.CTkLabel(form_frame, text="Nazwa:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(5, 2))
            name_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=12))
            name_entry.insert(0, item['name'])
            name_entry.pack(fill="x", pady=(0, 10))
            
            # Cena zakupu netto
            ctk.CTkLabel(form_frame, text="Cena zakupu netto:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(5, 2))
            price_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=12))
            price_entry.insert(0, str(item['purchase_price_net']))
            price_entry.pack(fill="x", pady=(0, 10))
            
            # VAT
            ctk.CTkLabel(form_frame, text="VAT (%):", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(5, 2))
            vat_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=12))
            vat_entry.insert(0, str(item['vat_rate']))
            vat_entry.pack(fill="x", pady=(0, 10))
            
            # Marża
            ctk.CTkLabel(form_frame, text="Marża (%):", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(5, 2))
            margin_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=12))
            margin_entry.insert(0, str(item.get('margin', 30)))
            margin_entry.pack(fill="x", pady=(0, 10))
            
            def save_edits():
                try:
                    item['name'] = name_entry.get().strip()
                    item['purchase_price_net'] = float(price_entry.get().strip().replace(',', '.'))
                    item['vat_rate'] = float(vat_entry.get().strip().replace(',', '.'))
                    item['margin'] = float(margin_entry.get().strip().replace(',', '.'))
                    
                    refresh_offer_items()
                    edit_dialog.destroy()
                    messagebox.showinfo("Sukces", "Wartości zostały zaktualizowane!")
                except ValueError:
                    messagebox.showerror("Błąd", "Nieprawidłowe wartości liczbowe!")
            
            ctk.CTkButton(
                edit_dialog,
                text="Zapisz zmiany",
                height=40,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color="#3B8ED0",
                hover_color="#2E7AB8",
                command=save_edits
            ).pack(pady=20)
        
        # === DOLNY PANEL: Duplikacja przycisków ===
        bottom_frame = ctk.CTkFrame(creator, fg_color="gray20", height=70)
        bottom_frame.pack(fill="x", padx=10, pady=(0, 10))
        bottom_frame.pack_propagate(False)
        
        bottom_actions = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        bottom_actions.pack(expand=True)
        
        ctk.CTkButton(
            bottom_actions,
            text="💾 Zapisz Szablon",
            width=180,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3B8ED0",
            hover_color="#2E7AB8",
            command=save_as_template
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            bottom_actions,
            text="📄 Generuj PDF",
            width=180,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#C8102E",
            hover_color="#B00D24",
            command=generate_pdf_from_creator
        ).pack(side="left", padx=10)
        
        # Inicjalizacja
        load_categories()
        
        # Jeśli edytujemy istniejącą ofertę
        if existing_offer_id:
            offer = self.db.get_offer_by_id(existing_offer_id)
            if offer:
                offer_title_var.set(offer['title'])
                selected_offer_items.extend(offer['items'])
                category_order_list.extend(offer.get('category_order', {}).keys())
                refresh_offer_items()
    
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
    
    def open_categories_window(self):
        """Otwiera okno zarządzania kategoriami"""
        
        # Okno dialogowe
        cat_window = ctk.CTkToplevel(self)
        cat_window.title("Zarządzanie Kategoriami")
        cat_window.geometry("700x500")
        cat_window.transient(self)
        cat_window.grab_set()
        
        # Centrowanie
        cat_window.update_idletasks()
        x = (cat_window.winfo_screenwidth() // 2) - (700 // 2)
        y = (cat_window.winfo_screenheight() // 2) - (500 // 2)
        cat_window.geometry(f"700x500+{x}+{y}")
        
        # Tytuł
        title_label = ctk.CTkLabel(
            cat_window,
            text="📁 Kategorie Produktów",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Ramka z listą kategorii
        list_frame = ctk.CTkFrame(cat_window)
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Scrollable frame dla kategorii
        scroll_frame = ctk.CTkScrollableFrame(list_frame, fg_color="gray20")
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        def refresh_categories():
            """Odświeża listę kategorii"""
            for widget in scroll_frame.winfo_children():
                widget.destroy()
            
            categories = self.db.get_categories()
            
            for cat in categories:
                cat_frame = ctk.CTkFrame(scroll_frame, fg_color="gray25")
                cat_frame.pack(fill="x", pady=5, padx=5)
                
                # Nazwa kategorii
                name_label = ctk.CTkLabel(
                    cat_frame,
                    text=cat['name'],
                    font=ctk.CTkFont(size=14, weight="bold"),
                    anchor="w"
                )
                name_label.pack(side="left", padx=10, pady=10)
                
                # Marża
                margin_label = ctk.CTkLabel(
                    cat_frame,
                    text=f"Marża: {cat['default_margin']:.1f}%",
                    font=ctk.CTkFont(size=12),
                    text_color="gray"
                )
                margin_label.pack(side="left", padx=10)
                
                # Przyciski akcji
                btn_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
                btn_frame.pack(side="right", padx=5)
                
                # Przycisk Edytuj
                edit_btn = ctk.CTkButton(
                    btn_frame,
                    text="✏️ Edytuj",
                    width=80,
                    height=30,
                    fg_color="#3B8ED0",
                    hover_color="#2E7AB8",
                    command=lambda c=cat: edit_category(c)
                )
                edit_btn.pack(side="left", padx=5)
                
                # Przycisk Usuń
                delete_btn = ctk.CTkButton(
                    btn_frame,
                    text="🗑️ Usuń",
                    width=80,
                    height=30,
                    fg_color="#C8102E",
                    hover_color="#B00D24",
                    command=lambda c=cat: delete_category(c)
                )
                delete_btn.pack(side="left", padx=5)
        
        def add_category():
            """Dodaje nową kategorię"""
            dialog = ctk.CTkToplevel(cat_window)
            dialog.title("Nowa Kategoria")
            dialog.geometry("400x250")
            dialog.transient(cat_window)
            dialog.grab_set()
            
            # Centrowanie
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
            y = (dialog.winfo_screenheight() // 2) - (250 // 2)
            dialog.geometry(f"400x250+{x}+{y}")
            
            ctk.CTkLabel(dialog, text="Nazwa kategorii:", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(20, 5))
            name_entry = ctk.CTkEntry(dialog, width=300, height=35, font=ctk.CTkFont(size=13))
            name_entry.pack(pady=5)
            
            ctk.CTkLabel(dialog, text="Domyślna marża (%):", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(15, 5))
            margin_entry = ctk.CTkEntry(dialog, width=300, height=35, font=ctk.CTkFont(size=13))
            margin_entry.insert(0, "30.0")
            margin_entry.pack(pady=5)
            
            def save():
                name = name_entry.get().strip()
                try:
                    margin = float(margin_entry.get().strip().replace(',', '.'))
                except:
                    messagebox.showerror("Błąd", "Marża musi być liczbą!")
                    return
                
                if not name:
                    messagebox.showwarning("Uwaga", "Wprowadź nazwę kategorii!")
                    return
                
                result = self.db.add_category(name, margin)
                if result:
                    messagebox.showinfo("Sukces", "Kategoria została dodana!")
                    refresh_categories()
                    dialog.destroy()
                else:
                    messagebox.showerror("Błąd", "Kategoria o tej nazwie już istnieje!")
            
            ctk.CTkButton(dialog, text="Dodaj", command=save, width=150, height=40, 
                         fg_color="#3B8ED0", hover_color="#2E7AB8").pack(pady=20)
        
        def edit_category(cat):
            """Edytuje kategorię"""
            dialog = ctk.CTkToplevel(cat_window)
            dialog.title("Edytuj Kategorię")
            dialog.geometry("400x250")
            dialog.transient(cat_window)
            dialog.grab_set()
            
            # Centrowanie
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
            y = (dialog.winfo_screenheight() // 2) - (250 // 2)
            dialog.geometry(f"400x250+{x}+{y}")
            
            ctk.CTkLabel(dialog, text="Nazwa kategorii:", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(20, 5))
            name_entry = ctk.CTkEntry(dialog, width=300, height=35, font=ctk.CTkFont(size=13))
            name_entry.insert(0, cat['name'])
            name_entry.pack(pady=5)
            
            ctk.CTkLabel(dialog, text="Domyślna marża (%):", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(15, 5))
            margin_entry = ctk.CTkEntry(dialog, width=300, height=35, font=ctk.CTkFont(size=13))
            margin_entry.insert(0, str(cat['default_margin']))
            margin_entry.pack(pady=5)
            
            def save():
                name = name_entry.get().strip()
                try:
                    margin = float(margin_entry.get().strip().replace(',', '.'))
                except:
                    messagebox.showerror("Błąd", "Marża musi być liczbą!")
                    return
                
                if not name:
                    messagebox.showwarning("Uwaga", "Wprowadź nazwę kategorii!")
                    return
                
                result = self.db.update_category(cat['id'], name, margin)
                if result:
                    messagebox.showinfo("Sukces", "Kategoria została zaktualizowana!")
                    refresh_categories()
                    self.load_products()  # Odśwież listę produktów
                    dialog.destroy()
                else:
                    messagebox.showerror("Błąd", "Nie można zaktualizować kategorii!")
            
            ctk.CTkButton(dialog, text="Zapisz", command=save, width=150, height=40,
                         fg_color="#3B8ED0", hover_color="#2E7AB8").pack(pady=20)
        
        def delete_category(cat):
            """Usuwa kategorię"""
            if messagebox.askyesno("Potwierdzenie", f"Czy na pewno usunąć kategorię '{cat['name']}'?\n\nUwaga: Można usunąć tylko kategorie bez przypisanych produktów."):
                result = self.db.delete_category(cat['id'])
                if result:
                    messagebox.showinfo("Sukces", "Kategoria została usunięta!")
                    refresh_categories()
                    self.load_products()
                else:
                    messagebox.showerror("Błąd", "Nie można usunąć kategorii. Prawdopodobnie ma przypisane produkty.")
        
        # Przycisk dodaj kategorię
        add_btn = ctk.CTkButton(
            cat_window,
            text="➕ Dodaj Kategorię",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color="#3B8ED0",
            hover_color="#2E7AB8",
            command=add_category
        )
        add_btn.pack(pady=10)
        
        # Załaduj kategorie
        refresh_categories()
    
    def open_saved_offers_window(self):
        """Otwiera okno z zapisanymi ofertami"""
        
        # Okno dialogowe
        offers_window = ctk.CTkToplevel(self)
        offers_window.title("Zapisane Oferty")
        offers_window.geometry("800x500")
        offers_window.transient(self)
        offers_window.grab_set()
        
        # Centrowanie
        offers_window.update_idletasks()
        x = (offers_window.winfo_screenwidth() // 2) - (800 // 2)
        y = (offers_window.winfo_screenheight() // 2) - (500 // 2)
        offers_window.geometry(f"800x500+{x}+{y}")
        
        # Tytuł
        title_label = ctk.CTkLabel(
            offers_window,
            text="💾 Zapisane Oferty",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Ramka z listą ofert
        list_frame = ctk.CTkFrame(offers_window)
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Scrollable frame dla ofert
        scroll_frame = ctk.CTkScrollableFrame(list_frame, fg_color="gray20")
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        def refresh_offers():
            """Odświeża listę ofert"""
            for widget in scroll_frame.winfo_children():
                widget.destroy()
            
            offers = self.db.get_saved_offers()
            
            if not offers:
                empty_label = ctk.CTkLabel(
                    scroll_frame,
                    text="Brak zapisanych ofert",
                    font=ctk.CTkFont(size=14),
                    text_color="gray"
                )
                empty_label.pack(pady=50)
                return
            
            for offer in offers:
                offer_frame = ctk.CTkFrame(scroll_frame, fg_color="gray25")
                offer_frame.pack(fill="x", pady=5, padx=5)
                
                # Tytuł oferty
                title_label = ctk.CTkLabel(
                    offer_frame,
                    text=offer['title'],
                    font=ctk.CTkFont(size=14, weight="bold"),
                    anchor="w"
                )
                title_label.pack(side="top", anchor="w", padx=10, pady=(10, 5))
                
                # Data
                date_label = ctk.CTkLabel(
                    offer_frame,
                    text=f"Utworzono: {offer['created_date']} | Zmodyfikowano: {offer['modified_date']}",
                    font=ctk.CTkFont(size=11),
                    text_color="gray",
                    anchor="w"
                )
                date_label.pack(side="top", anchor="w", padx=10, pady=(0, 10))
                
                # Przyciski akcji
                btn_frame = ctk.CTkFrame(offer_frame, fg_color="transparent")
                btn_frame.pack(side="right", padx=10, pady=5)
                
                # Przycisk Edytuj
                edit_btn = ctk.CTkButton(
                    btn_frame,
                    text="✏️ Edytuj",
                    width=100,
                    height=30,
                    fg_color="#28A745",
                    hover_color="#218838",
                    command=lambda o=offer: edit_offer(o)
                )
                edit_btn.pack(side="left", padx=5)
                
                # Przycisk Generuj PDF
                pdf_btn = ctk.CTkButton(
                    btn_frame,
                    text="📄 Generuj PDF",
                    width=120,
                    height=30,
                    fg_color="#3B8ED0",
                    hover_color="#2E7AB8",
                    command=lambda o=offer: generate_from_saved(o)
                )
                pdf_btn.pack(side="left", padx=5)
                
                # Przycisk Usuń
                delete_btn = ctk.CTkButton(
                    btn_frame,
                    text="🗑️ Usuń",
                    width=80,
                    height=30,
                    fg_color="#C8102E",
                    hover_color="#B00D24",
                    command=lambda o=offer: delete_offer(o)
                )
                delete_btn.pack(side="left", padx=5)
        
        def edit_offer(offer):
            """Otwiera kreator oferty w trybie edycji"""
            offers_window.destroy()
            self.open_offer_creator(existing_offer_id=offer['id'])
        
        def generate_from_saved(offer):
            """Generuje PDF z zapisanej oferty"""
            full_offer = self.db.get_offer_by_id(offer['id'])
            if not full_offer:
                messagebox.showerror("Błąd", "Nie można załadować oferty!")
                return
            
            # Wybór lokalizacji zapisu
            filename = f"{offer['title']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
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
                business_card = self.db.get_business_card()
                offer_data = {
                    'title': full_offer['title'],
                    'date': datetime.now().strftime('%d.%m.%Y'),
                    'items': full_offer['items'],
                    'business_card': business_card,
                    'category_order': full_offer.get('category_order', {})
                }
                
                # Generuj PDF
                success = self.pdf_gen.generate_offer_pdf(offer_data, save_path)
                
                if success:
                    messagebox.showinfo("Sukces", f"Oferta PDF została wygenerowana!\n\nZapisano jako:\n{save_path}")
                else:
                    messagebox.showerror("Błąd", "Nie udało się wygenerować PDF.")
                
            except Exception as e:
                messagebox.showerror("Błąd", f"Wystąpił błąd:\n{str(e)}")
        
        def delete_offer(offer):
            """Usuwa zapisaną ofertę"""
            if messagebox.askyesno("Potwierdzenie", f"Czy na pewno usunąć ofertę '{offer['title']}'?"):
                result = self.db.delete_offer(offer['id'])
                if result:
                    messagebox.showinfo("Sukces", "Oferta została usunięta!")
                    refresh_offers()
                else:
                    messagebox.showerror("Błąd", "Nie można usunąć oferty!")
        
        # Załaduj oferty
        refresh_offers()
    
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
