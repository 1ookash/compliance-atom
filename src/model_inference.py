from src.dtos import ModelInputDTO, ModelOutputDTO


class ModelInference:
    def inference(self, data: ModelInputDTO) -> ModelOutputDTO:
        raise NotImplementedError()
