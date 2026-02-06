from faker import Faker
import random
from datetime import datetime

fake = Faker('pt_BR')

class Amazon:
    PLATFORM_NAME = "Amazon"

    CATEGORIES = {
        'Smartphones': ['iPhone 15 Pro', 'Samsung Galaxy S24', 'Xiaomi 14'],
        'Laptops': ['MacBook Pro M3', 'Dell XPS 15', 'Lenovo ThinkPad'],
        'TVs': ['Samsung QLED 65"', 'LG OLED 55"', 'Sony Bravia 75"'],
        'Fones': ['AirPods Pro', 'Sony WH-1000XM5', 'JBL Tune 510'],
    }

    PRICE_RANGES = {
        'Smartphones': (800, 2000),
        'Laptops': (1200, 3500),
        'TVs': (1500, 5000),
        'Fones': (100, 500),
    }

    @staticmethod
    def generate_sale_event():
        category = random.choice(list(Amazon.CATEGORIES.keys()))
        product = random.choice(Amazon.CATEGORIES[category])
        price_min, price_max = Amazon.PRICE_RANGES[category]

        quantity = random.choices([1,2,3,4], weights=[70, 20, 7, 3])[0]
        price = round(random.uniform(price_min, price_max), 2)

        return {
            'event_id': f'SF_{fake.uuid4()}',
            'timestamp': datetime.now().isoformat(),
            'platform': Amazon.PLATFORM_NAME,
            'event_type': 'sale',
            'product_id': f'PROD_{random.randint(1000, 9999)}',
            'product_name': product,
            'quantity': quantity,
            'unit_price': price,
            'total': round(price * quantity, 2),
            'customer_id': f'CUST+{random.randint(1000, 9999)}',
            'region': random.choice(['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']),
            'payment_method': random.choice(['credit_card', 'debit_card', 'pix', 'boleto']),
        }
    
    @staticmethod
    def generate_stock_event():
        category = random.choice(list(Amazon.CATEGORIES.keys()))
        product = random.choice(Amazon.CATEGORIES[category])
        
        return {
            'event_id': f'SF_STK_{fake.uuid4()}',
            'timestamp': datetime.now().isoformat(),
            'platform': Amazon.PLATFORM_NAME,
            'event_type': 'stock_update',
            'product_id': f'PROD_{random.randint(1000, 9999)}',
            'product_name': product,
            'category': category,
            'stock_quantity': random.randint(0, 500),
            'warehouse': random.choice(['SP-01', 'RJ-02', 'MG-03']),
        }

    @staticmethod
    def generate_view_event():
        category = random.choice(list(Amazon.CATEGORIES.keys()))
        product = random.choice(Amazon.CATEGORIES[category])
    
        is_logged_in = random.choices([True, False], weights=[60, 40])[0]
        customer_id = f'CUST+{random.randint(1000, 9999)}' if is_logged_in else None

        return {
            'event_id': f'SF_VIEW_{fake.uuid4()}',
            'timestamp': datetime.now().isoformat(),
            'platform': Amazon.PLATFORM_NAME,
            'event_type': 'product_view',
            'product_id': f'PROD_{random.randint(1000, 9999)}',
            'product_name': product,
            'category': category,
            'customer_id': customer_id,
            'session_id': f'SESS_{fake.uuid4()}',
            'device_type': random.choice(['Mobile', 'Desktop', 'Tablet']),
            'referrer': random.choice(['Google_Ads', 'Organic_Search', 'Social_Media', 'Direct', 'Email_Mkt']),
            'region': random.choice(['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul'])
        }