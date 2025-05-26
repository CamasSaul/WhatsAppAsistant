from llama_cpp import Llama
from llama_cpp import Llama


llm = Llama(model_path=r"C:\Users\camas\.lmstudio\models\lmstudio-community\Qwen3-8B-GGUF\Qwen3-8B-Q4_K_M.gguf", verbose=True, use_cuda=True,  n_gpu_layers=6)