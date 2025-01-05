from data_flow_engine.models import FieldValidation, NewField
from data_flow_engine.transformations.extra_fields import add_flow_fields
from data_flow_engine.transformations.validations import validate_fields
from pyspark.sql import DataFrame, SparkSession


def test_validate_fields(spark: SparkSession, fake_data: DataFrame):
    validations = [
        FieldValidation(field="age", validations=["notNull"]),
        FieldValidation(field="office", validations=["notEmpty", "notNull"]),
    ]

    result = validate_fields(fake_data, validations)

    valid_df = result["ok"]
    not_valid_df = result["ko"]
    assert valid_df.count() == 1
    assert not_valid_df.count() == 2


def test_add_fields(spark: SparkSession, fake_data: DataFrame):
    fields = NewField(name="dt", function="current_timestamp")

    result_df = add_flow_fields(fake_data, [fields])
    assert "dt" in result_df.columns
