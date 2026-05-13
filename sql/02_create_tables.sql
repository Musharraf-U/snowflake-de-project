USE DATABASE DE_PROJECT;
USE SCHEMA RAW;

-- Raw orders table (matches Olist orders.csv)
CREATE OR REPLACE TABLE RAW_ORDERS (
  order_id              VARCHAR,
  customer_id           VARCHAR,
  order_status          VARCHAR,
  order_purchase_timestamp  TIMESTAMP_NTZ,
  order_approved_at         TIMESTAMP_NTZ,
  order_delivered_carrier_date  TIMESTAMP_NTZ,
  order_delivered_customer_date TIMESTAMP_NTZ,
  order_estimated_delivery_date TIMESTAMP_NTZ
);

-- Raw customers table
CREATE OR REPLACE TABLE RAW_CUSTOMERS (
  customer_id               VARCHAR,
  customer_unique_id        VARCHAR,
  customer_zip_code_prefix  VARCHAR,
  customer_city             VARCHAR,
  customer_state            VARCHAR
);

-- Raw order items table
CREATE OR REPLACE TABLE RAW_ORDER_ITEMS (
  order_id            VARCHAR,
  order_item_id       INT,
  product_id          VARCHAR,
  seller_id           VARCHAR,
  shipping_limit_date TIMESTAMP_NTZ,
  price               NUMBER(10,2),
  freight_value       NUMBER(10,2)
);