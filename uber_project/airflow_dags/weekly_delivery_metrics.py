from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import os

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='weekly_delivery_metrics_dag',
    default_args=default_args,
    description='Load weekly delivery metrics',
    schedule_interval='0 6 * * 1',  # Every monday at 6 AM
    start_date=days_ago(1),
    catchup=False,
    tags=['weekly', 'metrics']
) as dag:

    def read_sql_file(**context):
        filepath = os.path.join(os.path.dirname(__file__), '../sql/weekly_delivery_metrics.sql')
        with open(filepath, 'r') as file:
            raw_sql = file.read()
        rendered_sql = context['ti'].render_template(raw_sql)
        return rendered_sql

    load_metrics = PostgresOperator(
        task_id='load_weekly_delivery_metrics',
        postgres_conn_id='your_postgres_conn_id',  # ← update with the postgress connection
        sql=read_sql_file,
        provide_context=True
    )

    load_metrics
