import pytest

from src.toxicity.preprocessing import clean_text


LABELS = [
    "toxic",
    "severe_toxic",
    "obscene",
    "threat",
    "insult",
    "identity_hate",
]


def test_clean_text():

    text = """
    You are an idiot!!!
    Visit https://example.com
    """

    result = clean_text(text)

    assert result == (
        "you are an idiot visit"
    )


def test_clean_text_removes_html():

    text = "<p>You are stupid!</p>"

    result = clean_text(text)

    assert "<p>" not in result
    assert "</p>" not in result


def test_clean_text_removes_url():

    text = "Visit https://example.com now"

    result = clean_text(text)

    assert "https://example.com" not in result


def test_clean_text_handles_empty_string():

    result = clean_text("")

    assert result == ""


def test_clean_text_handles_none():

    result = clean_text(None)

    assert result == ""


def test_labels():

    assert len(LABELS) == 6

    assert LABELS == [
        "toxic",
        "severe_toxic",
        "obscene",
        "threat",
        "insult",
        "identity_hate",
    ]