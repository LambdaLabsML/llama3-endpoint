# Dockerized deployment for llama 3

Outside of Lambda On-demand instance, a way to ensure correct and consistent environment for the LLM deployment is to use Docker.
Here are the steps to deploy llama 3 with `vllm` on Docker.

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

Add current user to docker group (to avoid using `sudo docker` next)
```bash
sudo usermod -aG docker $USER
newgrp docker
```

Authenticate with Hugging Face to download the model
```bash
huggingface-cli login --token <YOUR_HF_TOKEN>
```

Deploy llama 3 inference backend with `vllm` Docker image.
```bash
MODEL=meta-llama/Meta-Llama-3-70B
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
* Note: `tensor-parallel` is not needed and not recommended for llama-3 8B
