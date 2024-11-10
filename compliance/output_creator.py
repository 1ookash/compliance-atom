from datetime import datetime

import pandas

from .dtos import OutputCreatorDTO


class OutputCreator:
    def create(self, data: OutputCreatorDTO) -> pandas.DataFrame:
        assert data.doc_cnt == len(data.result)
        result = {
            'Number': [0] * data.doc_cnt,
            'Name': [''] * data.doc_cnt,
            'Differences': [''] * data.doc_cnt,
            'Description': [''] * data.doc_cnt,
            'Complience Level': [''] * data.doc_cnt,
            'Value': [0.0] * data.doc_cnt,
            'Timestamp': [datetime.now()] * data.doc_cnt,
        }

        for i, res in enumerate(data.result):
            result['Number'][i] = res.doc_number
            result['Name'][i] = res.reference_name
            result['Differences'][i] = res.difference
            result['Description'][i] = res.description
            result['Complience Level'][i] = res.compliance_level
            result['Value'][i] = res.value

        return pandas.DataFrame(data=result)
