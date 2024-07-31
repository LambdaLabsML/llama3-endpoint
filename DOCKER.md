# Single node serving of llama 3.1 (8B, 70B, 405B FP8)

This guide covers serving llama 3.1 in 8B, 70B and 405B FP8 on a multi-GPU single node environment. 

## Models

We recommend the instruct fine-tuned models for most users and will refer to these models by default going forward.  
We use the FP8 quantized 405B models for this guide as the non quantized 405B model requires a multi-node environment. Checkout can out [our 1cc deployment guide for 405B](https://docs.lambdalabs.com/1-click-clusters/serving-llama-3.1-405b-on-a-lambda-1-click-cluster) for more information on deploying llama 3.1 405B.

## Hardware requirements
| Model              | Instance type       |
|--------------------|----------------|
| [llama 3.1 8B](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct)       | 1xA100 or 1xH100  |
| [llama 3.1 70B](https://huggingface.co/meta-llama/Meta-Llama-3.1-70B-Instruct)      | 8xA100 or 8xH100  |
| [llama 3.1 405B FP8](https://huggingface.co/meta-llama/Meta-Llama-3.1-405B-Instruct-FP8) | 8xH100             |

*07/30/2024: Performance benchmark for the different model and instance types [here](https://github.com/LambdaLabsML/llama3-endpoint/tree/main/benchmark_logs).*  
*This guide will be updated shortly with configuration recommendation to get the most performance out of your setup.*

## Serving guide

1. [Setup Docker](#setup-docker)
2. [Serve the model](#serve-the-model)

### Setup Docker

*The rest of this guide assumes that your environment has Docker and NVIDIA Container Toolkit installed, as is the case for Lambda Cloud instances. Please refer to the [Docker guide](https://docs.docker.com/engine/install/ubuntu/) and to the [NVIDIA guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) if you are not using Lambda Cloud and need to install these requirements.*

Add Current User to Docker Group
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Serve the model

Create a Hugging Face token and make sure to include the llama 3.1 repositories under the "Repositories permissions" section (otherwise the token will not have sufficient permission to download the model).

Authenticate with Hugging Face to download the model
```bash
huggingface-cli login --token <YOUR_HF_TOKEN>
```

Set model name:
```bash
MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct
#MODEL=meta-llama/Meta-Llama-3.1-70B-Instruct
#MODEL=meta-llama/Meta-Llama-3.1-405B-Instruct-FP8
```

Deploy the inference backend with a `vllm` Docker container.
```bash
docker run \
     --gpus all \
     -v ~/.cache/huggingface:/root/.cache/huggingface \
     -p 8000:8000 \
     --ipc=host \
     vllm/vllm-openai:latest \
     --model {MODEL} \
     --swap-space 16 \
     --disable-log-requests \
     # --tensor-parallel-size 4 \ # for parallelizing across 4 GPUs
     # --max-model-len 8192 # limit context len to 8K (cf config recommendation below)
```

## Config recommendations

| Model                                                                                     | Tensor Parallel                            | Comment                                                    | Instance Type          |
|-------------------------------------------------------------------------------------------|--------------------------------------------|-----------------------------------------------------------------|------------------------|
| [llama 3.1 8B](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct)              | N/A        | Do not parallelize                                           | 1xA100 or 1xH100       |
| [llama 3.1 70B](https://huggingface.co/meta-llama/Meta-Llama-3.1-70B-Instruct)            | `--tensor-parallel-size 4`                 | Default context length of 128K tokens requires a minimum of 4x GPUs (80GB each) | 8xA100 or 8xH100       |
| [llama 3.1 70B](https://huggingface.co/meta-llama/Meta-Llama-3.1-70B-Instruct)            | `--tensor-parallel-size 2 --max-model-len 8192` | Can run on 2x GPUs (80GB each) if limiting context length to 8K token | 8xA100 or 8xH100       |
| [llama 3.1 405B FP8](https://huggingface.co/meta-llama/Meta-Llama-3.1-405B-Instruct-FP8)  | `--tensor-parallel-size 8`                 | Default context length of 128K tokens requires a minimum of 8x GPUs (80GB each) | 8xH100 (no fp8 cores in A100s)                 |



