# Quickstart

See [./README.md](llama3 README.md) for download instructions.
Rest of this guide assumes you installed all llama3 dependencies, including `requirements.txt`


Issue fix on lambda cloud (details in [HF discussion](https://huggingface.co/meta-llama/Meta-Llama-3-8B/discussions/34)):
```
python3 -m pip install --upgrade torch 
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

