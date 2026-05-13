SELECT
  customer_id,
  customer_unique_id,
  UPPER(TRIM(customer_city))    AS customer_city,
  UPPER(TRIM(customer_state))   AS customer_state,
  customer_zip_code_prefix      AS zip_code
FROM {{ source('raw', 'RAW_CUSTOMERS') }}
WHERE customer_id IS NOT NULL