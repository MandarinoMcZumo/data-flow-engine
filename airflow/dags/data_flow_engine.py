import json
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from hdfs import InsecureClient

with DAG(
    "data_flow_engine",
    description="Processes a new workflow for the given metadata file.",
    schedule_interval=None,
    start_date=datetime(2024, 12, 31),
    catchup=False,
) as dag:
    metadata_filepath = "/opt/airflow/data/metadata.json"
    with open(metadata_filepath, "r") as json_file:
        metadata = json.load(json_file)


    def hdfs_upload():
        client = InsecureClient("http://namenode:9870")
        client.upload(
            "/data/input/events/person",
            "/opt/airflow/data/input/events/person/input-data.json",
            overwrite=True,
        )

    def hdfs_download():
        client = InsecureClient("http://namenode:9870")
        client.download(
            "/data/output/discards/person",
            "/opt/airflow/data/output/discards/person",
            overwrite=True,
        )

    hdfs_compose = "docker-compose -f /opt/airflow/hadoop/docker-compose.yaml"
    spark_compose = "docker-compose -f /opt/airflow/spark/docker-compose.yaml"
    kafka_compose = "docker-compose -f /opt/airflow/kafka/docker-compose.yaml"

    start_kafka_service = BashOperator(
        task_id="start_kafka_service", bash_command=f"{kafka_compose} up -d && sleep 60"
    )

    start_hdfs_service = BashOperator(
        task_id="start_hdfs_service", bash_command=f"{hdfs_compose} up -d && sleep 60"
    )

    upload_to_hdfs = PythonOperator(
        task_id="upload_to_hdfs", python_callable=hdfs_upload
    )

    start_spark_service = BashOperator(
        task_id="start_spark_service",
        bash_command=f"{spark_compose} up -d  && sleep 30",
    )

    spark_job = SparkSubmitOperator(
        task_id="spark_job",
        conn_id="spark",
        application="/opt/airflow/dags/pipelines/etl.py",
        packages="org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.4",
        py_files="hdfs://namenode:9000/packages/data_flow_engine-0.2.3.zip",
        application_args=[
            "--metadata",
            json.dumps(metadata),
            "--kafka_broker",
            "redpanda:9092",
            "--hdfs_host",
            "namenode",
            "--hdfs_port",
            "9000",
        ],
    )

    stop_spark_service = BashOperator(
        task_id="stop_spark_service",
        bash_command=f"{spark_compose} down",
        trigger_rule="all_done",
    )

    download_from_hdfs = PythonOperator(
        task_id="download_from_hdfs", python_callable=hdfs_download
    )

    stop_hdfs_service = BashOperator(
        task_id="stop_hdfs_service",
        bash_command=f"{hdfs_compose} down",
        trigger_rule="all_done",
    )

    stop_kafka_service = BashOperator(
        task_id="stop_kafka_service",
        bash_command=f"{kafka_compose} down",
    )

    (
        [start_hdfs_service, start_spark_service, start_kafka_service]
        >> upload_to_hdfs
        >> spark_job
        >> download_from_hdfs
        >> [stop_hdfs_service, stop_spark_service, stop_kafka_service]
    )
