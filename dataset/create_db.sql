
--schema for the COP 3710 pharma sales project

BEGIN EXECUTE IMMEDIATE 'DROP TABLE sales CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE products CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE pharmacies CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE manufacturers CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE calendar_day CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/

CREATE TABLE manufacturers (
    manufacturer_id   NUMBER PRIMARY KEY,
    manufacturer_name VARCHAR2(100) NOT NULL UNIQUE,
    country           VARCHAR2(50) NOT NULL,
    founded_year      NUMBER(4) NOT NULL,
    CONSTRAINT chk_manufacturer_year CHECK (founded_year BETWEEN 1900 AND 2030)
);

CREATE TABLE pharmacies (
    pharmacy_id    NUMBER PRIMARY KEY,
    pharmacy_name  VARCHAR2(100) NOT NULL UNIQUE,
    city           VARCHAR2(60) NOT NULL,
    state_code     VARCHAR2(2) NOT NULL,
    open_hour      NUMBER(2) NOT NULL,
    close_hour     NUMBER(2) NOT NULL,
    CONSTRAINT chk_open_hour  CHECK (open_hour BETWEEN 0 AND 23),
    CONSTRAINT chk_close_hour CHECK (close_hour BETWEEN 0 AND 23),
    CONSTRAINT chk_hours_order CHECK (close_hour > open_hour)
);

CREATE TABLE calendar_day (
    day_id        NUMBER PRIMARY KEY,
    date_value    DATE NOT NULL UNIQUE,
    year_num      NUMBER(4) NOT NULL,
    month_num     NUMBER(2) NOT NULL,
    open_hours    NUMBER(4) NOT NULL,
    weekday_name  VARCHAR2(20) NOT NULL,
    CONSTRAINT chk_month_num CHECK (month_num BETWEEN 1 AND 12),
    CONSTRAINT chk_open_hours CHECK (open_hours >= 0)
);

CREATE TABLE products (
    product_id        NUMBER PRIMARY KEY,
    category_code     VARCHAR2(10) NOT NULL,
    product_name      VARCHAR2(100) NOT NULL UNIQUE,
    category_name     VARCHAR2(150) NOT NULL,
    manufacturer_id   NUMBER NOT NULL,
    dosage_form       VARCHAR2(30) NOT NULL,
    unit_price        NUMBER(10,2) NOT NULL,
    CONSTRAINT fk_product_manufacturer FOREIGN KEY (manufacturer_id)
        REFERENCES manufacturers(manufacturer_id),
    CONSTRAINT chk_unit_price CHECK (unit_price >= 0)
);

CREATE TABLE sales (
    sale_id       NUMBER PRIMARY KEY,
    day_id        NUMBER NOT NULL,
    pharmacy_id   NUMBER NOT NULL,
    product_id    NUMBER NOT NULL,
    volume_sold   NUMBER(12,2) NOT NULL,
    sales_amount  NUMBER(12,2) NOT NULL,
    CONSTRAINT fk_sales_day FOREIGN KEY (day_id)
        REFERENCES calendar_day(day_id),
    CONSTRAINT fk_sales_pharmacy FOREIGN KEY (pharmacy_id)
        REFERENCES pharmacies(pharmacy_id),
    CONSTRAINT fk_sales_product FOREIGN KEY (product_id)
        REFERENCES products(product_id),
    CONSTRAINT chk_volume_sold CHECK (volume_sold >= 0),
    CONSTRAINT chk_sales_amount CHECK (sales_amount >= 0)
);

CREATE INDEX idx_sales_day ON sales(day_id);
CREATE INDEX idx_sales_pharmacy ON sales(pharmacy_id);
CREATE INDEX idx_sales_product ON sales(product_id);
CREATE INDEX idx_products_category ON products(category_code);
