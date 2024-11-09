from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

#TODO: сделать авторизацию по токену
#TODO: вынести пути в конфиг (закрыть порты ufw)
#TODO: сделать разные роуты для сохранения диалога/ нового

# Initialize FastAPI app
app = FastAPI()

# Load Qwen-like model and tokenizer (adjust paths/names as needed)
model_name = "Qwen/Qwen2.5-7B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name,
                                          torch_dtype=torch.float16)
model = AutoModelForCausalLM.from_pretrained('/home/user1/.cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct/snapshots/bb46c15ee4bb56c5b63245ef50fd7637234d6f75').to('cuda:0')


# Pydantic model for request
class Query(BaseModel):
    system_promt: str
    user_promt: str


@app.post("/ask")
def ask_question(query: Query):
    """
    Handle user queries and generate responses. Each query is treated as a standalone interaction.
    """
    try:
        # Create a standalone dialog context for each query
        messages = [
            {"role": "system", "content": query.system_promt},
            {"role": "user", "content": query.user_promt}
        ]

        # Convert messages to input text for the model
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        # Tokenize and prepare inputs for the model
        model_inputs = tokenizer([text], return_tensors="pt").to('cuda:0')
        # Generate the response
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=512,
            do_sample=False,  # Optional: enable sampling for more varied responses
            temperature=0.7  # Adjust temperature for creativity (lower = more focused, higher = more creative)
        )
        
        # Decode generated response
        response = tokenizer.decode(generated_ids[0], 
                                    skip_special_tokens=True)
        
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def read_root():
    return {"message": "Welcome to the QWEN2.5-7B AI API!"}
