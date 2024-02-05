from faker import Faker
import uuid
from datetime import datetime, timedelta
import random
import csv

fake = Faker('en-GB')

def get_or_create_id(connection, table, id, column, value):
    cursor = connection.cursor()
    cursor.execute(f"SELECT {id} FROM {table} WHERE {column} = ?", value)
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute(f"INSERT INTO {table} ({column}) VALUES (?)", value)
        connection.commit()
        return cursor.execute(f"SELECT {id} FROM {table} WHERE {column} = ?", value).fetchone()[0]

def generate_accounts(connection, num_accounts = 100):
    cursor = connection.cursor()
    
    accounts = []
    generated_emails = set()
    while len(accounts) < num_accounts:
        account_id = str(uuid.uuid4())
        email = Faker().email()
        if email not in generated_emails:
            date_registered = Faker().date_between(start_date='-5y', end_date='today').strftime('%Y-%m-%d %H:%M:%S')
            accounts.append((account_id, email, date_registered))
            generated_emails.add(email)
    
    cursor.executemany('INSERT INTO Account (AccountID, Email, DateRegistered) VALUES (?, ?, ?)', accounts)
    connection.commit()
    cursor.close()
    return num_accounts

def generate_towns(connection, num_towns = 20):
    cursor = connection.cursor()
    towns = {fake.city() for _ in range(num_towns)}
    for town in towns:
        cursor.execute("IF NOT EXISTS (SELECT * FROM Town WHERE Town = ?) INSERT INTO Town (Town) VALUES (?)", town, town)
    connection.commit()
    cursor.close()
    return towns

def generate_profiles(connection, towns, percentage_to_fill):
    cursor = connection.cursor()

    cursor.execute(f"SELECT TOP {percentage_to_fill} PERCENT AccountID FROM Account ORDER BY NEWID()")
    accounts = cursor.fetchall()
    account_ids = [account[0] for account in accounts]

    profiles = []
    for account_id in account_ids:
        display_name = fake.name()
        house = fake.building_number()
        locality = fake.street_name()
        town = random.choice(list(towns)) 

        cursor.execute("SELECT TownID FROM Town WHERE Town = ?", town)
        town_id = cursor.fetchone()[0]

        profiles.append((display_name, house, locality, town_id, account_id))

    cursor.executemany("INSERT INTO Profile (DisplayName, House, Locality, TownID, AccountID) VALUES (?, ?, ?, ?, ?)", profiles)
    connection.commit()
    cursor.close()
    return len(profiles)

 
def generate_products(connection):
    cursor = connection.cursor()
    total_products = 0

    with open('products.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if (row['product_price']=='not availabe'):
                continue

            # Normalize data
            brand_id = get_or_create_id(connection, 'Brand', 'BrandID', 'Brand', row['product_company'].strip())
            category_id = get_or_create_id(connection, 'Category', 'CategoryID', 'Category', row['category'].strip())

            product_id = str(uuid.uuid4())

            cursor.execute(
                "INSERT INTO Product (ProductID, Barcode, Name, BrandID , CategoryID, Weight, Price) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    product_id, fake.ean13(), row['product_name'].strip(), brand_id, category_id, int(row['product_size'].split()[0].replace('g','')), row['product_price']
                )
            connection.commit()

            cursor.execute(
                "INSERT INTO Rating (ProductID, Overall, OneStar, TwoStar, ThreeStar, FourStar, FiveStar, ReviewsNumber, ProductQuality) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                product_id, row['product_rate'], row['one_star'], row['two_star'], row['three_star'], row['four_star'], row['five_star'], row['reviews_number'], row['product_quality']
            )
            connection.commit()
            total_products+=1
        cursor.close()
        return total_products


def generate_orders(connection, client_percentage = 90):
    cursor = connection.cursor()
  
    cursor.execute(f"SELECT TOP {client_percentage} PERCENT AccountID, DateRegistered FROM Account ORDER BY NEWID()")
    accounts = cursor.fetchall()

    total_orders = 0

    def generate_orders(account_id, date_registered):
        num_orders = random.randint(1, 30)  # Random number of orders (1 to 30)
        orders = []
        for _ in range(num_orders):
            # Order date must be after date registered and not more than 5 years ago
            start_date = max(date_registered, datetime.now() - timedelta(days=5*365))
            order_date = fake.date_time_between_dates(datetime_start=start_date, datetime_end=datetime.now())
            orders.append((account_id, order_date))
        return orders

    # Generate and insert orders for each account
    for account_id, date_registered in accounts:
        orders = generate_orders(account_id, date_registered)
        total_orders += len(orders)
        cursor.executemany("INSERT INTO Orders (AccountID, OrderDate) VALUES (?, ?)", orders)
        connection.commit()
    cursor.close()
    return total_orders


def generate_order_items(connection):
    cursor = connection.cursor()
  
    # Fetch all OrderIDs
    cursor.execute("SELECT OrderID FROM Orders")
    orders = [row[0] for row in cursor.fetchall()]

    # Fetch all ProductIDs
    cursor.execute("SELECT ProductID FROM Product")
    products = [row[0] for row in cursor.fetchall()]

    total_order_items = 0

    # Function to generate order items for an order
    def generate_order_items(order_id, products):
        num_products = random.randint(1, 30)  # Random number of unique products
        selected_products = random.sample(products, num_products)
        order_items = [(order_id, product_id, random.randint(1, 5)) for product_id in selected_products]  # Random quantity for each product
        return order_items

    # Generate and insert order items for each order
    for order_id in orders:
        order_items = generate_order_items(order_id, products)
        total_order_items += len(order_items)
        cursor.executemany("INSERT INTO OrderItem (OrderID, ProductID, Quantity) VALUES (?, ?, ?)", order_items)
        connection.commit()
    cursor.close()
    return total_order_items
