import oracledb
import os

def get_connection():
    # Credentials from your teammate's load_db.py
    user = os.getenv("DB_USER", "RTOMS9124_SCHEMA_MXWBQ")
    password = os.getenv("DB_PASS", "QI24VPH4VZ!3QNGMrSD75V4QDBC3VT")
    dsn = os.getenv("DB_DSN", "db.freesql.com:1521/23ai_34ui2")
    return oracledb.connect(user=user, password=password, dsn=dsn)

def main():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        while True:
            print("\n--- Pharma Sales Management UI ---")
            print("1. Total Sales by Pharmacy (JOIN)")
            print("2. Product & Manufacturer Catalog (JOIN)")
            print("3. Monthly Sales Volume (JOIN)")
            print("4. Search Products by Price")
            print("5. Lookup Pharmacy Hours")
            print("6. Exit")
            
            choice = input("\nSelect a feature (1-6): ")

            if choice == '1':
                cursor.execute("""SELECT ph.pharmacy_name, SUM(s.sales_amount) 
                                  FROM sales s JOIN pharmacies ph ON s.pharmacy_id = ph.pharmacy_id 
                                  GROUP BY ph.pharmacy_name""")
            elif choice == '2':
                cursor.execute("""SELECT p.product_name, m.manufacturer_name, p.unit_price 
                                  FROM products p JOIN manufacturers m ON p.manufacturer_id = m.manufacturer_id""")
            elif choice == '3':
                cursor.execute("""SELECT c.year_num, c.month_num, SUM(s.volume_sold) 
                                  FROM sales s JOIN calendar_day c ON s.day_id = c.day_id 
                                  GROUP BY c.year_num, c.month_num ORDER BY 1, 2""")
            elif choice == '4':
                price = input("Enter minimum unit price: ")
                cursor.execute("SELECT product_name, unit_price FROM products WHERE unit_price >= :1", [price])
            elif choice == '5':
                name = input("Enter pharmacy name: ")
                cursor.execute("SELECT pharmacy_name, open_hour, close_hour FROM pharmacies WHERE pharmacy_name LIKE :1", [f"%{name}%"])
            elif choice == '6':
                break
            else:
                print("Invalid choice.")
                continue

            results = cursor.fetchall()
            print("\n--- Results ---")
            for row in results:
                print(row)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

import oracledb
import os
import sys

def get_connection():
    # Credentials from your teammate's load_db.py
    user = os.getenv("DB_USER", "RTOMS9124_SCHEMA_MXWBQ")
    password = os.getenv("DB_PASS", "QI24VPH4VZ!3QNGMrSD75V4QDBC3VT")
    dsn = os.getenv("DB_DSN", "db.freesql.com:1521/23ai_34ui2")
    
    try:
        # PATH TO YOUR INSTANT CLIENT: Update this string to your actual folder path!
        lib_dir = r"C:\path\to\your\instantclient_19_8"
        
        # Initialize thick mode
        oracledb.init_oracle_client(lib_dir=lib_dir)
    except Exception as e:
        print(f"Thick mode initialization failed: {e}")
        # If it's already initialized or path is in environment, this might error; 
        # usually safe to continue if the libraries are in the system PATH.

    return oracledb.connect(user=user, password=password, dsn=dsn)

if __name__ == "__main__":
    main()