# mypy: ignore-errors
import json

import requests

from .config import CONFIG
from .dtos import ModelAnswerDetailedDTO, ModelInputDTO, ModelOutputDTO
from .promt_templates import system_promt_template, user_promt_template
from .tools import logger

# from datetime import timedelta


class ModelInference:
    def __init__(self) -> None:
        self._logger = logger.nest_obj_logger(self)

    def inference(self, data: ModelInputDTO) -> ModelOutputDTO:
        # pylint: disable=missing-timeout
        self._logger.debug('inference begin')
        if data.source is None:
            self._logger.warning(
                'У спецификации нет соответствующей документации',
                params_please={'document number': data.doc_number},
            )
            return ModelOutputDTO(
                doc_number=data.doc_number,
                reference_name=data.reference_name,
                difference='ssts hasn\'t info about this',
                description='',
                compliance_level='NA',
                model_answer_raw='',
                detailed_difference=None,
            )

        system_promt = system_promt_template.strip(' \t\r\n').replace('\n\n', '\n')

        user_promt = (
            user_promt_template.format(
                reference=data.reference,
                source=data.source,
            )
            .strip(' \t\r\n')
            .replace('  ', ' ')
            .replace('\n\n', '\n')
        )

        self._logger.debug(
            'system and user promt created, sending request',
            params_please={
                'system promt tokens count': len(system_promt),
                'user promt tokens count': len(user_promt),
            },
        )

        response = requests.post(
            url=CONFIG.llm_url,
            headers={
                'accept': 'application/json',
                'Content-Type': 'application/json',
            },
            json={
                'system_promt': system_promt,
                'user_promt': user_promt,
            },
            # timeout=timedelta(hours=2).total_seconds(),
        )
        self._logger.debug('response', params_please={'response status': response.status_code})

        try:
            result = self._parse_anwser(response.text)
        except KeyError as error:
            self._logger.exception(
                'Не удалось распарсить ответ', params_please={'answer': response.text}
            )
            raise RuntimeError('Не удалось распарсить ответ') from error

        if data.doc_number != result.doc_number:
            self._logger.warning(
                'Номер документа не совпадает',
                params_please={
                    'document number by regex': data.doc_number,
                    'document number by LLM': result.doc_number,
                },
            )

        if data.reference_name.lower() != result.reference_name.lower():
            self._logger.warning(
                'Название спецификации не совпадает',
                params_please={
                    'document name by regex': data.reference_name,
                    'document name by LLM': result.reference_name,
                },
            )

        self._logger.debug(
            'inference end', params_please={'answer': json.loads(response.text)['answer']}
        )
        return result

    def _parse_anwser(self, answer_raw: str) -> ModelOutputDTO:
        answer = json.loads(answer_raw)['answer']

        detailed_difference = []
        for detailed in answer['Details']:  # type: ignore
            detailed_difference.append(
                ModelAnswerDetailedDTO(
                    category=detailed['Category'],  # type: ignore
                    difference=detailed['Difference'],  # type: ignore
                    difference_source=detailed['Source'],  # type: ignore
                    compliance_level=answer['Grade'],  # type: ignore
                )
            )

        return ModelOutputDTO(
            doc_number=int(answer['Number']),  # type: ignore
            reference_name=answer['Name'],  # type: ignore
            difference=answer['Difference'],  # type: ignore
            description=answer['Description'],  # type: ignore
            compliance_level=answer['Compliance Level'],  # type: ignore
            detailed_difference=detailed_difference,
            model_answer_raw=answer_raw,
        )
