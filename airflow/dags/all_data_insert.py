import os
import logging, time
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT 

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import pyarrow.csv as pv
import pyarrow.parquet as pq

from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")

USER = os.environ.get('PGUSER')
PGPASSWORD = os.environ.get('PGPASSWORD')
PGHOST = os.environ.get('PGHOST')
PGPORT = os.environ.get('PGPORT')
DBNAME = os.environ.get('DBNAME')

USER = 'airflow'
PGPASSWORD = 'airflow'
PGHOST = 'postgres'
PGPORT = 5432
DBNAME = 'nyc_taxi'


AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
run_month = "{{ execution_date.strftime(\'%Y-%m\') }}"
DATA_URL_PREFIX = "https://d37ci6vzurychx.cloudfront.net"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

def create_db():
    # try:
    con = psycopg2.connect(
        user=USER, 
        host=PGHOST,
        port=PGPORT,
        password=PGPASSWORD)

    cur = con.cursor()
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur.execute(sql.SQL(
        f"SELECT 'CREATE DATABASE {DBNAME}' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '{DBNAME}')")
        )
    # except Exception as e:
    #     print(e)

def format_to_parquet(src_file):
    """convert csv to parquet file

    Args:
        src_file (str): source filepath (must be csv)
    """
    if not src_file.endswith('.csv'):
        logging.error("Can only accept source files in CSV format, for the moment")
        return
    dest_file = src_file.replace('.csv', '.parquet')
    table = pv.read_csv(src_file)
    pq.write_table(table, dest_file)


def load_to_postgres(name, path):
    df = pd.read_parquet(path)
    connect = f'postgresql+psycopg2://{USER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{DBNAME}'
    print(f'\n\n{connect}\n\n')
    engine = create_engine(connect)
    total = len(df)
    count = 0

    while count < total:
        start = time.time()
        next_ = count + 50000
        # print(count, next_)
        write_df = df.iloc[count: next_]
        write_df.to_sql(name=f'{name}_taxi_data', con=engine, if_exists='append', index=False)
        count = next_
        print(f'inserted chunk... took: {round((time.time()-start), 2)} second')


def upload_to_gcs(bucket, object_name, local_file):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """

    client = storage.Client()

    print(f"\n\nbucket: {bucket}, \t {local_file}\n\n")
    bucket = client.bucket(bucket)
    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)


def download_and_uplod_to_gcs(
    dag,
    name,
    dataset_url,
    file_name,
    local_filepath,
    gcs_filepath
):
    with dag:

        download_dataset_task = BashOperator(
            task_id="download_dataset_task",
            bash_command=f"""
                        cd {AIRFLOW_HOME}

                        if [[ $(ls | grep {file_name}) = {file_name} ]]; then
                            echo "File - {file_name} already exists"
                        else
                            curl -sSL {dataset_url} > {local_filepath}
                            echo "Downloaded File - {file_name} successfully"
                        fi
                    """
        )

        local_to_gcs_task = PythonOperator(
            task_id="local_to_gcs_task",
            python_callable=upload_to_gcs,
            op_kwargs={
                "bucket": BUCKET,
                "object_name": f"{gcs_filepath}",
                "local_file": f"{local_filepath}",
            },
        )

        delete_file = BashOperator(
            task_id="delete_downloaded_file",
            # bash_command=f"rm {local_filepath}"
            bash_command=f"echo DELETED"
        )

        create_db_if_not_exist_task = PythonOperator(
            task_id="create_db_if_not_exist",
            python_callable=create_db,
        )

        load_to_postgres_task = PythonOperator(
            task_id="load_to_postgres",
            python_callable=load_to_postgres,
            op_kwargs={
                "name": name,
                "path": f"{local_filepath.replace('.csv', '.parquet')}",
            },
        )
        if name == 'zone':

            
            convert_to_parquet = PythonOperator(
                task_id="format_to_parquet",
                python_callable=format_to_parquet,
                op_kwargs={
                    "src_file": f"{local_filepath}",
                },
            )
            download_dataset_task >> convert_to_parquet >> [local_to_gcs_task, create_db_if_not_exist_task >> load_to_postgres_task] >> delete_file
        else:
            download_dataset_task >> [local_to_gcs_task, create_db_if_not_exist_task >> load_to_postgres_task] >> delete_file



dag_config = {
    'yellow': {
        'start_date': datetime(2019, 1, 1),
        'end_date': datetime(2021, 1, 1),
        'schedule_interval': '0 3 1 * *',
    },
    'green': {
        'start_date': datetime(2019, 1, 1),
        'end_date': datetime(2021, 1, 1),
        'schedule_interval': '0 4 1 * *',
    },
    'fhv': {
        'start_date': datetime(2019, 1, 1),
        'end_date': datetime(2020, 1, 1),
        'schedule_interval': '0 5 1 * *',
    },
    'zone': {
        'start_date': datetime.now(),
        'end_date': None,
        'schedule_interval': '@once',
    },
}


def create_dags(name=None, folder='trip-data', **config):
    FILE_NAME = f"{name}_tripdata_{run_month}.parquet"
    FILE_DOWNLOAD_TEMPLATE = f"{DATA_URL_PREFIX}/{folder}/{FILE_NAME}"
    FILE_LOCAL_TEMPLATE = f"{AIRFLOW_HOME}/{FILE_NAME}"
    FILE_GCS_TEMPLATE = f"raw/{name}_tripdata/{run_month}.parquet"

    if name == 'zone':
        # /misc/taxi+_zone_lookup.parquet
        FILE_DOWNLOAD_TEMPLATE = f"{DATA_URL_PREFIX}/misc/taxi+_zone_lookup.csv"
        FILE_LOCAL_TEMPLATE = f"{AIRFLOW_HOME}/taxi_zone_lookup.csv"
        FILE_GCS_TEMPLATE = f"raw/taxi_zone/taxi_zone_lookup.parquet"
        # ZONE_LOCAL_TEMPLATE = f"{AIRFLOW_HOME}/taxi_zone_lookup.csv"
        # ZONE_GCS_TEMPLATE = f"raw/taxi_zone/taxi_zone_lookup.parquet"

    dag = DAG(
        dag_id=f"{name}_taxi_data",
        schedule_interval=config["schedule_interval"],
        start_date=config["start_date"],
        end_date=config["end_date"],
        default_args=default_args,
        catchup=True,
        max_active_runs=3,
        tags=['dit-pipeline'],
    )

    download_and_uplod_to_gcs(
        dag=dag,
        name=name,
        dataset_url=FILE_DOWNLOAD_TEMPLATE,
        file_name=FILE_NAME,
        local_filepath=FILE_LOCAL_TEMPLATE,
        gcs_filepath=FILE_GCS_TEMPLATE,
    )
    return dag


globals()["yellow_taxi_dags"] = create_dags('yellow', 
                                schedule_interval='0 3 1 * *',
                                start_date = datetime(year=2019, month=12, day=1),
                                end_date = datetime(2021, 1, 1)
                                )

globals()["green_taxi_dags"] = create_dags('green', 
                                schedule_interval='0 4 1 * *',
                                start_date = datetime(year=2019, month=12, day=1),
                                end_date = datetime(2021, 1, 1)
                                )

globals()["fhv_taxi_dags"] = create_dags('fhv', 
                                schedule_interval='0 6 1 * *',
                                start_date = datetime(year=2019, month=12, day=1),
                                end_date = datetime(2020, 1, 1)
                                )

globals()["zone_taxi_dags"] = create_dags('zone', 
                                schedule_interval='@once',
                                start_date = datetime.now(),
                                end_date = None
                                )


