from .dtos import MetricCalculatorDTO, ModelOutputDTO


class MetricCalculator:
    def calc(
        self,
        data: ModelOutputDTO,
    ) -> MetricCalculatorDTO:
        # TODO: заглушка, тут нужно будет реализовать логику подсчета метрики
        return MetricCalculatorDTO(
            doc_number=data.doc_number,
            reference_name=data.reference_name,
            difference=data.difference,
            description=data.description,
            compliance_level=data.compliance_level,
            value=0.5,
        )
