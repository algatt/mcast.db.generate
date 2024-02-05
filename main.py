import pyodbc
from generator import Generator

def connect_to_db(server, db_name, autocommit = False):
    try:
        return pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={db_name};Trusted_Connection=yes;', autocommit=autocommit)
    except Exception as e:
        raise(e)

def generate_database(server, db_name):
    connection = connect_to_db(server, "", autocommit= True)
    cursor = connection.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM sys.databases WHERE name='{db_name}';")
    total_db = cursor.fetchone()[0]
    if total_db >0:
        choice = input(f"Database {db_name} already exists\nDelete it? (Y/n)?")
        if choice == 'Y':
            cursor.execute(f"DROP DATABASE {db_name};")
        else:
            print(f"Cannot proceed since database {db_name} already exists.")
            return

    with open('./db_script.sql', 'r') as file:
        sql_script = file.read()
        cursor.execute(f'CREATE DATABASE {db_name}')
        cursor.execute(f"USE {db_name}")
        cursor.execute(sql_script)
        cursor.close()
        print ("Tables Created")
    
    connection.close()

settings = {
    "account": {
        "total": 100,
        "start_date": "-5y",
        "end_date": "today"
    },
    "country": {
        "total" : 10
    },
    "city": {
        "min": 3,
        "max": 10
    },
    "profile" : {
        "fill_ratio" : 80,
        "prefix_ratio": 60,
        "postcode_ratio": 50 
    },
    "product": {},
    "order": {
        "fill_ratio": 80,
        "min": 1,
        "max": 30
    },
    "orderitem" :{
        "min_products" : 1,
        "max_products" : 30,
        "min_quantity": 1,
        "max_quantity": 10
    }

}

try:
    server = 'XMG'
    db_name = "supermarket_db"
    generate_database(server, db_name)

    db_connection = connect_to_db(server, db_name)
    
    generator = Generator(db_connection, settings)
    generator.generate_all_data()
except Exception as e:
    print (e)

