"""
gemini_client.py
----------------
Google Gemini API üzerinden bulut LLM ile iletişim.

Model: gemini-2.5-flash
API: Google AI Studio (ücretsiz tier)

Hem RAG cevap üretimi hem de enrichment (veri zenginleştirme) için kullanılır.
"""

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"


def configure():
    """Gemini API'yi yapılandır."""
    # TODO: Implement
    # import google.generativeai as genai
    # genai.configure(api_key=GEMINI_API_KEY)
    pass


def chat(system_prompt: str, user_prompt: str, stream: bool = False):
    """
    Gemini ile sohbet.
    
    Args:
        system_prompt: Sistem prompt'u
        user_prompt: Kullanıcı prompt'u
        stream: True ise generator döndürür (streaming)
    
    Returns:
        stream=False: Tam cevap string
        stream=True: Token generator
    """
    # TODO: Implement
    # import google.generativeai as genai
    # configure()
    # model = genai.GenerativeModel(GEMINI_MODEL)
    # response = model.generate_content(
    #     system_prompt + "\n\n" + user_prompt,
    #     stream=stream
    # )
    pass


def generate_json(prompt: str) -> dict:
    """
    Gemini'den JSON formatında cevap al (enrichment için).
    
    JSON parse hatası durumunda retry mekanizması içerir.
    """
    # TODO: Implement
    pass


def is_available() -> bool:
    """API anahtarının ayarlanıp ayarlanmadığını kontrol et."""
    return bool(GEMINI_API_KEY)
