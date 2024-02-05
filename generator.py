from faker import Faker
import uuid
import random
from datetime import date, datetime, timedelta
import csv

class Generator:

    def __init__(self, connection, settings):
        self.connection = connection
        self.settings = settings
       
    def get_or_create_id(self, table, id, column, value):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT {id} FROM {table} WHERE {column} = ?", value)
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            cursor.execute(f"INSERT INTO {table} ({column}) VALUES (?)", value)
            self.connection.commit()
            return cursor.execute(f"SELECT {id} FROM {table} WHERE {column} = ?", value).fetchone()[0]
        
    def generate_accounts(self):
        account_settings = self.settings["account"]

        cursor = self.connection.cursor()

        accounts = []
        generated_emails = set()
        while len(accounts) < account_settings["total"]:
            account_id = str(uuid.uuid4())
            email = Faker().email()
            if email not in generated_emails:
                date_registered = Faker().date_between(start_date=account_settings["start_date"], end_date=account_settings["end_date"]).strftime('%Y-%m-%d %H:%M:%S')
                accounts.append((account_id, email, date_registered))
                generated_emails.add(email)

        cursor.executemany('INSERT INTO Account (AccountID, Email, DateRegistered) VALUES (?, ?, ?)', accounts)
        self.connection.commit()
        cursor.close()
        return len(accounts)
    
    def generate_countries(self):
        country_settings = self.settings["country"]

        cursor = self.connection.cursor()
        
        countries = {Faker().country() for _ in range(country_settings["total"])}
        for country in countries:
            cursor.execute("IF NOT EXISTS (SELECT * FROM Country WHERE Country = ?) INSERT INTO Country (Country) VALUES (?)", country, country)
            self.connection.commit()
        cursor.close()
        return len(countries)
    
    def generate_cities(self):
        city_settings = self.settings["city"]

        cursor = self.connection.cursor()

        countries = cursor.execute("SELECT CountryID from Country")
        countries = countries.fetchall()
        cursor.commit()
        total_cities = 0

        for countryId in countries:
            num_cities = random.randint(city_settings["min"], city_settings["max"])
            total_cities += num_cities
            cities = {Faker().city() for _ in range(num_cities)}
            for city in cities:
                cursor.execute("IF NOT EXISTS (SELECT * FROM City WHERE City = ? AND CountryID = ?) INSERT INTO City (City, CountryID) VALUES (?, ?)", city, countryId[0], city, countryId[0])
                cursor.commit()
        cursor.close()
        return total_cities
    
    def generate_profiles(self):
        profile_settings = self.settings["profile"]

        cursor = self.connection.cursor()     

        cursor.execute(f"SELECT TOP {profile_settings['fill_ratio']} PERCENT AccountID FROM Account ORDER BY NEWID()")
        accounts = cursor.fetchall()
        account_ids = [account[0] for account in accounts]

        cursor.execute(f"SELECT CityID FROM City")
        cities = cursor.fetchall()
        city_ids = [city[0] for city in cities]
        

        profiles = []
        for account_id in account_ids:
            date_of_birth = Faker().date_between(date(1970, 1, 1), date(2005, 12, 31))
            prefix = None
            if random.randint(1, 100) < profile_settings["prefix_ratio"]: 
                prefix = Faker().prefix()
            first_name = Faker().first_name()
            last_name = Faker().last_name()
            street_address = Faker().address()
            post_code = None
            if random.randint(1, 100) < profile_settings["postcode_ratio"]: 
                post_code = Faker().postcode()
            city_id = random.choice(list(city_ids))       

            profiles.append((date_of_birth, prefix, first_name, last_name, street_address, post_code, city_id, account_id))

        cursor.executemany("INSERT INTO Profile (DateOfBirth, Prefix, FirstName, LastName, StreetAddress, PostCode, CityID, AccountID) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",  profiles)
        cursor.commit()
        cursor.close()
        return len(profiles)
    
    def generate_products(self):
        product_settings = self.settings["product"]
        cursor = self.connection.cursor()
        total_products = 0

        with open('products.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if (row['product_price']=='not availabe'):
                    continue

                # Normalize data
                brand_id = self.get_or_create_id('Brand', 'BrandID', 'Brand', row['product_company'].strip())
                category_id = self.get_or_create_id('Category', 'CategoryID', 'Category', row['category'].strip())

                product_id = str(uuid.uuid4())

                cursor.execute(
                    "INSERT INTO Product (ProductID, Barcode, Name, BrandID , CategoryID, Weight, Price) VALUES(?, ?, ?, ?, ?, ?, ?)",
                    product_id, Faker().ean13(), row['product_name'].strip(), brand_id, category_id, int(row['product_size'].split()[0].replace('g','')), row['product_price']
                )
                cursor.commit()

                cursor.execute(
                    "INSERT INTO Rating (ProductID, Overall, OneStar, TwoStar, ThreeStar, FourStar, FiveStar, ReviewsNumber, ProductQuality) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    product_id, row['product_rate'], row['one_star'], row['two_star'], row['three_star'], row['four_star'], row['five_star'], row['reviews_number'], row['product_quality']
                )
                cursor.commit()
                total_products+=1
        cursor.close()
        return total_products

    def generate_orders(self):
        order_settings = self.settings["order"]
        cursor = self.connection.cursor()
    
        cursor.execute(f"SELECT TOP {order_settings['fill_ratio']} PERCENT AccountID, DateRegistered FROM Account ORDER BY NEWID()")
        accounts = cursor.fetchall()

        total_orders = 0

        def generate_orders(account_id, date_registered):
            num_orders = random.randint(order_settings['min'], order_settings['max'])
            orders = []
            for _ in range(num_orders):
                # Order date must be after date registered and not more than 5 years ago
                start_date = max(date_registered, datetime.now() - timedelta(days=5*365))
                order_date = Faker().date_time_between_dates(datetime_start=start_date, datetime_end=datetime.now())
                orders.append((account_id, order_date))
            return orders

        # Generate and insert orders for each account
        for account_id, date_registered in accounts:
            orders = generate_orders(account_id, date_registered)
            total_orders += len(orders)
            cursor.executemany("INSERT INTO Orders (AccountID, OrderDate) VALUES (?, ?)", orders)
            cursor.commit()
        cursor.close()
        return total_orders
    
    def generate_order_items(self):
        orderitem_settings = self.settings["orderitem"]
        cursor = self.connection.cursor()
  
        cursor.execute("SELECT OrderID FROM Orders")
        orders = [row[0] for row in cursor.fetchall()]
   
        cursor.execute("SELECT ProductID FROM Product")
        products = [row[0] for row in cursor.fetchall()]

        total_order_items = 0

        # Function to generate order items for an order
        def generate_order_items(order_id, products):
            num_products = random.randint(orderitem_settings["min_products"], orderitem_settings["max_products"])
            selected_products = random.sample(products, num_products)
            order_items = [(order_id, product_id, random.randint(orderitem_settings["min_quantity"], orderitem_settings["max_quantity"])) for product_id in selected_products]
            return order_items

        # Generate and insert order items for each order
        for order_id in orders:
            order_items = generate_order_items(order_id, products)
            total_order_items += len(order_items)
            cursor.executemany("INSERT INTO OrderItem (OrderID, ProductID, Quantity) VALUES (?, ?, ?)", order_items)
            cursor.commit()
        cursor.close()
        return total_order_items

    def generate_all_data(self):
        print (f"{self.generate_accounts()} accounts generated")
        print (f"{self.generate_countries()} countries generated")
        print (f"{self.generate_cities()} cities generated")
        print (f"{self.generate_profiles()} profiles generated")
        print (f"{self.generate_products()} products generated (along with brand and categories)")
        print (f"{self.generate_orders()} orders generated")
        print (f"{self.generate_order_items()} order items generated")

     
        