import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from .config import CONFIG

# TODO: сделать авторизацию по токену
# TODO: вынести пути в конфиг (закрыть порты ufw)
# TODO: сделать разные роуты для сохранения диалога/ нового

app = FastAPI()

tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen2.5-7B-Instruct', torch_dtype=torch.float16)
model = AutoModelForCausalLM.from_pretrained(CONFIG.llm_absolute_fpath).to('cuda:0')


class Query(BaseModel):
    system_promt: str
    user_promt: str


@app.post('/ask')
def ask_question(query: Query):
    try:
        messages = [
            {'role': 'system', 'content': query.system_promt},
            {'role': 'user', 'content': query.user_promt},
        ]

        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        model_inputs = tokenizer([text], return_tensors='pt').to('cuda:0')  # type: ignore
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=2046,
            do_sample=True,
            temperature=0.7,
        )
        generated_ids = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = tokenizer.decode(
            generated_ids[0],
            skip_special_tokens=True,
        )

        return {'answer': response}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.get('/')
def read_root():
    return {'message': 'Welcome to the QWEN2.5-7B AI API!'}
