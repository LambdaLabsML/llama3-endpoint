# import os
# from typing import List
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from llama import Llama

# app = FastAPI()

# class TextCompletionRequest(BaseModel):
#     prompts: List[str]
#     temperature: float = 0.6
#     top_p: float = 0.9
#     max_seq_len: int = 128
#     max_gen_len: int = 64
#     max_batch_size: int = 4

# class TextCompletionResponse(BaseModel):
#     prompts: List[str]
#     completions: List[str]

# # Initialize the Llama model (lazy initialization)
# llama_model = None

# @app.on_event("startup")
# def load_model():
#     global llama_model
#     try:
#         # Set environment variables for PyTorch distributed
#         os.environ['RANK'] = '0'
#         os.environ['WORLD_SIZE'] = '1'
#         os.environ['MASTER_ADDR'] = 'localhost'
#         os.environ['MASTER_PORT'] = '29500'

#         llama_model = Llama.build(
#             ckpt_dir="Meta-Llama-3-8B-Instruct/",
#             tokenizer_path="Meta-Llama-3-8B-Instruct/tokenizer.model",
#             max_seq_len=512,
#             max_batch_size=6
#         )
#     except Exception as e:
#         raise RuntimeError(f"Failed to load model: {str(e)}")

# @app.post("/text_completion", response_model=TextCompletionResponse)
# async def text_completion(request: TextCompletionRequest):
#     global llama_model
#     if llama_model is None:
#         raise HTTPException(status_code=500, detail="Model not loaded")

#     try:
#         results = llama_model.text_completion(
#             request.prompts,
#             max_gen_len=request.max_gen_len,
#             temperature=request.temperature,
#             top_p=request.top_p,
#         )
#         completions = [result['generation'] for result in results]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

#     return TextCompletionResponse(
#         prompts=request.prompts,
#         completions=completions
#     )

# # Run the app with the command: uvicorn app:app --reload

import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from vllm import vLLMServer, SamplingParams

class RequestHandler(BaseHTTPRequestHandler):
    vllm_server = None

    @classmethod
    def load_model(cls):
        try:
            # Set environment variables for PyTorch distributed
            os.environ['RANK'] = '0'
            os.environ['WORLD_SIZE'] = '1'
            os.environ['MASTER_ADDR'] = 'localhost'
            os.environ['MASTER_PORT'] = '29500'

            model_path = "Meta-Llama-3-8B-Instruct/models"
            tokenizer_path = "Meta-Llama-3-8B-Instruct/tokenizer.model"

            cls.vllm_server = vLLMServer(
                model_path=model_path,
                tokenizer_path=tokenizer_path,
                max_seq_len=512,
                max_batch_size=6
            )
            cls.vllm_server.run(host="0.0.0.0", port=8080, block=False)
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {str(e)}")

    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        if self.path == '/text_completion':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data)

            try:
                prompts = request_data['prompts']
                temperature = request_data.get('temperature', 0.6)
                top_p = request_data.get('top_p', 0.9)
                max_gen_len = request_data.get('max_gen_len', 64)

                sampling_params = SamplingParams(
                    max_gen_len=max_gen_len,
                    temperature=temperature,
                    top_p=top_p
                )
                results = self.vllm_server.text_completion(
                    prompts,
                    sampling_params=sampling_params
                )
                completions = [result['generation'] for result in results]

                response = {
                    'prompts': prompts,
                    'completions': completions
                }
                self._set_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self._set_headers(500)
                response = {'detail': f'Text generation failed: {str(e)}'}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self._set_headers(404)
            response = {'detail': 'Not Found'}
            self.wfile.write(json.dumps(response).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    RequestHandler.load_model()
    run()
