import os
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llama import Llama

app = FastAPI()

class TextCompletionRequest(BaseModel):
    prompts: List[str]
    temperature: float = 0.6
    top_p: float = 0.9
    max_seq_len: int = 128
    max_gen_len: int = 64
    max_batch_size: int = 4

class TextCompletionResponse(BaseModel):
    prompts: List[str]
    completions: List[str]

# Initialize the Llama model (lazy initialization)
llama_model = None

@app.on_event("startup")
def load_model():
    global llama_model
    try:
        # Set environment variables for PyTorch distributed
        os.environ['RANK'] = '0'
        os.environ['WORLD_SIZE'] = '1'
        os.environ['MASTER_ADDR'] = 'localhost'
        os.environ['MASTER_PORT'] = '29500'

        llama_model = Llama.build(
            ckpt_dir="Meta-Llama-3-8B-Instruct/",
            tokenizer_path="Meta-Llama-3-8B-Instruct/tokenizer.model",
            max_seq_len=512,
            max_batch_size=6
        )
    except Exception as e:
        raise RuntimeError(f"Failed to load model: {str(e)}")

@app.post("/text_completion", response_model=TextCompletionResponse)
async def text_completion(request: TextCompletionRequest):
    global llama_model
    if llama_model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        results = llama_model.text_completion(
            request.prompts,
            max_gen_len=request.max_gen_len,
            temperature=request.temperature,
            top_p=request.top_p,
        )
        completions = [result['generation'] for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

    return TextCompletionResponse(
        prompts=request.prompts,
        completions=completions
    )

# Run the app with the command: uvicorn app:app --reload
