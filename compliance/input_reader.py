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


class InputReader:
    def extract(self, input_file_path: str) -> InputReaderDTO:
        source_result = {}
        reference_result = {}
        result = []

        with tempfile.TemporaryDirectory() as tempdir:
            zipfile.ZipFile(input_file_path).extractall(tempdir)

            for source_path in self._glob_paths(root_dir=tempdir, pathname='*/*/*/SSTS*.docx'):
                source_result[self._extract_doc_number(source_path)] = self._read_docx(source_path)

            for reference_path in self._glob_paths(root_dir=tempdir, pathname='*/*/*/UC*.docx'):
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
                        source=None,
                        doc_number=key,
                        reference_name=reference_name,
                    )
                )
                continue
            result.append(
                ModelInputDTO(
                    reference=value,
                    source=source,
                    doc_number=key,
                    reference_name=reference_name,
                )
            )

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

    def _glob_paths(self, root_dir: str, pathname: str) -> list[str]:
        result = [os.path.join(root_dir, path) for path in glob.glob(pathname, root_dir=root_dir)]
        if len(result) == 0:
            raise RuntimeError('couldn\'t find paths')
        return result
