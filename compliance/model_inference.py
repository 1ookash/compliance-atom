# mypy: ignore-errors
import json

import requests

from .config import CONFIG
from .dtos import ModelInputDTO, ModelOutputDTO
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
            )

        system_promt = (
            system_promt_template.strip(' \t\r\n').replace('  ', ' ').replace('\n\n', '\n')
        )

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

        self._logger.debug(
            'inference end', params_please={'answer': json.loads(response.text)['answer']}
        )
        return ModelOutputDTO(
            doc_number=data.doc_number,
            reference_name=data.reference_name,
            difference='ssts hasn\'t info about this',
            description='',
            compliance_level='NA',
        )
