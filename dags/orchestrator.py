import sys
from airflow.decorators import dag, task
from datetime import datetime, timedelta
from docker.types import Mount
from airflow.providers.docker.operators.docker import DockerOperator

# 注意：sys.path.append 必須在 import insert_records 之前執行
sys.path.append('/opt/airflow/api-request')
from insert_records import main

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

@dag(
    dag_id='weather_api_orchestrator',
    default_args=default_args,
    description='A DAG to orchestrate data',
    start_date=datetime(2026, 2, 10),
    schedule=timedelta(minutes=10),
    catchup=False,
    tags=['weather', 'api']
)
def weather_api_pipeline():

    # 將原本的 PythonOperator 改寫為 @task 裝飾的函數
    @task(task_id='insert_weather_data')
    def run_insert_records():
        # 直接呼叫引入的 main 函數
        main()

    run_dbt = DockerOperator(
        task_id='transform_data_task',
        image='ghcr.io/dbt-labs/dbt-postgres:1.9.latest',
        command='run',
        working_dir='/usr/app',
        mount_tmp_dir=False,
        mounts=[
            Mount(
                source='/Users/adam/Downloads/Project with Superset/dbt/weather_project',
                target='/usr/app',
                type='bind'
            ),
            Mount(
                source='/Users/adam/Downloads/Project with Superset/dbt/profiles.yml',
                target='/root/.dbt/profiles.yml',
                type='bind'
            )
        ],
        network_mode='projectwithsuperset_my-network',  # need to add your project name as prefix,
        docker_url='unix:///var/run/docker.sock',
        auto_remove='success',
    )

    # 執行 Task
    ingest_task = run_insert_records()

    ingest_task >> run_dbt

# 實例化 DAG
weather_api_pipeline()