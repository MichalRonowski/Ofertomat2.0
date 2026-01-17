"""
Generator testowych produktów CSV dla Ofertomat 2.0
Generuje 2000 produktów w różnych kategoriach
"""

import csv
import random

# Kategorie produktów z prefiksami
CATEGORIES = {
    'W': ('Warzywa i owoce', [
        'Pomidor', 'Ogórek', 'Papryka', 'Cebula', 'Czosnek', 'Marchew', 'Ziemniaki',
        'Sałata', 'Rukola', 'Szpinak', 'Brokuł', 'Kalafior', 'Kapusta', 'Por',
        'Seler', 'Pietruszka', 'Burak', 'Dynia', 'Cukinia', 'Bakłażan',
        'Jabłko', 'Gruszka', 'Banan', 'Pomarańcza', 'Cytryna', 'Mandarynka',
        'Grejpfrut', 'Ananas', 'Mango', 'Awokado', 'Arbuz', 'Melon'
    ]),
    'M': ('Mięso i ryby', [
        'Kurczak', 'Indyk', 'Kaczka', 'Wieprzowina', 'Wołowina', 'Cielęcina',
        'Łosoś', 'Dorsz', 'Tuńczyk', 'Pstrąg', 'Makrela', 'Sardynka', 'Halibut',
        'Sola', 'Karp', 'Sandacz', 'Okoń', 'Śledź', 'Krewetki', 'Kalmary',
        'Małże', 'Ośmiornica', 'Homary', 'Raki'
    ]),
    'N': ('Nabiał', [
        'Mleko', 'Śmietana', 'Jogurt', 'Kefir', 'Maślanka', 'Ser', 'Twaróg',
        'Masło', 'Margaryna', 'Serek', 'Mascarpone', 'Ricotta', 'Feta',
        'Parmezan', 'Gouda', 'Camembert', 'Brie', 'Mozzarella', 'Cheddar'
    ]),
    'P': ('Przyprawy i sosy', [
        'Sól', 'Pieprz', 'Papryka', 'Oregano', 'Bazylia', 'Tymianek', 'Rozmaryn',
        'Majeranek', 'Cynamon', 'Gałka', 'Imbir', 'Kurkuma', 'Curry', 'Kminek',
        'Koper', 'Kolendra', 'Mięta', 'Szałwia', 'Estragon', 'Kardamon',
        'Sos sojowy', 'Ketchup', 'Musztarda', 'Majonez', 'Pesto', 'Tabasco',
        'Ocet', 'Olej', 'Oliwa'
    ]),
    'J': ('Jedzenie suche', [
        'Makaron', 'Ryż', 'Kasza', 'Płatki', 'Mąka', 'Cukier', 'Drożdże',
        'Proszek do pieczenia', 'Soda', 'Skrobia', 'Mak', 'Rodzynki', 'Orzechy',
        'Migdały', 'Pistacje', 'Nerkowce', 'Orzechy laskowe', 'Orzechy włoskie',
        'Daktyle', 'Figi', 'Morele', 'Śliwki suszone', 'Żurawina suszona'
    ]),
    'D': ('Desery i słodycze', [
        'Lody', 'Sorbet', 'Ciasto', 'Tort', 'Babeczka', 'Ciastko', 'Sernik',
        'Tiramisu', 'Panna cotta', 'Mus', 'Krem', 'Budyń', 'Kisiel', 'Galaretka',
        'Czekolada', 'Cukierki', 'Lizaki', 'Guma', 'Draże', 'Wafel'
    ]),
    'A': ('Akcesoria kuchenne', [
        'Papier', 'Serwetka', 'Ścierka', 'Rękawice', 'Folia', 'Worek', 'Pojemnik',
        'Tacka', 'Talerz', 'Kubek', 'Sztućce', 'Nóż', 'Deska', 'Garnek',
        'Patelnia', 'Forma', 'Miska', 'Sitko', 'Trzepaczka', 'Łyżka'
    ]),
    'B': ('Napoje', [
        'Woda', 'Sok', 'Napój', 'Cola', 'Sprite', 'Fanta', 'Pepsi', 'Lemoniada',
        'Herbata', 'Kawa', 'Kakao', 'Czekolada na gorąco', 'Kompot', 'Syrop',
        'Piwo', 'Wino', 'Szampan', 'Whisky', 'Wódka', 'Rum', 'Gin', 'Likier'
    ]),
    'G': ('Gastronomia gotowe', [
        'Pizza', 'Burger', 'Kebab', 'Sushi', 'Wrap', 'Kanapka', 'Bagietka',
        'Croissant', 'Pączek', 'Rogalik', 'Precel', 'Bajgiel', 'Focaccia',
        'Ciabatta', 'Baguette', 'Tortilla', 'Naleśnik', 'Pierogi', 'Kluski'
    ]),
    'S': ('Sosy i dodatki', [
        'Sos czosnkowy', 'Sos barbecue', 'Sos miodowo-musztardowy', 'Sos ranch',
        'Sos cezar', 'Sos tysiąca wysp', 'Sos chili', 'Sos słodko-kwaśny',
        'Sos teriyaki', 'Sos curry', 'Sos śmietanowy', 'Sos pieczarkowy',
        'Sos pomidorowy', 'Sos beszamel', 'Sos holenderski', 'Sos tatarski'
    ])
}

