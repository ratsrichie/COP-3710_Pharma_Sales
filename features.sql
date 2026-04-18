SELECT r.region_name, SUM(s.amount) AS total_sales
FROM sales s
JOIN region r ON s.region_id = r.region_id
GROUP BY r.region_name;

SELECT rep.rep_name, SUM(s.amount) AS total_sales
FROM sales s
JOIN sales_rep rep ON s.rep_id = rep.rep_id
GROUP BY rep.rep_name;

SELECT d.drug_name, SUM(s.amount) AS total_sales
FROM sales s
JOIN drugs d ON s.drug_id = d.drug_id
GROUP BY d.drug_name
ORDER BY total_sales DESC;

SELECT * 
FROM sales
WHERE sale_date BETWEEN ? AND ?;

INSERT INTO sales (drug_id, rep_id, region_id, amount, sale_date)
VALUES (?, ?, ?, ?, ?);