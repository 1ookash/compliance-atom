from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer

#TODO: сделать авторизацию по токену
#TODO: вынести пути в конфиг (закрыть порты ufw)
#TODO: сделать разные роуты для сохранения диалога/ нового

# Initialize FastAPI app
app = FastAPI()

# Load Qwen-like model and tokenizer (adjust paths/names as needed)
model_name = "Qwen/Qwen2.5-14B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained('/home/user1/.cache/huggingface/hub/models--Qwen--Qwen2.5-14B-Instruct/snapshots/cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8')


# Pydantic model for request
class Query(BaseModel):
    system_promt: str
    user_promt: str


@app.post("/ask")
def ask_question(query: Query):
    try:
        messages = [
            {"role": "system", "content": query.system_promt},
            {"role": "user", "content": query.user_promt}
        ]
        text = tokenizer.apply_chat_template(messages,
                                             tokenize=False,
                                             add_generation_prompt=True)
        model_inputs = tokenizer([text], return_tensors="pt").to('cuda')
        generated_ids = model.generate(**model_inputs,
                                       max_new_tokens=512
                                       )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        # outputs = model.generate(inputs, max_length=200)
        # response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def read_root():
    return {"message": "Welcome to the QWEN2.5-14b AI API!"}
