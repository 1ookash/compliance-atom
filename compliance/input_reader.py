# pylint: disable=import-error
# pylint: disable=no-name-in-module
import glob
import os
import re
import tempfile
import zipfile

import docx
from docx.opc.exceptions import PackageNotFoundError

from .dtos import InputReaderDTO, ModelInputDTO
from .tools import logger


class InputReader:
    def __init__(self) -> None:
        self._logger = logger.nest_obj_logger(self)

    def extract(self, input_file_path: str) -> InputReaderDTO:
        self._logger.debug('extract begin')
        source_result = {}
        reference_result = {}
        result = []

        with tempfile.TemporaryDirectory() as tempdir:
            zipfile.ZipFile(input_file_path).extractall(tempdir)

            for source_path in self._glob_paths(root_dir=tempdir, name='SSTS'):
                source_result[self._extract_doc_number(source_path)] = self._read_docx(source_path)

            for reference_path in self._glob_paths(root_dir=tempdir, name='UC'):
                reference_result[self._extract_doc_number(reference_path)] = self._read_docx(
                    reference_path
                )

        for key, value in reference_result.items():
            reference_name = value[value.find(']') + 2 : value.find('\n')].strip(' \t\r\n')
            try:
                source = source_result[key]
            except KeyError:
                result.append(
                    ModelInputDTO(
                        reference=value,
                        reference_tokens_cnt=len(value),
                        source=None,
                        source_tokens_cnt=None,
                        doc_number=key,
                        reference_name=reference_name,
                    )
                )
                continue
            result.append(
                ModelInputDTO(
                    reference=value,
                    reference_tokens_cnt=len(value),
                    source=source,
                    source_tokens_cnt=len(source),
                    doc_number=key,
                    reference_name=reference_name,
                )
            )

        self._logger.debug('extract end', params_please={'document count': len(result)})
        return InputReaderDTO(result=result, doc_cnt=len(result))

    def _read_docx(self, path: str) -> str:
        try:
            return (
                '\n'.join(
                    [
                        paragraphs.text.strip(' \t\r\n')
                        for paragraphs in docx.Document(path).paragraphs
                    ]
                )
                .replace('  ', ' ')
                .replace('\n\n', '\n')
            )
        except PackageNotFoundError as error:
            raise RuntimeError(f'couldn\'t find path {path}') from error

    def _extract_doc_number(self, path: str) -> int:
        try:
            return int(re.findall(r'\d+', path)[-1])
        except IndexError as error:
            raise RuntimeError('couldn\'t extract document number') from error

    def _glob_paths(self, root_dir: str, name: str) -> list[str]:
        result = [
            os.path.join(root_dir, path)
            for path in [
                *glob.glob(f'*/**/{name}*.docx', root_dir=root_dir, recursive=True),
                *glob.glob(f'{name}*.docx', root_dir=root_dir, recursive=False),
            ]
        ]
        if len(result) == 0:
            raise RuntimeError('couldn\'t find paths')
        return result
