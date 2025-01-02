from __future__ import annotations

from data_flow_engine.models import NewField
from pyspark.sql import DataFrame
from pyspark.sql.functions import current_timestamp


def add_flow_fields(df: DataFrame, fields: list[NewField]) -> DataFrame:
    for field in fields:
        match field.function:
            case "current_timestamp":
                df = df.withColumn(field.name, current_timestamp())
            case _:
                raise Exception("Function not implemented!!")
    return df
