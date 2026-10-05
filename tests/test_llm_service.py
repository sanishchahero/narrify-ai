import pytest
from unittest.mock import patch, MagicMock

from app.services.llm import LLMService, _clean_json_output


def test_clean_json_output():
    raw_markdown = '```json\n{"title": "Atomic Habits", "scenes": []}\n```'
    cleaned = _clean_json_output(raw_markdown)
    assert cleaned == '{"title": "Atomic Habits", "scenes": []}'

    plain = '{"key": "value"}'
    assert _clean_json_output(plain) == '{"key": "value"}'


def test_llm_service_openrouter_missing_key():
    with patch("app.services.llm.get_settings") as mock_settings, \
         patch.dict("os.environ", {}, clear=True):
        mock_settings.return_value = MagicMock(
            llm_provider="openrouter",
            llm_model="meta-llama/llama-3.3-70b-instruct",
            openrouter_api_key="",
            openrouter_base_url="https://openrouter.ai/api/v1",
            llm_temperature=0.7,
        )
        service = LLMService()
        with pytest.raises(ValueError, match="OPENROUTER_API_KEY is not set"):
            service.generate("Hello")


def test_llm_service_openrouter_successful_call():
    with patch("app.services.llm.get_settings") as mock_settings, \
         patch("requests.post") as mock_post:
        mock_settings.return_value = MagicMock(
            llm_provider="openrouter",
            llm_model="meta-llama/llama-3.3-70b-instruct",
            openrouter_api_key="sk-or-test-key",
            openrouter_base_url="https://openrouter.ai/api/v1",
            llm_temperature=0.7,
        )
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "Sample summary response"}}]
        }
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        service = LLMService()
        result = service.generate("Summarize book")
        assert result == "Sample summary response"
