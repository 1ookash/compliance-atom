import typing

import pydantic
from pydantic.dataclasses import dataclass

COMPLIANCE_LEVEL = (
    typing.Literal['FC']
    | typing.Literal['LC']
    | typing.Literal['PC']
    | typing.Literal['NC']
    | typing.Literal['NA']
)


@dataclass(config=pydantic.ConfigDict(frozen=True, strict=True, extra='forbid'))
class ModelInputDTO:
    reference: str
    reference_tokens_cnt: int
    source: str | None
    source_tokens_cnt: int | None
    reference_name: str
    doc_number: int


@dataclass(config=pydantic.ConfigDict(frozen=True, strict=True, extra='forbid'))
class InputReaderDTO:
    result: list[ModelInputDTO]
    doc_cnt: int


@dataclass(config=pydantic.ConfigDict(frozen=True, strict=True, extra='forbid'))
class ModelAnswerDetailedDTO:
    category: str
    difference: str
    difference_source: str


@dataclass(config=pydantic.ConfigDict(frozen=True, strict=True, extra='forbid'))
class ModelOutputDTO:
    doc_number: int
    reference_name: str
    difference: str
    description: str
    compliance_level: COMPLIANCE_LEVEL
    detailed_difference: list[ModelAnswerDetailedDTO] | None
    model_answer_raw: str


@dataclass(config=pydantic.ConfigDict(frozen=True, strict=True, extra='forbid'))
class MetricCalculatorDTO:
    doc_number: int
    reference_name: str
    difference: str
    description: str
    compliance_level: COMPLIANCE_LEVEL
    value: float


@dataclass(config=pydantic.ConfigDict(frozen=True, strict=True, extra='forbid'))
class OutputCreatorDTO:
    result: list[MetricCalculatorDTO]
    doc_cnt: int
