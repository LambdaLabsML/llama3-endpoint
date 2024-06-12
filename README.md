# Quickstart

## Requirements

Gain access to Llama3 model on HF, specifically:
- [meta-llama/Meta-Llama-3-8B](https://huggingface.co/meta-llama/Meta-Llama-3-8B)
- [meta-llama/Meta-Llama-3-70B](https://huggingface.co/meta-llama/Meta-Llama-3-70B)

Create a HF token and *make sure to include the llama-3 repositories under the "Repositories permissions" section* (otherwise the token will not have sufficient permission to download the model).

The minimum hardware requirements is (cf [meta's recommendations](https://llamaimodel.com/requirements/)):
- 1x GPU node (16GB) for 8B model 
- 8x GPU node (32GB) for 70B model

We will be using ngrok for exposing the model server to the internet, which requires an account (cf [ngrok](https://ngrok.com/)).
See instruction on ngrok website to [install the ngrok client on your machine](https://dashboard.ngrok.com/get-started/setup/linux).

## Setup inference point

The following assume I am running on a GPU node with the adequate number of GPUs and the necessary permissions to access the model.
After starting a `ssh` session on the node, we will be using two `screen` sessions (start a new one with `screen` and detach with `Ctrl+A, D`).
* One screen session for the model server
* One screen session for the port forwarding service (eg ngrok)

### Model server

Create a new screen session for the model server
```
screen -S model_server
```

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

Start model server (download/cache as necessary) in a dedicated `screen` session.  
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

### Port forwarding

Create a new screen session for the model server
```
screen -S port_forwarding
```

Start ngrok port forwarding service
```
ngrok http 8000
```

You should see a screen like this one:
```
ngrok                                                           (Ctrl+C to quit)
                                                                                
Try our new Traffic Inspector: https://ngrok.com/r/ti                           
                                                                                
Session Status                online                                            
Account                       <account-email> (Plan: Free)                    
Version                       3.10.1                                            
Region                        United States (us)                                
Latency                       8ms                                               
Web Interface                 http://127.0.0.1:4040                             
Forwarding                    https://123-456-789.ngrok-free.app -> http
                                                                                
Connections                   ttl     opn     rt1     rt5     p50     p90       
                              1160    0       0.00    0.00    5.31    5.57 
```

In this case the endpoint will be exposed at `https://123-456-789.ngrok-free.app`.


## Usage

```
curl -X POST https://0dc3-207-211-172-86.ngrok-free.app/v1/completions \
     -H "Content-Type: application/json" \
     -d '{
           "prompt": "What is the name of the capital of France?",
           "model": "meta-llama/Meta-Llama-3-70B",
           "temperature": 0.1,
           "max_tokens": 1
         }'
```

response
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