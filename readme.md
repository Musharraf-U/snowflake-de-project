# Snowflake Data Engineering Project

End-to-end data pipeline built on Snowflake using the Olist Brazilian
E-Commerce dataset. Implements a medallion-style architecture:
RAW → STAGING → ANALYTICS.

## Dataset
- Source: Olist Brazilian E-Commerce (Kaggle)
- Tables: Orders, Customers, Order Items
- Volume: ~99K orders | ~99K customers | ~112K order items

## Architecture

CSV Files
   ↓
RAW (DE_PROJECT.RAW)
   → Exact copy of source CSVs
   → No transformations
   → Loaded via COPY INTO from internal stage
   ↓
STAGING (DE_PROJECT.STAGING)
   → Cleaned column names
   → Timestamps cast to DATE
   → Nulls filtered
   → Derived columns: days_to_deliver, total_amount
   ↓
ANALYTICS (DE_PROJECT.ANALYTICS)
   → Business-focused views
   → Joined across staging tables
   → Ready for reporting

## Analytics Views
| View | Description |
|------|-------------|
| VW_MONTHLY_SALES | Revenue and orders by month with MoM growth % |
| VW_TOP_PRODUCTS | Top 20 products by revenue |
| VW_REVENUE_BY_STATE | Revenue breakdown by Brazilian state |
| VW_TOP_CUSTOMERS | Top 50 customers by total spending |
| VW_ORDER_TRENDS | Daily order volume by status |

## dbt Models
| Model | Description |
|-------|-------------|
| stg_orders | Cleaned orders with date casting and days_to_deliver |
| stg_customers | Standardised city and state fields |
| stg_order_items | Price, freight, and total_amount fields |

## Tests
- 11 dbt tests across all staging models
- Covers uniqueness, not_null on all critical columns

## Project Structure
- `/sql` — DDL and load scripts
- `/scripts` — upload helper
- `/de_project` — dbt project with models and tests
- `README.md` — this file

## Stack
- Snowflake (Standard, AWS Mumbai)
- dbt-snowflake 1.11.4
- Python 3.13
- Next phase: GitHub Actions + incremental loads