# Warianty produktów
VARIANTS = [
    'świeży', 'mrożony', 'suszony', 'wędzony', 'grillowany', 'pieczony',
    'gotowany', 'surowy', 'organiczny', 'bio', 'ekologiczny', 'premium',
    'standard', 'ekonomiczny', 'rodzinny', 'mini', 'maxi', 'XXL',
    'light', 'zero', 'extra', 'deluxe', 'classic', 'tradycyjny',
    'włoski', 'francuski', 'hiszpański', 'grecki', 'amerykański', 'azjatycki'
]

# Cechy produktów
FEATURES = [
    'z', 'bez', 'w', 'na', 'do', 'ze', 'typu', 'rodzaj', 'gatunek', 'klasa'
]

ADDITIONAL_WORDS = [
    'pikantny', 'łagodny', 'ostry', 'słodki', 'kwaśny', 'gorzki', 'słony',
    'aromatyczny', 'delikatny', 'intensywny', 'naturalny', 'sztuczny',
    'kolorowy', 'biały', 'czarny', 'czerwony', 'zielony', 'żółty',
    'duży', 'mały', 'średni', 'cienki', 'gruby', 'długi', 'krótki'
]

# Jednostki miary
UNITS = ['kg', 'szt.', 'l', 'op.', 'rolka', 'puszka', 'butelka', 'opak.', 'gram', 'ml']

# Stawki VAT
VAT_RATES = ['8%', '23%', '5%']

def generate_product_name(base_name, index):
    """Generuje unikalną nazwę produktu"""
    variants = []
    
    # Dodaj wariant (30% szans)
    if random.random() < 0.3:
        variants.append(random.choice(VARIANTS))
    
    # Dodaj cechę (40% szans)
    if random.random() < 0.4:
        variants.append(random.choice(FEATURES))
        variants.append(random.choice(ADDITIONAL_WORDS))
    
    # Buduj nazwę
    if variants:
        name = f"{base_name} {' '.join(variants)}"
    else:
        name = base_name
    
    # Dodaj numer jeśli nazwa jest zbyt prosta
    if len(name) < 15 or random.random() < 0.2:
        name += f" #{index}"
    
    return name

def generate_products(count=2000):
    """Generuje listę produktów"""
    products = []
    products_per_category = count // len(CATEGORIES)
    
    for prefix, (category_name, base_names) in CATEGORIES.items():
        for i in range(products_per_category):
            # Generuj kod
            code = f"{prefix}{str(i+1).zfill(4)}"
            
            # Wybierz bazową nazwę i wygeneruj wariant
            base_name = random.choice(base_names)
            name = generate_product_name(base_name, i+1)
            
            # Jednostka
            unit = random.choice(UNITS)
            
            # Cena (od 0.50 do 500 zł)
            if prefix in ['A', 'B']:  # Akcesoria i napoje często droższe
                price = round(random.uniform(5.0, 150.0), 2)
            elif prefix in ['M', 'D']:  # Mięso i desery średnio drogie
                price = round(random.uniform(10.0, 100.0), 2)
            else:
                price = round(random.uniform(0.5, 50.0), 2)
            
            # VAT - 8% dla żywności, 23% dla reszty głównie
            if prefix in ['A', 'B'] or random.random() < 0.1:
                vat = random.choice(VAT_RATES)
            else:
                vat = '8%'
            
            products.append({
                'Kod': code,
                'Nazwa': name,
                'Jednostka': unit,
                'Cena zakupu netto': f"{price:.2f}".replace('.', ','),
                'VAT': vat
            })
    
    # Jeśli potrzebujemy więcej produktów, dodaj losowe
    remaining = count - len(products)
    if remaining > 0:
        for i in range(remaining):
            prefix = random.choice(list(CATEGORIES.keys()))
            category_name, base_names = CATEGORIES[prefix]
            
            code = f"{prefix}{str(1000+i).zfill(4)}"
            base_name = random.choice(base_names)
            name = generate_product_name(base_name, 1000+i)
            unit = random.choice(UNITS)
            price = round(random.uniform(0.5, 200.0), 2)
            vat = '8%' if prefix not in ['A', 'B'] else random.choice(VAT_RATES)
            
            products.append({
                'Kod': code,
                'Nazwa': name,
                'Jednostka': unit,
                'Cena zakupu netto': f"{price:.2f}".replace('.', ','),
                'VAT': vat
            })
    
    return products

def save_to_csv(products, filename='test_produkty_2000.csv'):
    """Zapisuje produkty do pliku CSV"""
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['Kod', 'Nazwa', 'Jednostka', 'Cena zakupu netto', 'VAT']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for product in products:
            writer.writerow(product)
    
    print(f"✅ Wygenerowano {len(products)} produktów do pliku: {filename}")

if __name__ == "__main__":
    # Generuj 2000 produktów
    products = generate_products(2000)
    save_to_csv(products, 'test_produkty_2000.csv')
    
    # Statystyki
    print(f"\n📊 Statystyki:")
    print(f"   Całkowita liczba produktów: {len(products)}")
    
    # Policz produkty per kategoria
    category_counts = {}
    for product in products:
        prefix = product['Kod'][0]
        category_counts[prefix] = category_counts.get(prefix, 0) + 1
    
    print(f"\n   Produkty per kategoria:")
    for prefix, count in sorted(category_counts.items()):
        category_name = CATEGORIES[prefix][0]
        print(f"   {prefix} - {category_name}: {count}")
