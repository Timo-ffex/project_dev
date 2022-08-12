import os
import logging

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator, BigQueryInsertJobOperator
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")

path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'trips_data_all')

DATASET = "tripdata"
INPUT_PART = "raw"
INPUT_FILETYPE = "parquet"

yellow_schema = [
    {"name":"VendorID", "type": "INTEGER"},
    {"name":"tpep_pickup_datetime", "type": "TIMESTAMP"},
    {"name":"tpep_dropoff_datetime", "type": "TIMESTAMP"},
    {"name":"passenger_count", "type": "FLOAT64"},
    {"name":"trip_distance", "type": "FLOAT64"},
    {"name":"RatecodeID", "type": "FLOAT64"},
    {"name":"store_and_fwd_flag", "type": "STRING"},
    {"name":"PULocationID", "type": "INTEGER"},
    {"name":"DOLocationID", "type": "INTEGER"},
    {"name":"payment_type", "type": "INTEGER"},
    {"name":"fare_amount", "type": "FLOAT64"},
    {"name":"extra", "type": "FLOAT64"},
    {"name":"mta_tax", "type": "FLOAT64"},
    {"name":"tip_amount", "type": "FLOAT64"},
    {"name":"tolls_amount", "type": "FLOAT64"},
    {"name":"improvement_surcharge", "type": "FLOAT64"},
    {"name":"total_amount", "type": "FLOAT64"},
    {"name":"congestion_surcharge", "type": "FLOAT64"},
]

green_schema = [
    {"name":"VendorID", "type": "INTEGER"},
    {"name":"lpep_pickup_datetime", "type": "TIMESTAMP"},
    {"name":"lpep_dropoff_datetime", "type": "TIMESTAMP"},
    {"name":"store_and_fwd_flag", "type": "STRING"},
    {"name":"RatecodeID", "type": "FLOAT64"},
    {"name":"PULocationID", "type": "INTEGER"},
    {"name":"DOLocationID", "type": "INTEGER"},
    {"name":"passenger_count", "type": "FLOAT64"},
    {"name":"trip_distance", "type": "FLOAT64"},
    {"name":"fare_amount", "type": "FLOAT64"},
    {"name":"extra", "type": "FLOAT64"},
    {"name":"mta_tax", "type": "FLOAT64"},
    {"name":"tip_amount", "type": "FLOAT64"},
    {"name":"tolls_amount", "type": "FLOAT64"},
    {"name":"improvement_surcharge", "type": "FLOAT64"},
    {"name":"total_amount", "type": "FLOAT64"},
    {"name":"payment_type", "type": "FLOAT64"},
    {"name":"trip_type", "type": "FLOAT64"},
    {"name":"congestion_surcharge", "type": "FLOAT64"},
]


fhv_schema = [
    {"name":"dispatching_base_num", "type": "STRING"},
    {"name":"pickup_datetime", "type": "TIMESTAMP"},
    {"name":"dropOff_datetime", "type": "TIMESTAMP"},
    {"name":"PUlocationID", "type": "STRING"},
    {"name":"DOlocationID", "type": "STRING"},
    {"name":"Affiliated_base_number", "type": "STRING"},
    {"name":"SR_Flag", "type": "STRING"}
]

COLOUR_RANGE = {'yellow': { 'partition_col': 'tpep_pickup_datetime', 'schema': yellow_schema},
                'green': { 'partition_col': 'lpep_pickup_datetime', 'schema': green_schema},
                'fhv': { 'partition_col': 'pickup_datetime', 'schema': fhv_schema},
                }

default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1,
}

# NOTE: DAG declaration - using a Context Manager (an implicit way)
with DAG(
    dag_id="gcs_2_bq_dag",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=['dit-pipeline'],
) as dag:

    for colour, properties in COLOUR_RANGE.items():
        schema = properties['schema']
        ds_col = properties['partition_col']
        print(schema)

        # move_files_gcs_task = GCSToGCSOperator(
        #     task_id=f'move_{colour}_{DATASET}_files_task',
        #     source_bucket=BUCKET,
        #     source_object=f'{INPUT_PART}/{colour}_{DATASET}*.{INPUT_FILETYPE}',
        #     destination_bucket=BUCKET,
        #     destination_object=f'{colour}/{colour}_{DATASET}',
        #     move_object=True
        # )

        bigquery_external_table_task = BigQueryCreateExternalTableOperator(
            task_id=f"bq_{colour}_{DATASET}_external_table_task",
            # schema_fields=schema,
            table_resource={
                "tableReference": {
                    "projectId": PROJECT_ID,
                    "datasetId": BIGQUERY_DATASET,
                    "tableId": f"{colour}_{DATASET}_external_table",
                },
                "schema": {"fields": schema},
                "externalDataConfiguration": {
                    # "schema_object": {"fields": schema},
                    "sourceFormat": f"{INPUT_FILETYPE.upper()}",
                    "sourceUris": [f"gs://{BUCKET}/raw/{colour}_tripdata/*.parquet"],
                },
            },
        )

        CREATE_BQ_TBL_QUERY = (
            f"CREATE OR REPLACE TABLE {BIGQUERY_DATASET}.{colour}_{DATASET} \
            PARTITION BY DATE({ds_col}) \
            AS \
            SELECT * FROM {BIGQUERY_DATASET}.{colour}_{DATASET}_external_table;"
        )

        # Create a partitioned table from external table
        bq_create_partitioned_table_job = BigQueryInsertJobOperator(
            task_id=f"bq_create_{colour}_{DATASET}_partitioned_table_task",
            configuration={
                "query": {
                    "query": CREATE_BQ_TBL_QUERY,
                    "useLegacySql": False,
                }
            }
        )

        # move_files_gcs_task >> bigquery_external_table_task >> bq_create_partitioned_table_job
        bigquery_external_table_task >> bq_create_partitioned_table_job