import sys
from airflow.decorators import dag, task
from datetime import datetime, timedelta

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
    schedule=timedelta(minutes=3),
    catchup=False,
    tags=['weather', 'api']
)
def weather_api_pipeline():

    # 將原本的 PythonOperator 改寫為 @task 裝飾的函數
    @task(task_id='task1')
    def run_insert_records():
        # 直接呼叫引入的 main 函數
        main()

    # 執行 Task
    run_insert_records()

# 實例化 DAG
weather_api_pipeline()