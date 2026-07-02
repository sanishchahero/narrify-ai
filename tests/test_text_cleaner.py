from app.services.text_cleaner import TextCleaner


def test_clean():

    text = "Hello\n\n\nWorld"

    assert TextCleaner.clean(text) == "Hello World"