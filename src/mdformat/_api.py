from __future__ import annotations

from collections.abc import Iterable, Mapping
from contextlib import AbstractContextManager
from os import PathLike
from pathlib import Path
from typing import Any

from mdformat._conf import DEFAULT_OPTS
from mdformat._util import EMPTY_MAP, NULL_CTX, build_mdit, detect_newline_type


def _strip_front_matter(md: str) -> tuple[str, str | None]:
    """Strip a leading YAML front matter block, returning (body, front_matter).

    Only a `---`-wrapped block at the very start of the document is treated
    as front matter; otherwise the input is returned unchanged. Both LF and
    CRLF line endings are recognized for the delimiters. The block is only
    considered front matter when it contains at least one `key: value`-style
    line (a shallow YAML check that avoids swallowing e.g. a blank line then
    `---` as a thematic break). The returned front_matter is normalized to LF
    line endings (matching text()'s normal LF output contract; file()
    converts to the target newline afterwards). Any blank lines directly
    after the closing delimiter are included in front_matter so the
    separation from the body survives rendering.
    """
    lines = md.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return md, None
    for i in range(1, len(lines)):
        if lines[i].rstrip("\r\n") == "---":
            # 浅 YAML 判定：块内须含至少一行 `key: value` 形式
            body_lines = lines[1:i]
            if not any(
                line.rstrip("\r\n").strip() and ":" in line.rstrip("\r\n")
                for line in body_lines
            ):
                return md, None
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            front_matter = "".join(lines[:j]).replace("\r\n", "\n")
            return "".join(lines[j:]), front_matter
    return md, None


def text(
    md: str,
    *,
    options: Mapping[str, Any] = EMPTY_MAP,
    extensions: Iterable[str] = (),
    codeformatters: Iterable[str] = (),
    _first_pass_contextmanager: AbstractContextManager = NULL_CTX,
    _filename: str = "",
) -> str:
    """Format a Markdown string."""
    # Lazy import to improve module import time
    from mdformat.renderer import MDRenderer

    body, front_matter = _strip_front_matter(md)

    with _first_pass_contextmanager:
        mdit = build_mdit(
            MDRenderer,
            mdformat_opts={**options, **{"filename": _filename}},
            extensions=extensions,
            codeformatters=codeformatters,
        )
        rendering = mdit.render(body)

    # If word wrap is changed, add a second pass of rendering.
    # Some escapes will be different depending on word wrap, so
    # rendering after 1st and 2nd pass will be different. Rendering
    # twice seems like the easiest way to achieve stable formatting.
    if options.get("wrap", DEFAULT_OPTS["wrap"]) != "keep":
        rendering = mdit.render(rendering)

    if front_matter is not None:
        rendering = front_matter + rendering

    return rendering


def file(
    f: str | PathLike[str],
    *,
    options: Mapping[str, Any] = EMPTY_MAP,
    extensions: Iterable[str] = (),
    codeformatters: Iterable[str] = (),
) -> None:
    """Format a Markdown file in place."""
    f = Path(f)
    try:
        is_file = f.is_file()
    except OSError:  # Catch "OSError: [WinError 123]" on Windows  # pragma: no cover
        is_file = False
    if not is_file:
        raise ValueError(f'Cannot format "{f}". It is not a file.')
    if f.is_symlink():
        raise ValueError(f'Cannot format "{f}". It is a symlink.')

    original_md = f.read_bytes().decode()
    formatted_md = text(
        original_md,
        options=options,
        extensions=extensions,
        codeformatters=codeformatters,
        _filename=str(f),
    )
    newline = detect_newline_type(
        original_md, options.get("end_of_line", DEFAULT_OPTS["end_of_line"])
    )
    formatted_md = formatted_md.replace("\n", newline)
    if formatted_md != original_md:
        f.write_bytes(formatted_md.encode())
