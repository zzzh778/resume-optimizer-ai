from abc import ABC, abstractmethod

from openai import OpenAI

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, LLM_PROVIDER

_token_usage_log = []


class LLMError(Exception):
    pass


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        ...


class DeepSeekProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str, base_url: str):
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY is not set")
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    def generate(self, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                timeout=30,
            )
            usage = response.usage
            if usage:
                _token_usage_log.append({
                    "model": self._model,
                    "input_tokens": usage.prompt_tokens or 0,
                    "output_tokens": usage.completion_tokens or 0,
                    "total_tokens": usage.total_tokens or 0,
                })
            return response.choices[0].message.content
        except Exception as e:
            msg = str(e)
            if "401" in msg or "auth" in msg.lower():
                raise LLMError("API Key 无效，请检查环境变量 DEEPSEEK_API_KEY") from e
            if "timeout" in msg.lower() or "timed out" in msg.lower():
                raise LLMError("AI服务响应超时，请稍后重试") from e
            if "connection" in msg.lower() or "connect" in msg.lower():
                raise LLMError("网络连接失败，请检查网络后重试") from e
            raise LLMError(f"AI服务暂时不可用，请稍后重试") from e


def pop_token_usage():
    data = list(_token_usage_log)
    _token_usage_log.clear()
    return data


def create_llm_provider() -> BaseLLMProvider:
    if LLM_PROVIDER == "deepseek":
        return DeepSeekProvider(
            api_key=DEEPSEEK_API_KEY,
            model=DEEPSEEK_MODEL,
            base_url=DEEPSEEK_BASE_URL,
        )
    raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")
