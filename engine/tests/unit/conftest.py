import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, StringType, StructField, StructType


@pytest.fixture(scope='session')
def spark():
    spark = (
        SparkSession
        .builder.appName("TestSparkSession")
        .config("spark.driver.extraJavaOptions", "-Djava.security.manager=allow")
        .getOrCreate()
    )
    yield spark
    spark.stop()


@pytest.fixture
def fake_data(spark):
    data = [
        {"name": "Xabier", "age": 39, "office": ""},
        {"name": "Miguel", "office": "RIO"},
        {"name": "Fran", "age": 31, "office": "RIO"}
    ]
    schema = StructType([
        StructField("name", StringType(), True),
        StructField("age", IntegerType(), True),
        StructField("office", StringType(), True)
    ])

    return spark.createDataFrame(data, schema=schema)
