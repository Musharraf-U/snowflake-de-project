#!/bin/bash
# Upload CSVs to Snowflake internal stage
# Usage: bash scripts/upload_to_stage.sh

ACCOUNT="xy43028.ap-southeast-7.aws"
USER="mushimaw1"
DATABASE="DE_PROJECT"
SCHEMA="RAW"
STAGE="CSV_STAGE"

snowsql \
  -a "$ACCOUNT" \
  -u "$USER" \
  -d "$DATABASE" \
  -s "$SCHEMA" \
  -q "PUT file://data/*.csv @${STAGE} AUTO_COMPRESS=TRUE OVERWRITE=TRUE;"