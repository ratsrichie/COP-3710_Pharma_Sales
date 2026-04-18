-- Adapted to the uploaded CSV schema:
--   sales(sale_id, day_id, pharmacy_id, product_id, volume_sold, sales_amount)
--   products(product_id, category_code, product_name, category_name, manufacturer_id, dosage_form, unit_price)
--   pharmacies(pharmacy_id, pharmacy_name, city, state_code, open_hour, close_hour)
--   manufacturers(manufacturer_id, manufacturer_name, country, founded_year)
--   calendar_day(day_id, date_value, year_num, month_num, open_hours, weekday_name)
--
-- Notes:
-- 1) There is no region table in the uploaded data, so REGION is mapped to pharmacy city.
-- 2) There is no sales_rep table in the uploaded data, so the "rep" feature is mapped to manufacturer.
-- 3) There is no drugs table in the uploaded data, so DRUG is mapped to product_name.
-- 4) sale_date is stored via calendar_day.date_value and is joined through sales.day_id.
-- 5) amount is stored as sales.sales_amount.

-- name: total_sales_by_region
SELECT
    p.city AS REGION,
    SUM(s.sales_amount) AS TOTAL_SALES
FROM sales s
JOIN pharmacies p ON s.pharmacy_id = p.pharmacy_id
GROUP BY p.city
ORDER BY TOTAL_SALES DESC;

-- name: total_sales_by_rep
SELECT
    m.manufacturer_name AS SALES_REP,
    SUM(s.sales_amount) AS TOTAL_SALES
FROM sales s
JOIN products pr ON s.product_id = pr.product_id
JOIN manufacturers m ON pr.manufacturer_id = m.manufacturer_id
GROUP BY m.manufacturer_name
ORDER BY TOTAL_SALES DESC;

-- name: total_sales_by_drug
SELECT
    pr.product_name AS DRUG,
    SUM(s.sales_amount) AS TOTAL_SALES
FROM sales s
JOIN products pr ON s.product_id = pr.product_id
GROUP BY pr.product_name
ORDER BY TOTAL_SALES DESC;

-- name: sales_between_dates
SELECT
    s.sale_id AS SALE_ID,
    pr.product_name AS DRUG_NAME,
    m.manufacturer_name AS REP_NAME,
    p.city AS REGION_NAME,
    s.sales_amount AS AMOUNT,
    c.date_value AS SALE_DATE
FROM sales s
JOIN products pr ON s.product_id = pr.product_id
JOIN manufacturers m ON pr.manufacturer_id = m.manufacturer_id
JOIN pharmacies p ON s.pharmacy_id = p.pharmacy_id
JOIN calendar_day c ON s.day_id = c.day_id
WHERE c.date_value BETWEEN :start_date AND :end_date
ORDER BY c.date_value, s.sale_id;

-- name: insert_sale
INSERT INTO sales (
    day_id,
    pharmacy_id,
    product_id,
    volume_sold,
    sales_amount
)
VALUES (
    :day_id,
    :pharmacy_id,
    :product_id,
    :volume_sold,
    :sales_amount
);

-- name: running_total
SELECT
    s.sale_id AS SALE_ID,
    c.date_value AS SALE_DATE,
    s.sales_amount AS AMOUNT,
    SUM(s.sales_amount) OVER (ORDER BY c.date_value, s.sale_id) AS RUNNING_TOTAL
FROM sales s
JOIN calendar_day c ON s.day_id = c.day_id
ORDER BY c.date_value, s.sale_id;

-- name: drug_ranking
SELECT
    DRUG,
    TOTAL_SALES,
    RANK() OVER (ORDER BY TOTAL_SALES DESC) AS SALES_RANK
FROM (
    SELECT
        pr.product_name AS DRUG,
        SUM(s.sales_amount) AS TOTAL_SALES
    FROM sales s
    JOIN products pr ON s.product_id = pr.product_id
    GROUP BY pr.product_name
);
