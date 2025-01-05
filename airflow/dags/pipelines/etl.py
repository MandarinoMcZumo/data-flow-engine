import argparse

from data_flow_engine.models import DataFlow
from pyspark.sql import SparkSession
import json

from data_flow_engine.engine import WorkFlow


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=str, help="ETL metadata")
    parser.add_argument("--kafka_broker", type=str, help="Kafka broker")
    parser.add_argument("--hdfs_host", type=str, help="HDFS host")
    parser.add_argument("--hdfs_port", type=str, help="HDFS port")

    args = parser.parse_args()

    spark = SparkSession.builder.appName("SparkPipeline").getOrCreate()

    validated_metadata = DataFlow.model_validate(json.loads(args.metadata))

    WorkFlow(
        spark=spark,
        metadata=validated_metadata,
        kafka_broker=args.kafka_broker,
        hdfs_host=args.hdfs_host,
        hdfs_port=args.hdfs_port,
    ).run()

    spark.stop()
