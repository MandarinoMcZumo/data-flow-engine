from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from hdfs import InsecureClient

with DAG(
        'spark_package_upload',
        description='Uploads a file to HDFS',
        schedule_interval=None,
        start_date=datetime(2024, 12, 31),
        catchup=False,
) as dag:
    hdfs_compose = "docker-compose -f /opt/airflow/hadoop/docker-compose.yaml"


    def hdfs_upload():
        client = InsecureClient('http://namenode:9870')
        client.upload(
            '/packages/data_flow_engine-0.1.2.zip',
            '/opt/airflow/spark/packages/data_flow_engine-0.1.2.zip',
            overwrite=True
        )


    start_hdfs_service = BashOperator(
        task_id='start_hdfs_service',
        bash_command=f"{hdfs_compose} up -d && sleep 60"
    )

    upload_to_hdfs = PythonOperator(
        task_id='upload_to_hdfs',
        python_callable=hdfs_upload
    )

    stop_hdfs_service = BashOperator(
        task_id='stop_hdfs_service',
        bash_command=f"{hdfs_compose} down",
        trigger_rule="all_done"

    )

    start_hdfs_service >> upload_to_hdfs >> stop_hdfs_service
