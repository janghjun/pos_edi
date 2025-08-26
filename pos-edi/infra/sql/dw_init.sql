CREATE SCHEMA IF NOT EXISTS public;
CREATE TABLE IF NOT EXISTS dim_date (
  date_key       DATE PRIMARY KEY,
  y INT, m INT, d INT, dow INT, week INT
);
CREATE TABLE IF NOT EXISTS dim_store (
  store_id VARCHAR(20) PRIMARY KEY,
  store_name VARCHAR(100),
  region VARCHAR(50)
);
CREATE TABLE IF NOT EXISTS dim_supplier (
  supplier_id VARCHAR(20) PRIMARY KEY,
  supplier_name VARCHAR(100)
);
CREATE TABLE IF NOT EXISTS dim_product (
  sku VARCHAR(30) PRIMARY KEY,
  product_name VARCHAR(200),
  category VARCHAR(100),
  brand VARCHAR(100)
);
CREATE TABLE IF NOT EXISTS fact_sales (
  sale_id VARCHAR(40),
  date_key DATE,
  store_id VARCHAR(20),
  sku VARCHAR(30),
  qty INT,
  net_amount NUMERIC(14,2),
  PRIMARY KEY (sale_id, sku)
);
CREATE TABLE IF NOT EXISTS fact_po (
  po_no VARCHAR(40),
  date_key DATE,
  supplier_id VARCHAR(20),
  store_id VARCHAR(20),
  sku VARCHAR(30),
  order_qty INT,
  PRIMARY KEY (po_no, sku)
);
CREATE TABLE IF NOT EXISTS fact_inbound (
  asn_no VARCHAR(40),
  date_key DATE,
  store_id VARCHAR(20),
  sku VARCHAR(30),
  accept_qty INT,
  PRIMARY KEY (asn_no, sku)
);
