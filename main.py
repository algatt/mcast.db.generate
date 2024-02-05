import pyodbc
import generator

SERVER = "XMG"
db_connection = None

def connect_to_db(db_name, autocommit = False):
    try:
        return pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={db_name};Trusted_Connection=yes;', autocommit=autocommit)
    except Exception as e:
        raise(e)

def generate_database(db_name):
    connection = connect_to_db("", autocommit= True)
    cursor = connection.cursor()
    with open('./db_script.sql', 'r') as file:
        sql_script = file.read()
        cursor.execute(f'CREATE DATABASE {db_name}')
        cursor.execute(f"USE {db_name}")
        cursor.execute(sql_script)
        cursor.close()
        connection.close()

try:
    db_name = "supermarket_db"

    generate_database(db_name)
    db_connection = connect_to_db(db_name)

    accounts = generator.generate_accounts(db_connection, 100)
    print (f"{accounts} accounts generated")

    towns = generator.generate_towns(db_connection)
    print(f"{len(towns)} towns generated")

    profiles = generator.generate_profiles(db_connection, towns, 85)
    print(f"{profiles} profiles generated")
 
    products = generator.generate_products(db_connection)
    print(f"{products} products generated with their respective brands and categories")

    orders = generator.generate_orders(db_connection, 90)
    print(f"{orders} orders generated")
 
    order_items = generator.generate_order_items(db_connection)
    print(f"{order_items} line orders generated")

    db_connection.close()
    
except Exception as e:
    print (e)

