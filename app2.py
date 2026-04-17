import oracledb

# --- DATABASE CONNECTION ---
conn = oracledb.connect(
    user="YOUR_USERNAME",
    password="YOUR_PASSWORD",
    dsn="localhost/XEPDB1"  # adjust if needed
)

cursor = conn.cursor()


def menu():
    print("\n====== Pharma Sales System ======")
    print("1. Total Sales by Pharmacy")
    print("2. Sales by Product")
    print("3. Sales by Manufacturer")
    print("4. Sales in Date Range")
    print("5. Add New Sale")
    print("6. Exit")


while True:
    menu()
    choice = input("Enter choice: ")

    # -----------------------------------
    # Feature 1: Sales by Pharmacy (JOIN)
    # -----------------------------------
    if choice == "1":
        print("\n--- Sales by Pharmacy ---")
        query = """
        SELECT p.pharmacy_name, SUM(s.sales_amount)
        FROM sales s
        JOIN pharmacies p ON s.pharmacy_id = p.pharmacy_id
        GROUP BY p.pharmacy_name
        """
        cursor.execute(query)

        for row in cursor:
            print(f"Pharmacy: {row[0]} | Total Sales: ${row[1]:.2f}")


    # -----------------------------------
    # Feature 2: Sales by Product (JOIN)
    # -----------------------------------
    elif choice == "2":
        print("\n--- Sales by Product ---")
        query = """
        SELECT pr.product_name, SUM(s.sales_amount)
        FROM sales s
        JOIN products pr ON s.product_id = pr.product_id
        GROUP BY pr.product_name
        ORDER BY SUM(s.sales_amount) DESC
        """
        cursor.execute(query)

        for row in cursor:
            print(f"Product: {row[0]} | Total Sales: ${row[1]:.2f}")


    # -----------------------------------
    # Feature 3: Sales by Manufacturer (JOIN)
    # -----------------------------------
    elif choice == "3":
        print("\n--- Sales by Manufacturer ---")
        query = """
        SELECT m.manufacturer_name, SUM(s.sales_amount)
        FROM sales s
        JOIN products pr ON s.product_id = pr.product_id
        JOIN manufacturers m ON pr.manufacturer_id = m.manufacturer_id
        GROUP BY m.manufacturer_name
        ORDER BY SUM(s.sales_amount) DESC
        """
        cursor.execute(query)

        for row in cursor:
            print(f"Manufacturer: {row[0]} | Total Sales: ${row[1]:.2f}")


    # -----------------------------------
    # Feature 4: Sales by Date Range (JOIN)
    # -----------------------------------
    elif choice == "4":
        print("\n--- Sales by Date Range ---")
        start = input("Enter start date (YYYY-MM-DD): ")
        end = input("Enter end date (YYYY-MM-DD): ")

        query = """
        SELECT c.date_value, SUM(s.sales_amount)
        FROM sales s
        JOIN calendar_day c ON s.day_id = c.day_id
        WHERE c.date_value BETWEEN TO_DATE(:1, 'YYYY-MM-DD') 
                              AND TO_DATE(:2, 'YYYY-MM-DD')
        GROUP BY c.date_value
        ORDER BY c.date_value
        """
        cursor.execute(query, [start, end])

        for row in cursor:
            print(f"Date: {row[0]} | Total Sales: ${row[1]:.2f}")


    # -----------------------------------
    # Feature 5: Add New Sale
    # -----------------------------------
    elif choice == "5":
        print("\n--- Add New Sale ---")

        try:
            sale_id = int(input("Sale ID: "))
            day_id = int(input("Day ID: "))
            pharmacy_id = int(input("Pharmacy ID: "))
            product_id = int(input("Product ID: "))
            volume = float(input("Volume Sold: "))
            amount = float(input("Sales Amount: "))

            query = """
            INSERT INTO sales 
            (sale_id, day_id, pharmacy_id, product_id, volume_sold, sales_amount)
            VALUES (:1, :2, :3, :4, :5, :6)
            """

            cursor.execute(query, [sale_id, day_id, pharmacy_id, product_id, volume, amount])
            conn.commit()

            print("✅ Sale added successfully!")

        except Exception as e:
            print("❌ Error:", e)


    # -----------------------------------
    # Exit
    # -----------------------------------
    elif choice == "6":
        print("Exiting...")
        break

    else:
        print("Invalid option. Try again.")

# Close connection
cursor.close()
conn.close()