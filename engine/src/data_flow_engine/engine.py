from __future__ import annotations

from data_flow_engine.models import (
    DataFlow,
    DataFlowSource,
    JsonFileOutput,
    KafkaOutput,
    SupportedFormats,
)
from data_flow_engine.sources.file import to_file
from data_flow_engine.sources.kafka import KafkaAgent
from data_flow_engine.transformations.common import apply_transformations
from loguru import logger
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    struct,
    to_json,
)


class WorkFlow:
    def __init__(
        self,
        spark: SparkSession,
        metadata: DataFlow,
        kafka_broker: str,
        hdfs_host: str,
        hdfs_port: int | str,
    ):
        """
        Args:
            spark: Spark Session
            metadata: Valid DataFlow object with inputs, validations,
                transformations and sinks to perform
            kafka_broker: Karfa URI with port
            hdfs_host: Hadoop host
            hdfs_port: Hadoop port
        """
        self.spark: SparkSession = spark
        self.metadata: DataFlow = metadata
        self.hdfs_host: str = hdfs_host
        self.hdfs_port: str = hdfs_port
        self.kafka_broker: str = kafka_broker
        self.kafka_agent: KafkaAgent = KafkaAgent(bootstrap_servers=kafka_broker)

    def get_hdfs_path(self, path: str) -> str:
        return f"hdfs://{self.hdfs_host}:{self.hdfs_port}{path}"

    def read_hdfs(self, path: str, format: SupportedFormats):
        match format:
            case SupportedFormats.json:
                return self.spark.read.json(path)
            case _:
                raise NotImplementedError(f"Format {format} not implemented!")

    def to_kafka(self, df: DataFrame, topic: str):
        """
        Creates the topic and writes the given dataframe into it.
        Args:
            df: DataFrame with data to dump into Kafka
            topic: Target Kafka topic

        Returns:

        """
        logger.info(f"Writting data in topic {topic}...")
        self.kafka_agent.add_topic(topic)
        df.select(to_json(struct("*")).alias("value")).selectExpr(
            "CAST(value AS STRING)"
        ).write.format("kafka").option("kafka.bootstrap.servers", self.kafka_broker).option(
            "topic", topic
        ).save()
        logger.info(f"Writting data in topic {topic}... DONE")

    def read_sources(self, sources: list[DataFlowSource], inputs: dict[str, DataFrame]):
        logger.info("Reading sources...")
        for source in sources:
            try:
                logger.info(f"Reading source {source}...")
                path = source.path.replace("*", "")
                hdfs_path = self.get_hdfs_path(path)
                df = self.read_hdfs(hdfs_path, source.format)
                inputs[source.name] = df
                logger.info(f"Reading source {source}... DONE")
            except Exception as e:
                logger.error(f"Could not read source {source}", e)
        logger.info("Reading sources... DONE")

    def sink(self, sinks: list[KafkaOutput | JsonFileOutput], inputs: dict):
        for sink in sinks:
            df = inputs[sink.input]

            match sink.format:
                case SupportedFormats.kafka:
                    topics = sink.topics
                    for topic in topics:
                        self.to_kafka(df, topic)

                case SupportedFormats.json:
                    for path in sink.paths:
                        hdfs_path = self.get_hdfs_path(path)
                        logger.info(f"Writing data into {hdfs_path}...")
                        to_file(df, hdfs_path, "json", sink.save_mode)
                        logger.info(f"Writing data into {hdfs_path}... DONE")

    def run(self):
        """
        Main method. Sequentially reads the sources, applies the transformations and
        sinks the data for the dataflows object in self.metadata.
        """
        for dataflow in self.metadata.dataflows:
            logger.info(f"Processing Data Flow {dataflow.name}...")
            inputs: dict[str, DataFrame] = {}
            self.read_sources(sources=dataflow.sources, inputs=inputs)
            logger.info("Applying transformations...")
            apply_transformations(transformations=dataflow.transformations, inputs=inputs)
            logger.info("Applying transformations... DONE")
            self.sink(sinks=dataflow.sinks, inputs=inputs)
            logger.info(f"Processing Data Flow {dataflow.name}... DONE")
