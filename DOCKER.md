# Single node serving of llama 3.1 (8B, 70B, 405B FP8)

This guide covers serving llama 3.1 in 8B, 70B and 405B FP8 on a multi-GPU single node environment. 

## Models

We use the FP8 quantized 405B models for this guide as the non quantized model requires a multi-node environment. Checkout out [this guide](https://docs.lambdalabs.com/1-click-clusters/serving-llama-3.1-405b-on-a-lambda-1-click-cluster) for deploying the non quantized llama 3.1 405B model on a Lambda 1cc cluster.  
We recommend the instruct fine-tuned models for most users and will refer to these models by default going forward.


## Hardware requirements
| Model              | Instance type       |
|--------------------|----------------|
| [llama 3.1 8B](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct)       | 1x A100 or 1x H100  |
| [llama 3.1 70B](https://huggingface.co/meta-llama/Meta-Llama-3.1-70B-Instruct)      | 8x A100 or 8x H100  |
| [llama 3.1 405B FP8](https://huggingface.co/meta-llama/Meta-Llama-3.1-405B-Instruct-FP8) | 8x H100             |

* *07/30/2024: Performance benchmark for the different model and instance types [here](https://github.com/LambdaLabsML/llama3-endpoint/tree/main/benchmark_logs).*  
* *This guide will be updated shortly with configuration recommendation to get the most performance out of your setup.*

## Serving guide

Steps:
* [Setup Docker and NVIDIA Container Toolkit](#setup-docker-and-nvidia-container-toolkit)
* [Serve the model](#serve-the-model)

## Setup Docker and NVIDIA Container Toolkit

Install Docker and NVIDIA Container Toolkit *(skip this step on Lambda Cloud)*.
```bash
# Install Docker
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Install the NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
```

Configure NVIDIA Container Toolkit
```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Add Current User to Docker Group
```bash
sudo usermod -aG docker $USER
newgrp docker
```


## Serve the model

### Download the model in advance (recommended)

Authenticate with Hugging Face to download the model
```bash
huggingface-cli login --token <YOUR_HF_TOKEN>
```

Download the model:
```bash
huggingface-cli dowload model meta-llama/Meta-Llama-3.1-70B-Instruct
```

The model will be saved to:
```
`~/.cache/huggingface/hub/models/`
```

If you have already downloaded the model in the previous step, then set the model path **as it will be in the Docker container**.
For example, if model path on the host is like `~/.cache/huggingface/`
```bash
MODEL=
```

If you have not dowloaded the model already, it will be downloaded upon serving.

Just make sure you correctly authenticated.
```bash
huggingface-cli login --token <YOUR_HF_TOKEN>
```

### Deployment

Deploy the inference backend with a `vllm` Docker container.
```bash
MODEL=meta-llama/Meta-Llama-3.1-70B
docker run \
     --runtime nvidia \
     --gpus all \
     -v ~/.cache/huggingface:/root/.cache/huggingface \
     -p 8000:8000 \
     --ipc=host \
     vllm/vllm-openai:latest \
     --model {MODEL} \
     --swap-space 16 \
     --disable-log-requests \
     --tensor-parallel-size 8 # for parallelize over 8 GPUs
```
Note: On H100 and on A100 instances, `--tensor-parallel-size 8` is not needed and not recommended for llama 3 8B, but is for llama 3 70B.
