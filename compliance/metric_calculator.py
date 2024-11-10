from .dtos import MetricCalculatorDTO, ModelAnswerDetailedDTO, ModelOutputDTO
from .tools import logger, printer


class MetricCalculator:
    def __init__(self) -> None:
        self._logger = logger.nest_obj_logger(self)

    def calc(
        self,
        data: ModelOutputDTO,
    ) -> MetricCalculatorDTO:
        self._logger.debug('calc begin')
        if data.model_answer_raw is None and data.compliance_level == 'NA':
            self._logger.warning(
                'Пропуск подсчета метрики из-за отсутствия ответа от модели',
                params_please={'document number': data.doc_number},
            )
            return MetricCalculatorDTO(
                doc_number=data.doc_number,
                reference_name=data.reference_name,
                difference=data.difference,
                description=data.description,
                compliance_level=data.compliance_level,
                value=0,
            )
        assert data.detailed_differences is not None

        eval_ref = self._evaluate_reference(detailed_differences=data.detailed_differences)
        self._logger.debug(
            'evaluate reference end',
            params_please={'evaluate reference result': printer.Printer.pretty_print(eval_ref)},
        )

        return MetricCalculatorDTO(
            doc_number=data.doc_number,
            reference_name=data.reference_name,
            difference=data.difference,
            description=data.description,
            compliance_level=data.compliance_level,
            value=self._evaluate_difference(eval_ref=eval_ref),
        )

    def _evaluate_reference(
        self, detailed_differences: list[ModelAnswerDetailedDTO]
    ) -> dict[str, int]:
        result = {
            'Preconditions': 0,
            'Main Scenario': 0,
            'Postconditions': 0,
            'Alternative Scenario': 0,
            'Exit Conditions': 0,
        }

        for detail in detailed_differences:
            if detail.category in result.keys():
                result[detail.category] += 1

        return result

    def _evaluate_difference(self, eval_ref: dict[str, int]) -> float:
        paragraph_weights = {
            'Preconditions': 0.3,
            'Main Scenario': 0.25,
            'Postconditions': 0.2,
            'Alternative Scenario': 0.15,
            'Exit Conditions': 0.1,
        }
        compliance_scale = {'FC': 1, 'LC': 0.75, 'PC': 0.5, 'NC': 0.25, 'NA': 0}

        total_grade = 0.0
        total_weight = 0.0

        for category, changes in eval_ref.items():
            grade = 'FC'
            if changes >= 5:
                grade = 'NC'
            if changes >= 3:
                grade = 'PC'
            if changes >= 1:
                grade = 'LC'

            weight = paragraph_weights[category]
            total_grade += compliance_scale[grade] * weight
            total_weight += weight

        if total_weight > 0:
            return total_grade / total_weight

        return 0.0
