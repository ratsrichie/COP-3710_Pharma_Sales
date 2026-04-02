"""
preprocess.py

Reads the raw salesdaily.csv file and creates cleaned CSV files inside ./data
for the tables used by the project schema.

Generated files:
- data/manufacturers.csv
- data/pharmacies.csv
- data/products.csv
- data/calendar_day.csv
- data/sales.csv
"""

from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pandas as pd


SEED = 42
random.seed(SEED)
np.random.seed(SEED)

CATEGORY_MAP = {
    "M01AB": "Acetic acid derivatives and related substances",
    "M01AE": "Propionic acid derivatives",
    "N02BA": "Salicylic acid and derivatives",
    "N02BE": "Pyrazolones and anilides",
    "N05B": "Anxiolytics",
    "N05C": "Hypnotics and sedatives",
    "R03": "Drugs for obstructive airway diseases",
    "R06": "Systemic antihistamines",
}

BASE_PRICES = {
    "M01AB": 18.50,
    "M01AE": 16.75,
    "N02BA": 9.50,
    "N02BE": 11.25,
    "N05B": 22.40,
    "N05C": 24.10,
    "R03": 29.99,
    "R06": 14.80,
}

FORMS = ["Tablet", "Capsule", "Syrup", "Injection", "Inhaler", "Cream"]
CITIES = [
    "Orlando", "Tampa", "Miami", "Jacksonville", "Lakeland",
    "Brandon", "Kissimmee", "St. Petersburg", "Tallahassee", "Gainesville",
]
COUNTRIES = ["USA", "Canada", "Germany", "India", "Brazil", "Spain", "Ireland", "Switzerland"]


def build_manufacturers() -> pd.DataFrame:
    rows = []
    for i in range(1, 101):
        rows.append(
            {
                "manufacturer_id": i,
                "manufacturer_name": f"PharmaMaker_{i:03d}",
                "country": COUNTRIES[(i - 1) % len(COUNTRIES)],
                "founded_year": 1980 + ((i * 3) % 41),
            }
        )
    return pd.DataFrame(rows)


def build_pharmacies() -> pd.DataFrame:
    rows = []
    for i in range(1, 121):
        rows.append(
            {
                "pharmacy_id": i,
                "pharmacy_name": f"CommunityPharm_{i:03d}",
                "city": CITIES[(i - 1) % len(CITIES)],
                "state_code": "FL",
                "open_hour": 8 + (i % 4),
                "close_hour": 18 + (i % 4),
            }
        )
    return pd.DataFrame(rows)


def build_products() -> pd.DataFrame:
    rows = []
    product_id = 1
    for code, category_name in CATEGORY_MAP.items():
        for j in range(1, 21):
            rows.append(
                {
                    "product_id": product_id,
                    "category_code": code,
                    "product_name": f"{code}_Product_{j:02d}",
                    "category_name": category_name,
                    "manufacturer_id": ((product_id - 1) % 100) + 1,
                    "dosage_form": FORMS[(product_id - 1) % len(FORMS)],
                    "unit_price": round(BASE_PRICES[code] * (0.85 + 0.02 * (j % 8)), 2),
                }
            )
            product_id += 1
    return pd.DataFrame(rows)


def build_calendar(raw_df: pd.DataFrame) -> pd.DataFrame:
    calendar_df = (
        raw_df[["datum", "Year", "Month", "Hour", "Weekday Name"]]
        .drop_duplicates()
        .sort_values("datum")
        .copy()
    )
    calendar_df["day_id"] = range(1, len(calendar_df) + 1)
    calendar_df["date_value"] = calendar_df["datum"].dt.strftime("%Y-%m-%d")
    calendar_df = calendar_df[["day_id", "date_value", "Year", "Month", "Hour", "Weekday Name"]]
    calendar_df.columns = ["day_id", "date_value", "year_num", "month_num", "open_hours", "weekday_name"]
    return calendar_df


def build_sales(raw_df: pd.DataFrame, calendar_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
    long_df = raw_df.melt(
        id_vars=["datum", "Year", "Month", "Hour", "Weekday Name"],
        value_vars=list(CATEGORY_MAP.keys()),
        var_name="category_code",
        value_name="volume_sold",
    )
    long_df["volume_sold"] = long_df["volume_sold"].astype(float).round(2)
    long_df = long_df.merge(
        calendar_df[["day_id", "date_value"]],
        left_on=long_df["datum"].dt.strftime("%Y-%m-%d"),
        right_on="date_value",
        how="left",
    )
    long_df = long_df.drop(columns=["date_value"])

    products_by_category = {
        code: products_df.loc[products_df["category_code"] == code, "product_id"].tolist()
        for code in CATEGORY_MAP
    }

    sales_rows = []
    sale_id = 1

    for _, row in long_df.iterrows():
        total = round(float(row["volume_sold"]), 2)

        if total == 0:
            pieces = [0.0]
        else:
            parts = np.random.dirichlet(np.ones(3), 1)[0]
            pieces = [round(total * p, 2) for p in parts]
            diff = round(total - sum(pieces), 2)
            pieces[-1] = round(pieces[-1] + diff, 2)

        for piece in pieces:
            product_id = random.choice(products_by_category[row["category_code"]])
            pharmacy_id = random.randint(1, 120)
            unit_price = float(
                products_df.loc[products_df["product_id"] == product_id, "unit_price"].iloc[0]
            )

            sales_rows.append(
                {
                    "sale_id": sale_id,
                    "day_id": int(row["day_id"]),
                    "pharmacy_id": pharmacy_id,
                    "product_id": product_id,
                    "volume_sold": round(piece, 2),
                    "sales_amount": round(piece * unit_price, 2),
                }
            )
            sale_id += 1

    return pd.DataFrame(sales_rows)


def main() -> None:
    repo_root = Path(__file__).resolve().parent
    raw_path = repo_root / "salesdaily.csv"
    data_dir = repo_root / "data"
    data_dir.mkdir(exist_ok=True)

    raw_df = pd.read_csv(raw_path)
    raw_df["datum"] = pd.to_datetime(raw_df["datum"])

    manufacturers_df = build_manufacturers()
    pharmacies_df = build_pharmacies()
    products_df = build_products()
    calendar_df = build_calendar(raw_df)
    sales_df = build_sales(raw_df, calendar_df, products_df)

    manufacturers_df.to_csv(data_dir / "manufacturers.csv", index=False)
    pharmacies_df.to_csv(data_dir / "pharmacies.csv", index=False)
    products_df.to_csv(data_dir / "products.csv", index=False)
    calendar_df.to_csv(data_dir / "calendar_day.csv", index=False)
    sales_df.to_csv(data_dir / "sales.csv", index=False)

    print("Done. Clean CSV files were written to ./data")


if __name__ == "__main__":
    main()
