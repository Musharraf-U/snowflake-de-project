# Snowflake Data Engineering Project

End-to-end data pipeline built on Snowflake using the Olist Brazilian
E-Commerce dataset. Implements a medallion-style architecture:
RAW → STAGING → ANALYTICS.

---

## Project Objective

Build a production-grade data pipeline that takes raw e-commerce CSV data
and transforms it into clean, tested, analytics-ready business insights
using Snowflake, dbt, and SQL.

---

## Dataset

- **Source:** Olist Brazilian E-Commerce (Kaggle)
- **Tables:** Orders, Customers, Order Items
- **Volume:** ~99K orders | ~99K customers | ~112K order items
- **Domain:** Brazilian e-commerce transactions across multiple states

---

## Architecture
CSV Files
↓
RAW (DE_PROJECT.RAW)
→ Exact copy of source CSVs
→ No transformations applied
→ Loaded via COPY INTO from Snowflake internal stage
↓
STAGING (DE_PROJECT.STAGING)
→ Cleaned and standardised column names
→ Timestamps cast to DATE
→ Nulls filtered on critical columns
→ Derived business columns added
→ Managed entirely by dbt models
↓
ANALYTICS (DE_PROJECT.ANALYTICS)
→ Business-focused views
→ Joined across staging tables
→ Ready for reporting and dashboards

---

## Staging Layer — dbt Models

| Model | Source Table | Description |
|-------|-------------|-------------|
| stg_orders | RAW_ORDERS | Cleaned orders with date casting and business columns |
| stg_customers | RAW_CUSTOMERS | Standardised city and state fields |
| stg_order_items | RAW_ORDER_ITEMS | Price, freight, and derived amount fields |

### Derived Business Columns

**stg_orders**
| Column | Description |
|--------|-------------|
| order_month | Month extracted from order purchase timestamp |
| order_year | Year extracted from order purchase timestamp |
| days_to_deliver | Days between purchase date and delivery date |
| is_late_delivery | TRUE if delivered after estimated delivery date |

**stg_order_items**
| Column | Description |
|--------|-------------|
| total_amount | Price + freight value |
| shipping_cost_ratio | Freight as percentage of total amount |

---

## Analytics Layer — Views

| View | Description |
|------|-------------|
| VW_MONTHLY_SALES | Revenue and order count by month with MoM growth % |
| VW_TOP_PRODUCTS | Top 20 products ranked by total revenue |
| VW_REVENUE_BY_STATE | Revenue breakdown by Brazilian state |
| VW_TOP_CUSTOMERS | Top 50 customers ranked by total spending |
| VW_ORDER_TRENDS | Daily order volume split by delivery status |
| VW_DELIVERY_PERFORMANCE | Late vs on-time delivery % and avg days by state |

---

## Data Quality

- **15 dbt tests** across all 3 staging models
- Tests cover: uniqueness, not_null on all critical columns
- All 15 tests passing on every `dbt build`
- Additional manual checks: RAW vs STAGING row count validation, duplicate checks

---

## Snowflake Features Implemented

| Feature | Implementation |
|---------|---------------|
| Virtual Warehouse | DEV_WH — X-Small, auto-suspend 60s |
| Internal Stage | CSV_STAGE — used for COPY INTO loads |
| Tasks | LOAD_ORDERS_TASK — scheduled COPY INTO via cron |
| Streams | ORDERS_STREAM — APPEND_ONLY CDC on RAW_ORDERS |
| Time Travel | Used to recover deleted rows from RAW_ORDERS |
| Zero Copy Cloning | STAGING_DEV cloned from STAGING for safe testing |

---

## Project Structure
snowflake-de-project/
├── sql/
│   ├── 01_setup.sql          — warehouse, database, schema creation
│   ├── 02_create_tables.sql  — raw table DDL
│   └── 03_load_data.sql      — COPY INTO + stage setup
├── scripts/
│   └── upload_to_stage.sh    — CSV upload helper
├── de_project/               — dbt project
│   └── models/
│       └── staging/
│           ├── sources.yml
│           ├── schema.yml
│           ├── stg_orders.sql
│           ├── stg_customers.sql
│           └── stg_order_items.sql
└── README.md

---

## Stack

- **Snowflake** — Standard edition, AWS Mumbai (ap-south-1)
- **dbt-snowflake** — v1.11.4
- **Python** — v3.13
- **Git + GitHub** — version control and public portfolio

---

## How to Run

1. Run `sql/01_setup.sql` — creates warehouse, database, schemas
2. Upload CSVs to Snowflake internal stage via web UI
3. Run `sql/02_create_tables.sql` — creates RAW layer tables
4. Run `sql/03_load_data.sql` — loads data via COPY INTO
5. Activate virtual environment — `dbt-env\Scripts\activate`
6. Navigate to dbt project — `cd de_project`
7. Run `dbt build` — builds staging models and runs all 15 tests

---

## Next Phase

- Incremental dbt models
- Python + Snowflake integration
- Airflow orchestration
- AWS integration