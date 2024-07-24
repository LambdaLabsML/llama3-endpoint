# Benchmarking step-by-step

This guide covers running inference benchmark for llama3.
It can be broken down into two steps:
1. Deploy the inference server
2. Run the benchmark

Benchmark results will then be printed to stdout.

Note: run the benchmark code on the inference server.

Clone benchmark code
```bash
cd ~
git clone https://github.com/vllm-project/vllm.git
```

Download dataset
```bash
cd ~
wget https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered/resolve/main/ShareGPT_V3_unfiltered_cleaned_split.json
```

Create dedicated python environment
``` bash
apt install python3.10-venv
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install vllm==0.5.0.post1 huggingface-hub==0.23.2 torch==2.3.0
```

Login to HF
```bash
huggingface-cli login
```


Deploy llama3 server side

8B model
```bash
python3 -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Meta-Llama-3-8B \
    --swap-space 16 \
    --disable-log-requests
```

* Add --tensor-parallel-size 8 for parallelizing on 8 GPUs

70B model
```bash
python3 -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Meta-Llama-3-70B \
    --tensor-parallel-size 8 \
    --swap-space 16 \
    --disable-log-requests
```


Run benchmark client side (same machine)
```bash
python3 vllm/benchmarks/benchmark_serving.py \
    --backend vllm \
    --host localhost \
    --port 8000 \
    --model meta-llama/Meta-Llama-3-8B \
    --dataset-name sharegpt \
    --dataset-path ~/ShareGPT_V3_unfiltered_cleaned_split.json
```

