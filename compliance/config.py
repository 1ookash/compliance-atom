import environs
import pydantic
from pydantic.dataclasses import dataclass

env = environs.Env()
env.read_env()


@dataclass(config=pydantic.ConfigDict(frozen=True, strict=True, extra='forbid'))
class Config:
    llm_url: str = env.str('LLM_URL')


CONFIG = Config()
