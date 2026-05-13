"""
openai_client.py
----------------
OpenAI gpt-4o-mini ile RAG cevap üretimi. Streaming destekli.
"""

from openai import OpenAI

OPENAI_API_KEY = "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"
OPENAI_MODEL = "gpt-5.4-mini"

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


def chat(
    system_prompt: str,
    user_prompt: str,
    stream: bool = False,
    history: list[dict] | None = None,
):
    """
    OpenAI ile sohbet.

    history: [{"role": "user"|"assistant", "content": "..."}] — önceki turlar
    Returns:
        stream=False: Tam cevap string
        stream=True: Token generator (Streamlit st.write_stream ile uyumlu)
    """
    client = get_client()
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_prompt})
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.3,
        stream=stream,
    )

    if stream:
        def _gen():
            for chunk in response:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        return _gen()
    else:
        return response.choices[0].message.content
