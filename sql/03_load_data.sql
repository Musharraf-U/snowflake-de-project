USE DATABASE DE_PROJECT;
USE SCHEMA RAW;
USE WAREHOUSE DEV_WH;

-- Create an internal stage
CREATE OR REPLACE STAGE DE_PROJECT.RAW.CSV_STAGE
  FILE_FORMAT = (
    TYPE = 'CSV'
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    SKIP_HEADER = 1
    NULL_IF = ('NULL', 'null', '')
    EMPTY_FIELD_AS_NULL = TRUE
    DATE_FORMAT = 'AUTO'
    TIMESTAMP_FORMAT = 'AUTO'
  );

LIST @CSV_STAGE;

-- Load orders
COPY INTO RAW_ORDERS
FROM @CSV_STAGE/olist_orders_dataset.csv
ON_ERROR = 'CONTINUE';

-- Load customers
COPY INTO RAW_CUSTOMERS
FROM @CSV_STAGE/olist_customers_dataset.csv
ON_ERROR = 'CONTINUE';

-- Load order items
COPY INTO RAW_ORDER_ITEMS
FROM @CSV_STAGE/olist_order_items_dataset.csv
ON_ERROR = 'CONTINUE';

-- Verify
SELECT 'orders'      AS table_name, COUNT(*) AS total_rows FROM RAW_ORDERS      UNION ALL
SELECT 'customers',                  COUNT(*)               FROM RAW_CUSTOMERS    UNION ALL
SELECT 'order_items',                COUNT(*)               FROM RAW_ORDER_ITEMS;