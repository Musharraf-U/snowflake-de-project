SELECT
  order_id,
  order_item_id,
  product_id,
  seller_id,
  price,
  freight_value,
  ROUND(price + freight_value, 2)                         AS total_amount,
  ROUND(freight_value / NULLIF(price + freight_value, 0) * 100, 2) AS shipping_cost_ratio,
  shipping_limit_date::DATE                               AS shipping_limit_date
FROM {{ source('raw', 'RAW_ORDER_ITEMS') }}
WHERE order_id IS NOT NULL