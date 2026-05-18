SELECT
  order_id,
  customer_id,
  LOWER(TRIM(order_status))                               AS order_status,
  order_purchase_timestamp::DATE                          AS order_purchase_date,
  order_approved_at::DATE                                 AS order_approved_date,
  order_delivered_customer_date::DATE                     AS order_delivered_date,
  order_estimated_delivery_date::DATE                     AS order_estimated_delivery_date,
  DATE_PART('month', order_purchase_timestamp)            AS order_month,
  DATE_PART('year', order_purchase_timestamp)             AS order_year,
  DATEDIFF('day',
    order_purchase_timestamp,
    order_delivered_customer_date)                        AS days_to_deliver,
  CASE
    WHEN order_delivered_customer_date > order_estimated_delivery_date
    THEN TRUE
    ELSE FALSE
  END                                                     AS is_late_delivery
FROM {{ source('raw', 'RAW_ORDERS') }}
WHERE order_id IS NOT NULL