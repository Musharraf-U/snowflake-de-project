import os
import logging
from dotenv import load_dotenv
from snowflake_connection import get_connection

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)
logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

FILES = {
    "olist_orders_dataset.csv":      "RAW_ORDERS",
    "olist_customers_dataset.csv":   "RAW_CUSTOMERS",
    "olist_order_items_dataset.csv": "RAW_ORDER_ITEMS"
}

STAGE = "DE_PROJECT.RAW.CSV_STAGE"


def upload_to_stage(cursor, file_path, file_name):
    logger.info(f"Uploading {file_name} to stage...")
    # Normalize path — forward slashes + wrap in quotes for spaces
    file_path_normalized = file_path.replace("\\", "/")
    put_command = f"""
        PUT 'file://{file_path_normalized}'
        @{STAGE}
        AUTO_COMPRESS=TRUE
        OVERWRITE=TRUE
    """
    cursor.execute(put_command)
    logger.info(f"Upload complete — {file_name}")


def copy_into_table(cursor, table_name, file_name):
    logger.info(f"Loading {file_name} into {table_name}...")
    copy_command = f"""
        COPY INTO DE_PROJECT.RAW.{table_name}
        FROM @{STAGE}/{file_name}.gz
        ON_ERROR = 'CONTINUE'
    """
    cursor.execute(copy_command)
    results = cursor.fetchall()
    for row in results:
        logger.info(f"Load result — {row}")


def get_row_count(cursor, table_name):
    cursor.execute(f"SELECT COUNT(*) FROM DE_PROJECT.RAW.{table_name}")
    count = cursor.fetchone()[0]
    return count


def run_ingestion():
    logger.info("Starting ingestion pipeline...")
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("USE WAREHOUSE DEV_WH")
        cursor.execute("USE DATABASE DE_PROJECT")
        cursor.execute("USE SCHEMA RAW")

        for file_name, table_name in FILES.items():
            file_path = os.path.abspath(os.path.join(DATA_DIR, file_name))

            if not os.path.exists(file_path):
                logger.warning(f"File not found — {file_path}. Skipping.")
                continue

            # Upload to stage
            upload_to_stage(cursor, file_path, file_name)

            # Copy into table
            copy_into_table(cursor, table_name, file_name)

            # Row count check
            count = get_row_count(cursor, table_name)
            logger.info(f"Row count after load — {table_name}: {count}")

        logger.info("Ingestion pipeline completed successfully.")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    run_ingestion()