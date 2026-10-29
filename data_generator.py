import os
import random
import pandas as pd
from faker import Faker

fake = Faker('bg_BG')

CATEGORIES = ['Electronics', 'Home & Garden', 'Clothing', 'Books', 'Sports', 'Automotive']
PAYMENT_METHODS = ['Credit Card', 'Cash on Delivery', 'Bank Transfer', 'Digital Wallet']
CITIES = ['София', 'Пловдив', 'Варна', 'Бургас', 'Русе', 'Стара Загора', 'Велико Търново']

#Generate data
def generate_dataset(num_records: int = 150_000, output_path: str = "data/ecommerce_transactions.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"[*] Генериране на {num_records:,} транзакции с Faker...")

    records = []
    for i in range(1, num_records + 1):
        category = random.choice(CATEGORIES)
        qty = random.randint(1, 5)
        unit_price = round(random.uniform(10.0, 1200.0), 2)
        total_amount = round(qty * unit_price, 2)

        records.append({
            "transaction_id": i,
            "timestamp": fake.date_time_between(start_date="-1y", end_date="now").strftime("%Y-%m-%d %H:%M:%S"),
            "customer_name": fake.name(),
            "city": random.choice(CITIES),
            "category": category,
            "quantity": qty,
            "unit_price": unit_price,
            "total_amount": total_amount,
            "payment_method": random.choice(PAYMENT_METHODS)
        })

        if i % 50_000 == 0:
            print(f"    - Генерирани {i:,} записа...")

    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"[+] Данните са записани успешно във: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_dataset()
