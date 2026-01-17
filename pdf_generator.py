from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from datetime import datetime
from typing import List, Dict
import os

class PDFGenerator:
    """Klasa do generowania raportów PDF z ofert"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
        # Rejestruj czcionkę obsługującą Unicode (polskie znaki)
        try:
            # Pobierz ścieżkę do systemowych czcionek Windows
            import winreg
            import pathlib
            
            # Znajdź katalog czcionek Windows
            fonts_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
            
            # Użyj Arial Unicode MS lub Arial - obie obsługują polskie znaki
            arial_path = os.path.join(fonts_dir, 'arial.ttf')
            arial_bold_path = os.path.join(fonts_dir, 'arialbd.ttf')
            
            if os.path.exists(arial_path):
                pdfmetrics.registerFont(TTFont('ArialUnicode', arial_path))
                self.font_name = 'ArialUnicode'
            else:
                self.font_name = 'Helvetica'
                
            if os.path.exists(arial_bold_path):
                pdfmetrics.registerFont(TTFont('ArialUnicode-Bold', arial_bold_path))
                self.font_bold = 'ArialUnicode-Bold'
            else:
                self.font_bold = 'Helvetica-Bold'
                
        except Exception as e:
            print(f"Nie można załadować czcionki Arial: {e}")
            self.font_name = 'Helvetica'
            self.font_bold = 'Helvetica-Bold'
        
        # Dodaj niestandardowe style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            fontName=self.font_bold,
            textColor=colors.HexColor('#8B8B8B'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CategoryHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            fontName=self.font_bold,
            textColor=colors.HexColor('#C8102E'),
            spaceAfter=10,
            spaceBefore=20,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='TableText',
            parent=self.styles['Normal'],
            fontSize=8,
            fontName=self.font_name,
            leading=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Normal'],
            fontSize=14,
            fontName=self.font_bold,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=5
        ))
        
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName=self.font_bold,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=5
        ))
        
        self.styles.add(ParagraphStyle(
            name='DateItalic',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName=self.font_name,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=20
        ))
    
    def calculate_price(self, purchase_price: float, margin: float, vat_rate: float, quantity: float = 1):
        """
        Kalkuluje ceny
        
        Returns:
            dict z kluczami: net_unit, gross_unit, net_total, vat_amount, gross_total
        """
        # Cena jednostkowa netto sprzedaży
        net_unit = purchase_price * (1 + margin / 100)
        
        # Cena jednostkowa brutto
        gross_unit = net_unit * (1 + vat_rate / 100)
        
        # Wartości dla ilości
        net_total = net_unit * quantity
        vat_amount = net_total * (vat_rate / 100)
        gross_total = net_total + vat_amount
        
        return {
            'net_unit': round(net_unit, 2),
            'gross_unit': round(gross_unit, 2),
            'net_total': round(net_total, 2),
            'vat_amount': round(vat_amount, 2),
            'gross_total': round(gross_total, 2)
        }
    
    def add_watermark(self, canvas_obj, doc):
        """Dodaje znak wodny (logo) w tle każdej strony"""
        logo_path = 'logo_piwowar.png'
        if os.path.exists(logo_path):
            try:
                # Zapisz stan
                canvas_obj.saveState()
                
                # Ustaw przezroczystość
                canvas_obj.setFillAlpha(0.1)
                
                # Wycentruj logo na stronie
                page_width, page_height = A4
                logo_width = 15*cm
                logo_height = 6*cm
                x = (page_width - logo_width) / 2
                y = (page_height - logo_height) / 2
                
                # Narysuj logo jako znak wodny
                canvas_obj.drawImage(logo_path, x, y, width=logo_width, height=logo_height, 
                                    mask='auto', preserveAspectRatio=True)
                
                # Przywróć stan
                canvas_obj.restoreState()
            except Exception as e:
                print(f"Błąd dodawania znaku wodnego: {e}")
    
    def generate_offer_pdf(self, offer_data: Dict, output_path: str, progress_callback=None) -> bool:
        """
        Generuje PDF z ofertą
        
        Args:
            offer_data: Słownik z danymi oferty:
                - title: str (tytuł oferty)
                - date: str (data, opcjonalnie)
                - items: List[Dict] - produkty z polami:
                    - name: str
                    - quantity: float
                    - purchase_price_net: float
                    - vat_rate: float
                    - margin: float (z kategorii)
                    - category_name: str
            output_path: Ścieżka do pliku wyjściowego PDF
            progress_callback: Opcjonalna funkcja callback(current, total) dla progress bar
        
        Returns:
            bool - True jeśli sukces
        """
        try:
            # Stwórz katalog jeśli nie istnieje
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            
            # Utwórz dokument
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Elementy dokumentu
            elements = []
            
            # 1. Logo w nagłówku (jeśli istnieje)
            logo_path = 'logo_piwowar.png'
            if os.path.exists(logo_path):
                try:
                    logo = Image(logo_path, width=8*cm, height=3*cm, kind='proportional')
                    logo.hAlign = 'CENTER'
                    elements.append(logo)
                    elements.append(Spacer(1, 15))
                except Exception as e:
                    print(f"Nie można załadować logo: {e}")
            
            # 2. Wizytówka - Firma (pogrubiona, wyśrodkowana)
            business_card = offer_data.get('business_card')
            if business_card and business_card.get('company'):
                company_para = Paragraph(business_card['company'], self.styles['CompanyName'])
                elements.append(company_para)
            
            # 3. Wizytówka - reszta danych (pogrubiona, wyśrodkowana)
            if business_card:
                contact_parts = []
                if business_card.get('full_name'):
                    contact_parts.append(business_card['full_name'])
                if business_card.get('phone'):
                    contact_parts.append(f"Tel: {business_card['phone']}")
                if business_card.get('email'):
                    contact_parts.append(f"E-mail: {business_card['email']}")
                
                if contact_parts:
                    contact_para = Paragraph(" | ".join(contact_parts), self.styles['ContactInfo'])
                    elements.append(contact_para)
            
            # 4. Data (kursywa, wyśrodkowana)
            date_str = offer_data.get('date', datetime.now().strftime('%d.%m.%Y'))
            date_para = Paragraph(f"<i>Data: {date_str}</i>", self.styles['DateItalic'])
            elements.append(date_para)
            
            # 5. Tytuł (np. "Oferta handlowa")
            title = offer_data.get('title', 'Oferta handlowa')
            elements.append(Paragraph(title, self.styles['CustomTitle']))
            elements.append(Spacer(1, 20))
            
            # Pogrupuj produkty po kategoriach
            items_by_category = {}
            for item in offer_data.get('items', []):
                if item is None:
                    continue  # Pomiń None items
                category = item.get('category_name', 'Bez kategorii')
                if category not in items_by_category:
                    items_by_category[category] = []
                items_by_category[category].append(item)
            
            # Suma całkowita
            grand_total_net = 0
            grand_total_gross = 0
            
            # Pobierz kolejność kategorii lub użyj sortowania alfabetycznego
            category_order = offer_data.get('category_order', {})
            
            # Sortuj kategorie według niestandardowej kolejności
            def get_category_order(cat_name):
                return category_order.get(cat_name, 999)  # Kategorie bez kolejności na końcu
            
            sorted_categories = sorted(items_by_category.items(), 
                                      key=lambda x: (get_category_order(x[0]), x[0]))
            
            # Progress tracking dla dużych zbiorów
            total_items = sum(len(items) for _, items in sorted_categories)
            processed_items = 0
            
            if progress_callback:
                progress_callback(0, total_items)
            
            # Dla każdej kategorii
            for cat_idx, (category_name, items) in enumerate(sorted_categories):
                # Nagłówek kategorii
                elements.append(Paragraph(category_name, self.styles['CategoryHeader']))
                
                # Tabela produktów
                table_data = [
                    ['Nazwa', 'Cena netto', 'J.M.', 'VAT', 'Cena brutto']
                ]
                
                category_total_net = 0
                category_total_gross = 0
                
                for item_idx, item in enumerate(items):
                    prices = self.calculate_price(
                        item['purchase_price_net'],
                        item.get('margin', item.get('default_margin', 30.0)),
                        item['vat_rate'],
                        item.get('quantity', 1.0)
                    )
                    
                    category_total_net += prices['net_total']
                    category_total_gross += prices['gross_total']
                    
                    # Użyj Paragraph dla nazwy aby obsługiwać długie teksty
                    name_para = Paragraph(item['name'], self.styles['TableText'])
                    
                    table_data.append([
                        name_para,
                        f"{prices['net_unit']:.2f}",
                        f"zł/{item.get('unit', 'szt.')}",
                        f"{item['vat_rate']:.0f}%",
                        f"{prices['gross_unit']:.2f} zł"
                    ])
                    
                    # Aktualizuj progress co 50 produktów dla dużych zbiorów
                    processed_items += 1
                    if progress_callback and (processed_items % 50 == 0 or processed_items == total_items):
                        progress_callback(processed_items, total_items)
                
                grand_total_net += category_total_net
                grand_total_gross += category_total_gross
                
                # Stwórz tabelę - dostosowane szerokości kolumn
                table = Table(table_data, colWidths=[9*cm, 2.5*cm, 2*cm, 1.5*cm, 2.5*cm])
                
                # Stylizacja tabeli
                table.setStyle(TableStyle([
                    # Nagłówek
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C8102E')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), self.font_bold),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    
                    # Dane
                    ('FONTNAME', (0, 1), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Siatka
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    
                    # Padding
                    ('TOPPADDING', (0, 1), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 15))
            
            # Informacja o ważności oferty
            elements.append(Spacer(1, 20))
            validity_style = ParagraphStyle(
                name='Validity',
                parent=self.styles['Normal'],
                fontSize=8,
                fontName=self.font_name,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
            validity_text = "<i>Oferta ważna w dniu przedstawienia do momentu zmiany cen rynkowych.</i>"
            elements.append(Paragraph(validity_text, validity_style))
            
            # Zbuduj PDF ze znakiem wodnym
            doc.build(elements, onFirstPage=self.add_watermark, onLaterPages=self.add_watermark)
            return True
            
        except Exception as e:
            import traceback
            print(f"Błąd generowania PDF: {e}")
            traceback.print_exc()
            return False
