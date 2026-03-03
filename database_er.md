
<img width="580" height="660" alt="image" src="https://github.com/user-attachments/assets/3d189a1d-d4fa-42f3-b6de-56f8f40a91c1" />

# DrugCategory (Strong Entity)

- category_id (Primary Key)
- category_name (Mandatory)
- description (Optional)

# Time (Strong Entity)
- Time
- time_id (PK)
- date (Mandatory)
- year
- month
- hour
- weekday_name
- 
# SaleRecord (Associative Entity)
- sale_id (PK)
- category_id (FK)
- time_id (FK)
- sales_volume (Mandatory)
- _Drug Category and time has M:M Relationship_

# Manufacturer (Strong Entity) 
- manufacturer_id (PK)
- name
- contact_email (Optional)
-  _Manufacturer and Drug Catagory has a 1:M Relationship_

# RegulatoryReport (Weak Entity)
- report_id (Partial key)
- sale_id (FK)
- report_status

# Users
- Data Analyst
- Regulatory Officer
- Sales Manager
- System Admin


### Relational Schema (Final Design)

There are 3 Relations for my Schema:

- DRUG_CATEGORY
- DATE
- SALES_FACT

### Functional Dependencies

All the dependencies I found were Nontrivial Functional Dependencies:

- Drug Category: drug_code → drug_name
    - Each drug code uniquely determines its drug name
- Date: date_id→ full_date, year, month, weekday_name, hour_value
    - Each date_id uniquely identifies a full date and all associated time attributes.
- Sales_fact: date_id,drug_code→ sale_volume
    - For a given date and drug category, there is exactly one sales value.

### BCNF Decomposition

- Drug Category: drug_code → drug_name
    - Already in BCNF
- Date: date_id→ full_date, year, month, weekday_name, hour_value
    - date_id is a candidate key
- Sales_Fact: (date_id, drug_code) → sales_volume
    - date_id and drug_code is a superkey

### Normalization

Originally, the CSV dataset was in a wide format:

SALES_DAILY_WIDE(full_date, M01AB, M01AE, N02BA, N02BE, N05B, N05C, R03, R06, year, month, weekday_name, hour_value)

In this format:

- Each drug category was stored as a separate column.
- Time attributes were repeated for every row.
- The design was not flexible if new drug categories were added.

To normalize the schema:

1. Drug categories were separated into DRUG_CATEGORY.
2. Date-related attributes were separated into DATE_DIM.
3. Sales data was converted into a fact table (SALES_FACT) with one row per date per drug.
