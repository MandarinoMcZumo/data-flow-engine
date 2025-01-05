from __future__ import annotations

from data_flow_engine.models import (
    NewFieldTransformation,
    SupportedTransformations,
    ValidationFieldTransformation,
)
from data_flow_engine.transformations.extra_fields import add_flow_fields
from data_flow_engine.transformations.validations import validate_fields
from pyspark.sql import DataFrame


def apply_transformations(
    transformations: list[NewFieldTransformation | ValidationFieldTransformation],
    inputs: dict[str, DataFrame],
):
    for transformation in transformations:
        params = transformation.params
        match transformation.type:
            case SupportedTransformations.validate_fields:
                validations = params.validations
                validation_result_dfs = validate_fields(inputs[params.input], validations)
                inputs[f"{transformation.name}_ok"] = validation_result_dfs["ok"]
                inputs[f"{transformation.name}_ko"] = validation_result_dfs["ko"]

            case SupportedTransformations.add_fields:
                df = add_flow_fields(inputs[params.input], params.add_fields)
                inputs[transformation.name] = df
