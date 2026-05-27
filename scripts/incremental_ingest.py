import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from snowflake_connection import get_connection

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)
logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
STAGE    = "DE_PROJECT.RAW.CSV_STAGE"

FILES = {
    "olist_orders_dataset.csv":      "RAW_ORDERS",
    "olist_customers_dataset.csv":   "RAW_CUSTOMERS",
    "olist_order_items_dataset.csv": "RAW_ORDER_ITEMS"
}

TIMESTAMP_COLUMNS = {
    "RAW_ORDERS":      "order_purchase_timestamp",
    "RAW_CUSTOMERS":   None,
    "RAW_ORDER_ITEMS": "shipping_limit_date"
}


def get_watermark(cursor, table_name):
    cursor.execute(f"""
        SELECT last_loaded_at
        FROM DE_PROJECT.PIPELINE.LOAD_WATERMARK
        WHERE table_name = '{table_name}'
    """)
    result = cursor.fetchone()
    return result[0] if result else None


def update_watermark(cursor, table_name):
    cursor.execute(f"""
        UPDATE DE_PROJECT.PIPELINE.LOAD_WATERMARK
        SET last_loaded_at = CURRENT_TIMESTAMP,
            updated_at     = CURRENT_TIMESTAMP
        WHERE table_name = '{table_name}'
    """)
    logger.info(f"Watermark updated — {table_name}")


def write_audit(cursor, table_name, source_file, rows_loaded, status, error=None):
    error_msg = error.replace("'", "''") if error else None
    cursor.execute(f"""
        INSERT INTO DE_PROJECT.PIPELINE.LOAD_AUDIT
          (table_name, source_file, rows_loaded, load_status, error_message)
        VALUES
          ('{table_name}', '{source_file}', {rows_loaded},
           '{status}', {'NULL' if error_msg is None else f"'{error_msg}'"})
    """)
    logger.info(f"Audit record written — {table_name} | {status} | {rows_loaded} rows")


def upload_to_stage(cursor, file_path, file_name):
    logger.info(f"Uploading {file_name} to stage...")
    file_path_normalized = file_path.replace("\\", "/")
    cursor.execute(f"""
        PUT 'file://{file_path_normalized}'
        @{STAGE}
        AUTO_COMPRESS=TRUE
        OVERWRITE=TRUE
    """)
    logger.info(f"Upload complete — {file_name}")


def get_new_row_count(cursor, table_name, watermark, timestamp_col):
    if timestamp_col is None:
        cursor.execute(f"SELECT COUNT(*) FROM DE_PROJECT.RAW.{table_name}")
    else:
        cursor.execute(f"""
            SELECT COUNT(*)
            FROM DE_PROJECT.RAW.{table_name}
            WHERE {timestamp_col} > '{watermark}'
        """)
    return cursor.fetchone()[0]


def run_incremental_ingest():
    logger.info("Starting incremental ingestion pipeline...")
    conn   = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("USE WAREHOUSE DEV_WH")
        cursor.execute("USE DATABASE DE_PROJECT")
        cursor.execute("USE SCHEMA RAW")

        for file_name, table_name in FILES.items():
            file_path     = os.path.abspath(os.path.join(DATA_DIR, file_name))
            timestamp_col = TIMESTAMP_COLUMNS[table_name]

            if not os.path.exists(file_path):
                logger.warning(f"File not found — {file_path}. Skipping.")
                continue

            # Get watermark
            watermark = get_watermark(cursor, table_name)
            logger.info(f"Watermark for {table_name}: {watermark}")

            # Upload to stage
            upload_to_stage(cursor, file_path, file_name)

            # Copy into table
            logger.info(f"Loading {file_name} into {table_name}...")
            cursor.execute(f"""
                COPY INTO DE_PROJECT.RAW.{table_name}
                FROM @{STAGE}/{file_name}.gz
                ON_ERROR = 'CONTINUE'
            """)

            # Count new rows
            rows_loaded = get_new_row_count(
                cursor, table_name, watermark, timestamp_col
            )
            logger.info(f"New rows loaded — {table_name}: {rows_loaded}")

            # Write audit record
            write_audit(cursor, table_name, file_name, rows_loaded, "SUCCESS")

            # Update watermark
            update_watermark(cursor, table_name)

        logger.info("Incremental ingestion pipeline completed successfully.")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        write_audit(cursor, "UNKNOWN", "UNKNOWN", 0, "FAILED", str(e))
        raise

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    run_incremental_ingest()