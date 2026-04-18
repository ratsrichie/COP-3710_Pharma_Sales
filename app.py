import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import date

# =========================================
# CONFIG
# =========================================
DB_FILE = Path("student_app.db")
DATA_FOLDER = Path(r"C:\Users\richi\Downloads\Codes\DBMS\estevan\data_ese\ratsrichie COP-3710_Pharma_Sales main data")
SQL_FILE = Path("features.sql")

CSV_FILES = {
    "calendar_day": "calendar_day.csv",
    "manufacturers": "manufacturers.csv",
    "pharmacies": "pharmacies.csv",
    "products": "products.csv",
    "sales": "sales.csv",
}

# =========================================
# LOAD SQL FILE
# =========================================
def load_queries():
    queries = {}
    current_name = None
    current_query = []

    if not SQL_FILE.exists():
        st.error(f"Could not find SQL file: {SQL_FILE.resolve()}")
        return {}

    with open(SQL_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("-- name:"):
                if current_name:
                    queries[current_name] = "".join(current_query).strip()
                current_name = line.replace("-- name:", "").strip()
                current_query = []
            else:
                current_query.append(line)

        if current_name:
            queries[current_name] = "".join(current_query).strip()

    return queries

# =========================================
# DB CONNECTION
# =========================================
def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

# =========================================
# DATABASE SETUP
# =========================================
def create_tables(conn):
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS calendar_day (
            day_id INTEGER PRIMARY KEY,
            date_value TEXT,
            year_num INTEGER,
            month_num INTEGER,
            open_hours INTEGER,
            weekday_name TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS manufacturers (
            manufacturer_id INTEGER PRIMARY KEY,
            manufacturer_name TEXT,
            country TEXT,
            founded_year INTEGER
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS pharmacies (
            pharmacy_id INTEGER PRIMARY KEY,
            pharmacy_name TEXT,
            city TEXT,
            state_code TEXT,
            open_hour INTEGER,
            close_hour INTEGER
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            category_code TEXT,
            product_name TEXT,
            category_name TEXT,
            manufacturer_id INTEGER,
            dosage_form TEXT,
            unit_price REAL,
            FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(manufacturer_id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY,
            day_id INTEGER,
            pharmacy_id INTEGER,
            product_id INTEGER,
            volume_sold REAL,
            sales_amount REAL,
            FOREIGN KEY (day_id) REFERENCES calendar_day(day_id),
            FOREIGN KEY (pharmacy_id) REFERENCES pharmacies(pharmacy_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
        """
    )

    conn.commit()


def table_has_rows(conn, table_name):
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cur.fetchone()[0] > 0


def load_csv_to_table(conn, table_name, csv_path):
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, conn, if_exists="append", index=False)


def initialize_database():
    missing = [name for name, file_name in CSV_FILES.items() if not (DATA_FOLDER / file_name).exists()]
    if missing:
        st.error(
            "Missing CSV files in DATA_FOLDER: " + ", ".join(f"{name} -> {CSV_FILES[name]}" for name in missing)
        )
        st.stop()

    conn = get_connection()
    try:
        create_tables(conn)
        for table_name, file_name in CSV_FILES.items():
            if not table_has_rows(conn, table_name):
                load_csv_to_table(conn, table_name, DATA_FOLDER / file_name)
        conn.commit()
    finally:
        conn.close()

# =========================================
# QUERY HELPERS
# =========================================
def run_select(query, params=None):
    conn = None
    try:
        conn = get_connection()
        df = pd.read_sql_query(query, conn, params=params or {})
        return df
    except Exception as e:
        st.error(f"Query failed: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()


def run_action(query, params=None):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params or {})
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Action failed: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_lookup_df(query):
    return run_select(query)

# =========================================
# APP STARTUP
# =========================================
st.set_page_config(page_title="Pharma Sales Dashboard", layout="wide")
st.title("Pharma Sales Dashboard")
st.caption("Streamlit + pandas + SQLite using your local CSV files and features.sql")

initialize_database()
QUERIES = load_queries()

required_queries = [
    "total_sales_by_region",
    "total_sales_by_rep",
    "total_sales_by_drug",
    "sales_between_dates",
    "insert_sale",
    "running_total",
    "drug_ranking",
]

missing_queries = [q for q in required_queries if q not in QUERIES]
if missing_queries:
    st.error("Missing queries in features.sql: " + ", ".join(missing_queries))
    st.stop()

menu = st.sidebar.selectbox(
    "Choose feature",
    [
        "Sales by Region",
        "Sales by Rep",
        "Sales by Drug",
        "Sales Between Dates",
        "Running Total",
        "Drug Ranking",
        "Add Sale",
    ],
)

# =========================================
# FEATURES
# =========================================
if menu == "Sales by Region":
    st.subheader("Sales by Region")
    if st.button("Run region report"):
        df = run_select(QUERIES["total_sales_by_region"])
        st.dataframe(df, use_container_width=True)
        if not df.empty and "REGION" in df.columns:
            chart_df = df.set_index("REGION")[["TOTAL_SALES"]]
            st.bar_chart(chart_df)

elif menu == "Sales by Rep":
    st.subheader("Sales by Rep")
    if st.button("Run rep report"):
        df = run_select(QUERIES["total_sales_by_rep"])
        st.dataframe(df, use_container_width=True)
        if not df.empty and "SALES_REP" in df.columns:
            chart_df = df.set_index("SALES_REP")[["TOTAL_SALES"]]
            st.bar_chart(chart_df)

elif menu == "Sales by Drug":
    st.subheader("Sales by Drug")
    if st.button("Run product report"):
        df = run_select(QUERIES["total_sales_by_drug"])
        st.dataframe(df, use_container_width=True)
        if not df.empty and "DRUG" in df.columns:
            chart_df = df.set_index("DRUG")[["TOTAL_SALES"]]
            st.bar_chart(chart_df)

elif menu == "Sales Between Dates":
    st.subheader("Sales Between Dates")
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Start date", value=date(2014, 1, 1))
    with col2:
        end = st.date_input("End date", value=date(2014, 12, 31))

    if st.button("Search sales"):
        if start > end:
            st.error("Start date cannot be after end date.")
        else:
            df = run_select(
                QUERIES["sales_between_dates"],
                {"start_date": start.isoformat(), "end_date": end.isoformat()},
            )
            st.dataframe(df, use_container_width=True)
            st.write(f"Rows returned: {len(df)}")

elif menu == "Running Total":
    st.subheader("Running Total of Sales")
    if st.button("Run running total"):
        df = run_select(QUERIES["running_total"])
        if not df.empty:
            if "SALE_DATE" in df.columns:
                df["SALE_DATE"] = pd.to_datetime(df["SALE_DATE"])
            st.dataframe(df, use_container_width=True)
            if "SALE_DATE" in df.columns and "RUNNING_TOTAL" in df.columns:
                chart_df = df.set_index("SALE_DATE")[["RUNNING_TOTAL"]]
                st.line_chart(chart_df)
        else:
            st.warning("No data returned.")

elif menu == "Drug Ranking":
    st.subheader("Drug Ranking by Total Sales")
    if st.button("Run ranking"):
        df = run_select(QUERIES["drug_ranking"])
        st.dataframe(df, use_container_width=True)

elif menu == "Add Sale":
    st.subheader("Insert New Sale")
    st.write("Use existing IDs from your CSV data.")

    with st.expander("See sample valid IDs"):
        sample_products = run_select("SELECT product_id, product_name FROM products ORDER BY product_id LIMIT 10")
        sample_pharmacies = run_select("SELECT pharmacy_id, pharmacy_name, city FROM pharmacies ORDER BY pharmacy_id LIMIT 10")
        sample_days = run_select("SELECT day_id, date_value FROM calendar_day ORDER BY day_id LIMIT 10")
        st.write("Products")
        st.dataframe(sample_products, use_container_width=True)
        st.write("Pharmacies")
        st.dataframe(sample_pharmacies, use_container_width=True)
        st.write("Calendar days")
        st.dataframe(sample_days, use_container_width=True)

    product_id = int(st.number_input("Product ID", min_value=1, step=1))
    pharmacy_id = int(st.number_input("Pharmacy ID", min_value=1, step=1))
    day_id = int(st.number_input("Day ID", min_value=1, step=1))
    sales_amount = float(st.number_input("Sales amount", min_value=0.0, step=0.01))

    if st.button("Insert sale"):
        ok = run_action(
            QUERIES["insert_sale"],
            {
                "drug_id": product_id,
                "rep_id": 1,
                "region_id": pharmacy_id,
                "amount": sales_amount,
                "sale_date": day_id,
            },
        )
        if ok:
            st.success("Inserted successfully.")
            preview = run_select("SELECT * FROM sales ORDER BY sale_id DESC LIMIT 5")
            st.dataframe(preview, use_container_width=True)
