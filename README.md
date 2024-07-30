# Quickstart

**Please see [the updated instructions for deploying llama 3.1 with Docker](https://github.com/LambdaLabsML/llama3-endpoint/blob/main/DOCKER.md).**


This guide covers the deployment of a LLama 3 inference endpoint on Lambda Cloud.  
The Meta Llama 3 series of large language models (LLMs) was developped and launched by Meta and features generative text models available in 8B and 70B sizes. These open source models are recognized for their state of the art performance in common industry benchmarks.

## Requirements

Gain access to Llama3 model on HuggingFace, specifically:
- [meta-llama/Meta-Llama-3-8B](https://huggingface.co/meta-llama/Meta-Llama-3-8B)
- [meta-llama/Meta-Llama-3-70B](https://huggingface.co/meta-llama/Meta-Llama-3-70B)

Create a HuggingFace token and *make sure to include the llama-3 repositories under the "Repositories permissions" section* (otherwise the token will not have sufficient permission to download the model).

The minimum hardware requirements are as follow (see [meta's recommendations](https://llamaimodel.com/requirements/) for more details):
- 1x GPU node (16GB) for 8B model
- 8x GPU node (32GB) for 70B model

## Setup inference point

The following assumes you are using a GPU node with the adequate GPUs and have the necessary permissions on HuggingFace to access the model.

Create dedicated python environment
```
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install vllm==0.4.3 huggingface-hub==0.23.2 torch==2.3.0
```

Login to HuggingFace
```
huggingface-cli login
```

Start model server (download/cache as necessary).  
For 8B model: 
```
python3 -m vllm.entrypoints.openai.api_server \
  --host=0.0.0.0 \
  --port=8000 \
  --model=meta-llama/Meta-Llama-3-8B
```  
For 70B model (assumes 8x GPU node)
```
python3 -m vllm.entrypoints.openai.api_server \
  --host=0.0.0.0 \
  --port=8000 \
  --model=meta-llama/Meta-Llama-3-70B \
  --tensor-parallel-size 8
```


## Usage

request:
```
curl -X POST http://<node_ip>:8000/v1/completions \
     -H "Content-Type: application/json" \
     -d '{
           "prompt": "What is the name of the capital of France?",
           "model": "meta-llama/Meta-Llama-3-70B",
           "temperature": 0.0,
           "max_tokens": 1
         }'
```

response:
```
{
  "id": "cmpl-d898e2089b7b4855b48e00684b921c95",
  "object": "text_completion",
  "created": 1718221710,
  "model": "meta-llama/Meta-Llama-3-70B",
  "choices": [
    {
      "index": 0,
      "text": " Paris",
      "logprobs": null,
      "finish_reason": "length",
      "stop_reason": null
    }
  ],
  "usage": {
    "prompt_tokens": 11,
    "total_tokens": 12,
    "completion_tokens": 1
  }
}
```
