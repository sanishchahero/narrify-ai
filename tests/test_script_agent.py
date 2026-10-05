import json
import pytest
from unittest.mock import MagicMock, patch

from app.agents.script_agent import ScriptAgent
from app.domain.models.script_response import ScriptResponse, SceneResponse


def test_script_response_validation():
    valid_payload = {
        "title": "Atomic Habits",
        "hook": "Why you fail at goals",
        "summary": "Focus on systems, not goals.",
        "scenes": [
            {"id": 1, "duration": 6, "narration": "Hook line", "visual_goal": "A runner at dawn", "emotion": "curious"},
            {"id": 2, "duration": 6, "narration": "Trap line", "visual_goal": "A person stuck in maze", "emotion": "frustrated"},
            {"id": 3, "duration": 7, "narration": "Breakthrough", "visual_goal": "Exponential curve", "emotion": "enlightened"},
            {"id": 4, "duration": 7, "narration": "Protocol", "visual_goal": "Writing in notebook", "emotion": "focused"},
            {"id": 5, "duration": 6, "narration": "Climax", "visual_goal": "Sunrise over mountains", "emotion": "triumphant"},
        ],
    }

    res = ScriptResponse.model_validate(valid_payload)
    assert len(res.scenes) == 5
    assert res.scenes[0].id == 1


def test_script_response_too_few_scenes():
    invalid_payload = {
        "title": "Short",
        "hook": "Too short",
        "summary": "Too few scenes",
        "scenes": [
            {"id": 1, "duration": 6, "narration": "One", "visual_goal": "Image 1", "emotion": "neutral"},
        ],
    }
    with pytest.raises(Exception):
        ScriptResponse.model_validate(invalid_payload)


def test_script_agent_generate():
    with patch("app.agents.script_agent.LLMService") as mock_llm_cls:
        mock_llm = MagicMock()
        mock_llm.load_prompt.return_value = "System prompt template"
        mock_llm.generate.return_value = json.dumps({
            "title": "Atomic Mastery",
            "hook": "What if 1% was enough?",
            "summary": "Small habits compound over time.",
            "scenes": [
                {"id": i, "duration": 6, "narration": f"Narration {i}", "visual_goal": f"Visual {i}", "emotion": "focused"}
                for i in range(1, 6)
            ],
        })
        mock_llm_cls.return_value = mock_llm

        agent = ScriptAgent()
        script = agent.generate("Book summary text", target_scenes=5)

        assert script.title == "Atomic Mastery"
        assert len(script.scenes) == 5
        assert script.scenes[0].id == 1
        assert script.scenes[4].id == 5
