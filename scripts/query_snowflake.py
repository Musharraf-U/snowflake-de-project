import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from snowflake_connection import get_connection
import os

load_dotenv()

def fetch_query(query):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        df = pd.DataFrame(results, columns=columns)
        return df
    finally:
        cursor.close()
        conn.close()

def main():
    # 1. Row counts across all staging tables
    print("\n--- Staging Layer Row Counts ---")
    query = """
    SELECT 'STG_ORDERS'      AS table_name, COUNT(*) AS total_rows FROM DE_PROJECT.STAGING.STG_ORDERS      UNION ALL
    SELECT 'STG_CUSTOMERS',                  COUNT(*)               FROM DE_PROJECT.STAGING.STG_CUSTOMERS    UNION ALL
    SELECT 'STG_ORDER_ITEMS',                COUNT(*)               FROM DE_PROJECT.STAGING.STG_ORDER_ITEMS
    """
    df = fetch_query(query)
    print(df.to_string(index=False))

    # 2. Order status distribution
    print("\n--- Order Status Distribution ---")
    query = """
    SELECT order_status, COUNT(*) AS total_orders
    FROM DE_PROJECT.STAGING.STG_ORDERS
    GROUP BY order_status
    ORDER BY total_orders DESC
    """
    df = fetch_query(query)
    print(df.to_string(index=False))

    # 3. Late delivery summary
    print("\n--- Late Delivery Summary ---")
    query = """
    SELECT
      is_late_delivery,
      COUNT(*) AS total_orders,
      ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
    FROM DE_PROJECT.STAGING.STG_ORDERS
    WHERE order_status = 'delivered'
    GROUP BY is_late_delivery
    """
    df = fetch_query(query)
    print(df.to_string(index=False))

    # 4. Top 5 states by revenue
    print("\n--- Top 5 States by Revenue ---")
    query = """
    SELECT customer_state, total_orders, total_revenue
    FROM DE_PROJECT.ANALYTICS.VW_REVENUE_BY_STATE
    LIMIT 5
    """
    df = fetch_query(query)
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()