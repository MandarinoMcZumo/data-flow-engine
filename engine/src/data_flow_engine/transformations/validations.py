from __future__ import annotations

from data_flow_engine.models import ColumnNames, FieldValidation
from pyspark.sql import DataFrame
from pyspark.sql.functions import array, col, concat, lit, struct, when
from pyspark.sql.types import ArrayType, StringType, StructField, StructType


def not_null(df: DataFrame, field: str) -> DataFrame:
    validation_error = struct(lit(field).alias("field"), lit("Field cannot be null").alias("error"))
    return df.withColumn(
        ColumnNames.failed_validations.value,
        when(
            col(field).isNull(),
            concat(col(ColumnNames.failed_validations.value), array(validation_error))
        ).otherwise(col(ColumnNames.failed_validations.value))
    )


def not_empty(df: DataFrame, field: str) -> DataFrame:
    validation_error = struct(lit(field).alias("field"), lit("Field cannot be empty").alias("error"))
    return df.withColumn(
        ColumnNames.failed_validations.value,
        when(
            col(field) == "",
            concat(col(ColumnNames.failed_validations.value), array(validation_error))
        ).otherwise(col(ColumnNames.failed_validations.value))
    )


def validate_fields(df: DataFrame, field_validations: list[FieldValidation]) -> dict[str, DataFrame]:
    df = df.withColumn(
        ColumnNames.failed_validations.value,
        lit([]).cast(ArrayType(StructType([
            StructField("field", StringType(), True),
            StructField("error", StringType(), True)
        ])))
    )

    for field_validation in field_validations:
        if "notEmpty" in field_validation.validations:
            df = not_empty(df=df, field=field_validation.field)

        if "notNull" in field_validation.validations:
            df = not_null(df=df, field=field_validation.field)

    df.cache()
    valid_df = df.filter(df[ColumnNames.failed_validations.value] == lit([])).drop(
        ColumnNames.failed_validations.value)
    invalid_df = df.filter(df[ColumnNames.failed_validations.value] != lit([]))
    return {'ok': valid_df, 'ko': invalid_df}
