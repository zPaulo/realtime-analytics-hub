import os
import time
import json
from kafka import KafkaProducer
from platforms.amazon import Amazon
from decouple import config
import random


KAFKA_SERVER = config('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
MOCK_AUTO_START = config('MOCK_AUTO_START', 'false') == 'true'
MOCK_INTERVAL_MIN = config('MOCK_INTERVAL_MIN', cast=float)
MOCK_INTERVAL_MAX = config('MOCK_INTERVAL_MAX', cast=float)


producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

PLATFORMS = [Amazon]

def generate_event():
    """Gera um evento aleatório de uma plataforma aleatória"""
    platform = random.choice(PLATFORMS)
    event_type = random.choices(
        ['sale', 'stock_update', 'view'],
        weights=[14.5,0.5,85]
    )[0]

    if event_type == 'sale':
        event = platform.generate_sale_event()
    elif event_type == 'stock_update':
        event = platform.generate_stock_event()
    else:
        event = platform.generate_view_event()
    
    return event

def main():
    if not MOCK_AUTO_START:
        ...
    while True:
        try:
            event = generate_event()

            producer.send('ecommerce-events', event)

            time.sleep(random.uniform(MOCK_INTERVAL_MIN, MOCK_INTERVAL_MAX))

        except Exception as e:
            time.sleep(5)

if __name__ == '__main__':
    main()