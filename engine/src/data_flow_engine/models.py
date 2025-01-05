from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class ColumnNames(str, Enum):
    failed_validations = "failed_validations"


class SupportedTransformations(str, Enum):
    validate_fields = "validate_fields"
    add_fields = "add_fields"


class SupportedFormats(str, Enum):
    json = "JSON"
    kafka = "KAFKA"


class SupportedSaveModes(str, Enum):
    overwrite = "OVERWRITE"


class FieldValidation(BaseModel):
    field: str
    validations: list[str]


class FieldValidationParams(BaseModel):
    input: str
    validations: list[FieldValidation]


class ValidationFieldTransformation(BaseModel):
    name: str
    type: Literal[SupportedTransformations.validate_fields] = Field(alias="type")
    params: FieldValidationParams


class NewField(BaseModel):
    name: str
    function: str


class NewFieldParams(BaseModel):
    input: str
    add_fields: list[NewField] = Field(alias="addFields")


class NewFieldTransformation(BaseModel):
    name: str
    type: Literal[SupportedTransformations.add_fields] = Field(alias="type")
    params: NewFieldParams


class KafkaOutput(BaseModel):
    input: str  # Add custom validator for path with wildcard
    name: str
    topics: list[str]
    format: Literal[SupportedFormats.kafka]


class JsonFileOutput(BaseModel):
    input: str
    name: str
    paths: list[str]
    format: Literal[SupportedFormats.json]
    save_mode: SupportedSaveModes = Field(alias="saveMode")


class DataFlowSource(BaseModel):
    name: str
    path: str
    format: SupportedFormats


class DataFlowMetadata(BaseModel):
    name: str
    sources: list[DataFlowSource]
    transformations: list[NewFieldTransformation | ValidationFieldTransformation] | None = Field(
        default=None
    )
    sinks: list[KafkaOutput | JsonFileOutput]


class DataFlow(BaseModel):
    dataflows: list[DataFlowMetadata]
