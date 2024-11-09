from .dtos import MetricCalculatorDTO, ModelOutputDTO
from .tools import logger
from dataclasses import asdict




class MetricCalculator:
    def __init__(self) -> None:
        self._logger = logger.nest_obj_logger(self)
        
    def calc(
        self,
        data: ModelOutputDTO,
    ) -> MetricCalculatorDTO:
        # TODO: заглушка, тут нужно будет реализовать логику подсчета метрики
        # Пример использования класса
        file_path = '/content/v2.json'  
        data_dict = asdict(data)
        self._logger.debug(f'{data_dict}')
        metric_count = MetricCount(data_dict)
        final_scores = metric_count.run()
        self._logger.debug('1')
        print(final_scores)
        self._logger.debug(f'final score:{final_scores}')
        return MetricCalculatorDTO(
            doc_number=data.doc_number,
            reference_name=data.reference_name,
            difference=data.difference,
            description=data.description,
            compliance_level=data.compliance_level,
            value=final_scores.get('grade'),
        )



import json
import numpy as np

class MetricCount:
    def __init__(self, json):
        self.file_path = json
        self.documents = []
        self._logger = logger.nest_obj_logger(self)

        
    def process_json(self):
        """Обрабатывает JSON-файл и возвращает объекты."""
        with open(self.file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data['objects']
    
    def evaluate_specifications(self, specifications):
        """Оценивает спецификации и подсчитывает категории."""
        documents = {}
        print(specifications)
        
        number = specifications["doc_number"]
            
        if number not in documents:
            documents[number] = {
                "Preconditions": 0,
                "Main Scenario": 0,
                "Postconditions": 0,
                "Alternative Scenario": 0,
                "Exit Conditions": 0
            }
            
        # details = specifications.get("Details", [])
        differences_details = specifications.get("detailed_difference", [])
        self._logger.debug(f'differences_details:{differences_details}')

        for detail in differences_details:
            category = detail.get("category")
            self._logger.debug(f'category:{category}')
            if category in documents[number]:
                documents[number][category] += 1

        results_array = []
        for number, counts in documents.items():
            result_entry = {
                "Number": number,
                "Counts": counts
            }
            results_array.append(result_entry)

        self._logger.debug(f'results_array:{results_array}')
        return results_array

    def evaluate_difference(self, documents):
        """Оценивает различия в спецификациях."""
        paragraph_weights = {
            'Preconditions': 0.3,
            'Main Scenario': 0.25,
            'Postconditions': 0.2,
            'Alternative Scenario': 0.15,
            'Exit Conditions': 0.1
        }

        compliance_scale = {
            'FC': 1,
            'LC': 0.75,
            'PC': 0.5,
            'MN': 0.25,
            'NC': 0
        }

        results = {}

        for document in documents:
            doc_number = document['Number']
            differences = document['Counts']
            
            total_grade = 0
            total_weight = 0

            for category, changes in differences.items():
                if changes >= 5:
                    grade = 'NC'
                elif changes >= 3:
                    grade = 'PC'
                elif changes >= 1:
                    grade = 'LC'
                else:
                    grade = 'FC'  

                numerical_grade = compliance_scale[grade]
                weight = paragraph_weights.get(category, 0)

                total_grade += numerical_grade * weight
                total_weight += weight

            if total_weight > 0:
                overall_grade = total_grade / total_weight  
            else:
                overall_grade = 0

            results['grade'] = overall_grade

        return results

    def run(self):
        """Запускает процесс обработки и оценки."""
        try:
            specifications = self.file_path
            self.documents = self.evaluate_specifications(specifications)
            results = self.evaluate_difference(self.documents)

            full_score = {doc_number: np.round(score, 2) for doc_number, score in results.items()}
            return full_score
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return {}



