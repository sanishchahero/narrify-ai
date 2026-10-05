from app.config.image_styles import ImageStyle
from app.domain.models.camera import Camera
from app.domain.models.character import Character
from app.domain.models.environment import Environment
from app.domain.models.frame import Frame
from app.domain.models.scene import Scene as StoryboardScene
from app.domain.models.video_blueprint import Scene as BlueprintScene
from app.domain.models.visual_context import VisualContext
from app.services.prompt_enhancer import PromptEnhancer


def test_prompt_contains_blueprint_scene_information():
    scene = BlueprintScene(
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
    assert "===" not in prompt
    assert "Narration:" not in prompt


def test_prompt_contains_storyboard_scene_and_context():
    frame = Frame(
        primary_subject="Young apprentice",
        primary_action="carving a wooden toy with focused expression",
        subject_description="focused determined face, messy brown hair",
        secondary_subjects=[],
        important_objects=["chisel", "wood shavings", "work desk"],
        foreground=["scattered tools"],
        middle_ground=[],
        background=["warm rustic workshop"],
        visual_metaphor="craftsmanship",
    )
    camera = Camera(
        shot="close-up",
        angle="eye-level",
        lens="50mm",
        focus="subject",
        composition="rule of thirds",
    )
    environment = Environment(
        location="carpentry workshop",
        background="bookshelves and lumber",
        weather="clear",
        season="autumn",
        time_of_day="golden hour",
    )
    char = Character(
        id="c1",
        name="Leo",
        gender="male",
        age="teenager",
        hairstyle="short wavy brown hair",
        face="determined",
        clothing="leather apron over rolled-up linen shirt",
        accessories=["wooden pendant"],
    )
    scene = StoryboardScene(
        id=1,
        title="Apprentice at work",
        narration="Skill is forged through deliberate practice.",
        frame=frame,
        camera=camera,
        environment=environment,
        characters=[char],
        emotion="inspirational",
        music_mood="acoustic",
    )
    context = VisualContext(
        art_style="hand-drawn sketch",
        illustration_style="vintage textbook",
        color_palette="warm sepia and earthy green",
        paper_style="deckled parchment",
        line_style="crosshatched ink",
        lighting_style="warm amber lantern light",
        aspect_ratio="9:16",
    )

    prompt = PromptEnhancer.enhance(
        scene=scene,
        context=context,
        style=ImageStyle.HANDWRITTEN,
    )

    assert "Young apprentice" in prompt
    assert "carving a wooden toy" in prompt
    assert "chisel" in prompt
    assert "close-up shot" in prompt
    assert "hand-drawn sketch" in prompt
    assert "9:16" in prompt
    # Verify no markdown or negative words in positive prompt
    assert "===" not in prompt
    assert "Title:" not in prompt
    assert "Narration:" not in prompt
    assert "No text" not in prompt


def test_prompt_style_switch():
    scene = BlueprintScene(
        id=2,
        title="Modern Office",
        narration="Focus is your greatest asset.",
        subject="Programmer writing code",
        action="typing on keyboard",
        background="minimalist office with neon accents",
    )

    prompt = PromptEnhancer.enhance(scene, style=ImageStyle.CARTOON)

    assert "Programmer writing code" in prompt
    assert "typing on keyboard" in prompt
    assert "clean modern 2d vector cartoon" in prompt