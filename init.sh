#!/bin/sh
set -e

BUCKET_NAME="${INFLUXDB_BUCKET:-home_assistant}"
ORG="${INFLUXDB_ORG:-ut}"
RETENTION="${INFLUXDB_RETENTION:-72h}"

echo "Waiting for InfluxDB to be ready..."
until influx ping >/dev/null 2>&1; do
  sleep 2
done

echo "Creating bucket '$BUCKET_NAME' with retention '$RETENTION'..."

influx bucket create -n "$BUCKET_NAME" -o "$ORG" -r "$RETENTION"|| {
  echo "Bucket '$BUCKET_NAME' already exists or failed to create."
}

echo "Bucket '$BUCKET_NAME' is ready."