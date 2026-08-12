import os

from markdown_it import MarkdownIt
import pytest

import md_kx
from md_kx._util import is_md_equal
from md_kx.renderer import MDRenderer

UNFORMATTED_MARKDOWN = "\n\n# A header\n\n"
FORMATTED_MARKDOWN = "# A header\n"


def test_fmt_file(tmp_path):
    file_path = tmp_path / "test_markdown.md"

    # Use string argument
    file_path.write_text(UNFORMATTED_MARKDOWN)
    md_kx.file(str(file_path))
    assert file_path.read_text() == FORMATTED_MARKDOWN

    # Use pathlib.Path argument
    file_path.write_text(UNFORMATTED_MARKDOWN)
    md_kx.file(file_path)
    assert file_path.read_text() == FORMATTED_MARKDOWN


def test_fmt_file__invalid_filename():
    with pytest.raises(ValueError) as exc_info:
        md_kx.file("this is not a valid filepath?`=|><@{[]\\/,.%¤#'")
    assert "not a file" in str(exc_info.value)


def test_fmt_file__symlink(tmp_path):
    file_path = tmp_path / "test_markdown.md"
    file_path.write_text(UNFORMATTED_MARKDOWN)
    symlink_path = tmp_path / "symlink.md"
    symlink_path.symlink_to(file_path)

    with pytest.raises(ValueError) as exc_info:
        md_kx.file(symlink_path)
    assert "It is a symlink" in str(exc_info.value)


def test_fmt_string():
    assert md_kx.text(UNFORMATTED_MARKDOWN) == FORMATTED_MARKDOWN


@pytest.mark.parametrize(
    "input_",
    [
        pytest.param("\x0b"),  # vertical tab only
        pytest.param("\t##"),  # no trailing newline in codeblock
        pytest.param("a\n\n\xa0\n\nb"),  # lone NBSP between two paragraphs
        pytest.param("\xa0\n\n# heading"),  # lone NBSP followed by a heading
        pytest.param(
            "```\na\n```\n\u2003\n# A\n"
        ),  # em space surrounded by code and header
    ],
)
def test_output_is_equal(input_):
    output = md_kx.text(input_)
    assert is_md_equal(input_, output)


@pytest.mark.parametrize(
    "input_",
    [
        pytest.param("\x1c\n\na"),
        pytest.param(">\x0b"),
        pytest.param("<!K"),
    ],
)
def test_cases_found_by_fuzzer(input_):
    output = md_kx.text(input_)
    assert is_md_equal(input_, output)


def test_api_options():
    non_numbered = """\
0. a
0. b
0. c
"""
    numbered = """\
0. a
1. b
2. c
"""
    assert md_kx.text(non_numbered, options={"number": True}) == numbered


def test_eol__lf(tmp_path):
    file_path = tmp_path / "test.md"
    file_path.write_bytes(b"Oi\r\n")
    md_kx.file(str(file_path))
    assert file_path.read_bytes() == b"Oi\n"


def test_eol__crlf(tmp_path):
    file_path = tmp_path / "test.md"
    file_path.write_bytes(b"Oi\n")
    md_kx.file(str(file_path), options={"end_of_line": "crlf"})
    assert file_path.read_bytes() == b"Oi\r\n"


def test_eol__keep_lf(tmp_path):
    file_path = tmp_path / "test.md"
    file_path.write_bytes(b"Oi\n")
    md_kx.file(str(file_path), options={"end_of_line": "keep"})
    assert file_path.read_bytes() == b"Oi\n"


def test_eol__keep_crlf(tmp_path):
    file_path = tmp_path / "test.md"
    file_path.write_bytes(b"Oi\r\n")
    md_kx.file(str(file_path), options={"end_of_line": "keep"})
    assert file_path.read_bytes() == b"Oi\r\n"


def test_no_timestamp_modify(tmp_path):
    file_path = tmp_path / "test.md"

    file_path.write_bytes(b"lol\n")
    initial_access_time = 0
    initial_mod_time = 0
    os.utime(file_path, (initial_access_time, initial_mod_time))

    # Assert that modification time does not change when no changes are applied
    md_kx.file(file_path)
    assert os.path.getmtime(file_path) == initial_mod_time


def test_mdrenderer_no_finalize(tmp_path):
    mdit = MarkdownIt()
    mdit.options["store_labels"] = True
    env: dict = {}
    tokens = mdit.parse(
        "[gl ref]: https://gitlab.com\n\nHere's a link to [GitLab][gl ref]", env
    )
    unfinalized = MDRenderer().render(tokens, {}, env, finalize=False)
    finalized = MDRenderer().render(tokens, {}, env)
    assert finalized == unfinalized + "\n\n[gl ref]: https://gitlab.com\n"


def test_import_typing():
    """Try to import md_kx.renderer.typing.

    The module consists of annotation types only, so md_kx never imports
    it at runtime. This test ensures that it still runs.
    """
    import md_kx.renderer.typing  # noqa: F401
