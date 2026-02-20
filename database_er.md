
<img width="580" height="660" alt="image" src="https://github.com/user-attachments/assets/3d189a1d-d4fa-42f3-b6de-56f8f40a91c1" />

# DrugCategory

- category_id (Primary Key)
- category_name (Mandatory)
- description (Optional)


# Time 
- Time
- time_id (PK)
- date (Mandatory)
- year
- month
- hour
- weekday_name


# SaleRecord
- sale_id (PK)
- category_id (FK)
- time_id (FK)
- sales_volume (Mandatory)

# Manufacturer
- manufacturer_id (PK)
- name
- contact_email (Optional)

# RegulatoryReport
- report_id (Partial key)
- sale_id (FK)
- report_status
