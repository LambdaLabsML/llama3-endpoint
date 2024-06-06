# Quickstart

## Requirements

Gain access to Llama3 model on HF, specifically:
- [meta-llama/Meta-Llama-3-8B](https://huggingface.co/meta-llama/Meta-Llama-3-8B)
- [meta-llama/Meta-Llama-3-70B](https://huggingface.co/meta-llama/Meta-Llama-3-70B)

Create a HF token and *make sure to include the two repositories under the "Repositories permissions" section* (otherwise the model download will fail!).

The minimum hardware requirements is:
- 1x GPU node for 8B model 
- 8x GPU node for 70B model

## Setup inference point (Docker)

Note: putting Docker development on-hold for now because using a shared machine and am instructed to avoid any system-wide changes.

```
docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --env "HUGGING_FACE_HUB_TOKEN=<secret>" \
    -p 8000:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    --model meta-llama/Meta-Llama-3-70B
```

## Setup inference point (manually)

The following assume I am running on a GPU node with the adequate number of GPUs and the necessary permissions to access the model.

Create dedicated python env
```
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt 
```

Login to huggingface
```
huggingface-cli login
```

Start model server (download/cache as necessary).  
For 8B model: 
```
python3 -m vllm.entrypoints.openai.api_server \
  --host=127.0.0.1 \
  --port=8000 \
  --model=meta-llama/Meta-Llama-3-8B
```  
For 70B model (assumes 8x GPU node)
```
python3 -m vllm.entrypoints.openai.api_server \
  --host=127.0.0.1 \
  --port=8000 \
  --model=meta-llama/Meta-Llama-3-70B
  --tensor-parallel-size 8
```

Attempt to limit memory allocated DID NOT WORK
1. Mixed precision
2. Quantization

Mixed precision:
```
python3 -m vllm.entrypoints.openai.api_server \
  --host=127.0.0.1 \
  --port=8000 \
  --model=meta-llama/Meta-Llama-3-70B \
  --dtype=float16 \
  --max_seq_len=4096 \
  --tensor_parallel_size=1 \
  --kv_cache_dtype=float16
```

Quantization:
```
python3 -m vllm.entrypoints.openai.api_server \
  --host=127.0.0.1 \
  --port=8000 \
  --model=meta-llama/Meta-Llama-3-70B \
  --dtype=float16 \
  --quantization=INT8 \
  --max_seq_len=4096 \
  --tensor_parallel_size=1
```
Start port fowarding service (eg ngok)
```
ngrok http 8000 (update this)
```


## Usage

curl (quick test):
```
```


python:
```
@traceable(run_type="llm")
def invoke_llm_local(user_input: str):

    openai_api_key = "EMPTY"
    openai_api_base = "https://<host>/v1"
    client = OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_base,
    )
    return client.completions.create(
            prompt= user_input,
            model="meta-llama/Meta-Llama-3-8B",
            temperature=0.0,
        )
```


-----


# DEPRECATED



---

See [./README.md](llama3 README.md) for download instructions.
Rest of this guide assumes you installed all llama3 dependencies, including `requirements.txt`


Issue fix on lambda cloud (details in [HF discussion](https://huggingface.co/meta-llama/Meta-Llama-3-8B/discussions/34)):
```
python3 -m pip install --upgrade torch 
```

### VLLM inference acceleration

```
python3 -m pip install vllm
```


### Instructions to run the API

Install FastAPI and Uvicorn if you haven't already:
```bash
pip install fastapi uvicorn
```

Start the FastAPI server:
```bash
uvicorn app:app --reload
```

### Endpoint
- **POST** `/text_completion`
  - **Request Body** (JSON):
    ```json
    {
      "prompts": ["Prompt 1", "Prompt 2"],
      "temperature": 0.6,
      "top_p": 0.9,
      "max_seq_len": 128,
      "max_gen_len": 64,
      "max_batch_size": 4
    }
    ```
  - **Response Body** (JSON):
    ```json
    {
      "prompts": ["Prompt 1", "Prompt 2"],
      "completions": ["Completion 1", "Completion 2"]
    }
    ```

With `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/text_completion" -H "Content-Type: application/json" -d '{
  "prompts": ["I believe the meaning of life is", "Simply put, the theory of relativity states that"],
  "temperature": 0.6,
  "top_p": 0.9,
  "max_seq_len": 128,
  "max_gen_len": 64,
  "max_batch_size": 4
}'
```


```bash
curl -X POST "https://49c9-129-146-111-221.ngrok-free.app/text_completion" -H "Content-Type: application/json" -d '{
  "prompts": ["I believe the meaning of life is", "Simply put, the theory of relativity states that"],
  "temperature": 0.6,
  "top_p": 0.9,
  "max_seq_len": 128,
  "max_gen_len": 64,
  "max_batch_size": 4
}'
```

