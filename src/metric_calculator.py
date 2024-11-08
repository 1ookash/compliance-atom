from src.dtos import MetricCalculatorDTO, ModelOutputDTO


class MetricCalculator:
    def calc(
        self,
        data: ModelOutputDTO,
    ) -> MetricCalculatorDTO:
        raise NotImplementedError()
