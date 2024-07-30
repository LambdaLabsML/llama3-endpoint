# Serving of llama 3.1 (8B, 70B and 405B FP8)

This guide covers serving llama 3.1 on a multi-GPU single node environment.

Hardware requirements
| Model              | Instance type       |
|--------------------|----------------|
| [llama 3.1 8B](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct)       | 1x A100 or 1x H100  |
| [llama 3.1 70B](https://huggingface.co/meta-llama/Meta-Llama-3.1-70B-Instruct)      | 8x A100 or 8x H100  |
| [llama 3.1 405B FP8](https://huggingface.co/meta-llama/Meta-Llama-3.1-405B-Instruct-FP8) | 8x H100             |


## Install Docker and NVIDIA Container Toolkit

*Note: Skip this step if already installed, e.g. if using Lambda Cloud.*

Setup Docker:
```bash
sudo apt-get update
sudo apt-get install -y curl gnupg
sudo apt install podman-docker
```

Add the NVIDIA package repositories:
```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
```

Install the NVIDIA Container Toolkit
```bash
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

## Configure NVIDIA Container Toolkit
```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

## Add Current User to Docker Group

```bash
sudo usermod -aG docker $USER
newgrp docker
```

## Download the model in advance (recommended)

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

## Serve model

### Download the model in before serving

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
