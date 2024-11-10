import argparse
import os
import sqlite3
from datetime import datetime

from pydantic import RootModel

from .config import CONFIG
from .dtos import ModelOutputDTO, OutputCreatorDTO
from .input_reader import InputReader
from .metric_calculator import MetricCalculator
from .model_inference import ModelInference
from .output_creator import OutputCreator
from .tools import logger


class Application:
    def __init__(self) -> None:
        logger.start_streams(log_root='root', stderr_f=False)
        self._logger = logger.nest_obj_logger(self)

        self._db_connect = sqlite3.connect(CONFIG.db_fpath)
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

        self._model_dto_dir_path = os.path.join(
            'data', f'app_run_{datetime.strftime(datetime.now(), "%Y_%m_%dT%H_%M_%S")}'
        )
        if not os.path.exists(self._model_dto_dir_path):
            os.makedirs(self._model_dto_dir_path)

        self._logger.info(
            'init',
            params_please={
                'input file fpath': self._input_file_fpath,
                'output file fpath': self._output_file_fpath,
                'model dto dir path': self._model_dto_dir_path,
            },
        )

    def run(self) -> None:
        if self._input_file_fpath[self._input_file_fpath.rfind('.') + 1 :] != 'zip':
            self._logger.warning(
                'Входной файл должен быть в разрешении .zip',
                params_please={'input file fpath': self._input_file_fpath},
            )
            raise RuntimeError('Входной файл должен быть в разрешении .zip')
        if self._output_file_fpath[self._output_file_fpath.rfind('.') + 1 :] not in ('xlsx', 'csv'):
            self._logger.warning(
                'Выходной файл должен быть в разрешении .xlsx или .csv',
                params_please={'output file fpath': self._output_file_fpath},
            )
            raise RuntimeError('Выходной файл должен быть в разрешении .xlsx или .csv')
        if not os.path.exists(self._input_file_fpath):
            self._logger.warning(
                'Указанный входной файл не найден',
                params_please={'input file fpath': self._input_file_fpath},
            )
            raise RuntimeError(f'Указанный входной файл не найден: {self._input_file_fpath}')

        self._logger.debug('run begin')

        input_dto = self._input_reader.extract(self._input_file_fpath)
        self._logger.debug(
            'input dto created',
            params_please={'input dto id': id(input_dto), 'document count': input_dto.doc_cnt},
        )
        assert input_dto.doc_cnt == len(input_dto.result)

        output_dto_result = []
        for input_data in input_dto.result:
            model_dto = self._model_inference.inference(input_data)
            with open(
                os.path.join(self._model_dto_dir_path, f'{model_dto.doc_number}-dto.json'),
                'w',
                encoding='utf-8',
            ) as file:
                file.write(RootModel[ModelOutputDTO](model_dto).model_dump_json())
            self._logger.debug(
                'model dto saved', params_please={'document number': model_dto.doc_number}
            )
            output_dto_result.append(self._metric_calculator.calc(model_dto))

        output_df = self._output_creator.create(
            OutputCreatorDTO(
                result=output_dto_result,
                doc_cnt=input_dto.doc_cnt,
            )
        )

        output_df.to_sql(name='compliance', con=self._db_connect, if_exists='append', index=False)
        self._db_connect.commit()
        self._db_connect.close()
        if self._output_file_fpath[self._output_file_fpath.rfind('.') + 1 :] == 'xlsx':
            output_df.to_excel(self._output_file_fpath, index=False)
        if self._output_file_fpath[self._output_file_fpath.rfind('.') + 1 :] == 'csv':
            output_df.to_csv(self._output_file_fpath, index=False, sep=',')

        self._logger.debug('run end')

        logger.stop()
