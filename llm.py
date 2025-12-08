import os
from langchain_ollama import ChatOllama

llm = None

def _build_llm(model, base_url, temperature, num_ctx, num_predict, timeout):
    return ChatOllama(
        base_url = base_url,
        model = model,
        temperature = temperature,
        num_ctx = num_ctx,
        num_predict = num_predict,
        num_thread = os.cpu_count() or 4,
        request_timeout = timeout,
        keep_alive = "30m",
        stream = False,
    )

def configure(cfg: dict | None = None):
    global llm
    cfg = cfg or {}
    model = cfg.get("model") or os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
    base_url = cfg.get("api_base") or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    temperature = float(cfg.get("temperature", os.getenv("OLLAMA_TEMPERATURE", 0.0)))
    num_ctx = int(os.getenv("OLLAMA_NUM_CTX", "4096"))
    num_predict = int(cfg.get("max_tokens", os.getenv("OLLAMA_NUM_PREDICT", "192")))
    timeout = int(cfg.get("timeout", os.getenv("OLLAMA_TIMEOUT", "45")))
    llm = _build_llm(model, base_url, temperature, num_ctx, num_predict, timeout)

if llm is None:
    configure({})