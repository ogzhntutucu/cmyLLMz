"""
ollama_client.py
----------------
Ollama API üzerinden local LLM ile iletişim.

Model: gemma3:4b (veya phi4-mini)
Endpoint: http://localhost:11434

Streaming destekli — Streamlit arayüzünde token'lar birer birer ekrana düşer.
"""

import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")


def chat(system_prompt: str, user_prompt: str, stream: bool = False):
    """
    Ollama ile sohbet.
    
    Args:
        system_prompt: Sistem prompt'u
        user_prompt: Kullanıcı prompt'u
        stream: True ise generator döndürür (streaming)
    
    Returns:
        stream=False: Tam cevap string
        stream=True: Token generator
    """
    # TODO: Implement
    # import ollama
    # response = ollama.chat(
    #     model=OLLAMA_MODEL,
    #     messages=[
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": user_prompt}
    #     ],
    #     stream=stream
    # )
    pass


def is_available() -> bool:
    """Ollama servisinin çalışıp çalışmadığını kontrol et."""
    # TODO: Implement
    pass
