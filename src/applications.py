import argparse
import os

from src.dtos import OutputCreatorDTO
from src.input_reader import InputReader
from src.metric_calculator import MetricCalculator
from src.model_inference import ModelInference
from src.output_creator import OutputCreator


class Application:
    def __init__(self) -> None:
        self._input_reader = InputReader()
        self._model_inference = ModelInference()
        self._metric_calculator = MetricCalculator()
        self._output_creator = OutputCreator()

        self._parser = argparse.ArgumentParser(
            prog='src/main.py',
            description='Приложение проводит анализ комплеанс соответствие документации спецификации',
            allow_abbrev=True,
            exit_on_error=True,
        )

        self._parser.add_argument(
            '-i',
            '--input-file-fpath',
            required=True,
            metavar='file-path',
            help='Путь до .zip файла с документами',
        )

        self._parser.add_argument(
            '-o',
            '--output-file-fpath',
            default='output.xlsx',
            metavar='file-path',
            help='Путь куда сложить результат в формате .xlsx',
        )

        arguments = vars(self._parser.parse_args())

        self._input_file_fpath = arguments['input_file_fpath']
        self._output_file_fpath = arguments['output_file_fpath']

    def run(self) -> None:
        if self._input_file_fpath[-4:] != '.zip':
            raise RuntimeError('Входной файл должен быть в разрешении .zip')
        if self._output_file_fpath[-5:] != '.xlsx':
            raise RuntimeError('Выходной файл должен быть в разрешении .xlsx')
        if not os.path.exists(self._input_file_fpath):
            raise RuntimeError(f'Указанный входной файл не найден: {self._input_file_fpath}')

        input_dto = self._input_reader.extract(self._input_file_fpath)
        assert input_dto.doc_cnt == len(input_dto.result)

        output_dto_result = []
        for input_data in input_dto.result:
            model_dto = self._model_inference.inference(input_data)
            output_dto_result.append(self._metric_calculator.calc(model_dto))

        output_df = self._output_creator.create(
            OutputCreatorDTO(
                result=output_dto_result,
                doc_cnt=input_dto.doc_cnt,
            )
        )

        output_df.to_excel(self._output_file_fpath)
