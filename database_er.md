
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
