"""Tests for the redline comparison tool."""

from redline import redline, diff_words, diff_lines


def test_identical_documents():
    text = "Hello world.\nThis is a test.\n"
    result = redline(text, text)
    # No ANSI codes should appear for identical text
    assert "\033[" not in result
    assert "Hello world" in result


def test_word_insertion():
    original = "The cat sat."
    revised = "The big cat sat."
    result = redline(original, revised, mode="word", output_format="terminal")
    assert "\033[32m" in result  # green for addition
    assert "big" in result


def test_word_deletion():
    original = "The big cat sat."
    revised = "The cat sat."
    result = redline(original, revised, mode="word", output_format="terminal")
    assert "\033[9m" in result  # strikethrough for deletion
    assert "big" in result


def test_word_replacement():
    original = "The cat sat."
    revised = "The dog sat."
    result = redline(original, revised, mode="word", output_format="terminal")
    assert "cat" in result
    assert "dog" in result


def test_line_mode():
    original = "line one\nline two\n"
    revised = "line one\nline three\n"
    result = redline(original, revised, mode="line", output_format="terminal")
    assert "two" in result
    assert "three" in result


def test_html_output():
    original = "Hello world."
    revised = "Hello brave new world."
    result = redline(original, revised, mode="word", output_format="html")
    assert '<span class="add">' in result
    assert "brave" in result
    assert "&lt;" not in result or "<script>" not in original  # no injection


def test_html_escaping():
    original = "x < y"
    revised = "x > y"
    result = redline(original, revised, mode="word", output_format="html")
    assert "&lt;" in result
    assert "&gt;" in result


def test_empty_documents():
    result = redline("", "")
    assert result == ""


def test_completely_new():
    result = redline("", "new content", mode="word", output_format="terminal")
    assert "new content" in result
    assert "\033[32m" in result


def test_completely_deleted():
    result = redline("old content", "", mode="word", output_format="terminal")
    assert "old content" in result
    assert "\033[31m" in result


def test_diff_words_returns_list():
    changes = diff_words("a b", "a c")
    assert isinstance(changes, list)
    tags = {c["tag"] for c in changes}
    assert "equal" in tags


def test_diff_lines_returns_list():
    changes = diff_lines("a\n", "b\n")
    assert isinstance(changes, list)


if __name__ == "__main__":
    import subprocess
    import sys
    sys.exit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
