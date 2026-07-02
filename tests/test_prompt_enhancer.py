from app.domain.models.video_blueprint import Scene
from app.services.prompt_enhancer import PromptEnhancer


def test_prompt_contains_scene_information():

    scene = Scene(
        id=1,
        title="Seed",
        narration="Every habit starts small.",
        visual_prompt="Tiny seed growing into a tree.",
        duration=0,
        camera="slow_zoom",
        transition="fade",
        subtitle_style="word_by_word",
        emotion="hope",
        music_mood="calm",
        sound_effects=[],
    )

    prompt = PromptEnhancer.enhance(scene)

    assert "Tiny seed growing into a tree." in prompt
    assert "hope" in prompt
    assert "slow_zoom" in prompt