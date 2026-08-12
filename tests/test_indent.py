import os
import tempfile

import md_kx
from md_kx._cli import run

NESTED_MD = "- a\n  - b\n    - c\n  - d\n"


def test_default_no_regression():
    """AC-001：未设置缩进宽度配置时输出与现有行为一致。"""
    assert md_kx.text(NESTED_MD) == NESTED_MD


def test_indent_width_unified():
    """AC-002：设置缩进宽度为 N 后嵌套列表统一为 N 空格。"""
    output = md_kx.text(NESTED_MD, options={"indent_width": 4})
    assert output == "- a\n    - b\n        - c\n    - d\n"


def test_indent_width_ordered_list():
    """AC-002 有序列表：统一缩进同样应用于有序列表。"""
    md = "1. a\n\n   1. b\n\n      1. c\n"
    output = md_kx.text(md, options={"indent_width": 4})
    assert output == "1. a\n\n    1. b\n\n        1. c\n"


def test_code_block_untouched_byte_for_byte():
    """AC-003：设置缩进宽度后代码块内容逐字节不被改动。"""
    md = "# T\n\n```\ncode line\n  indented line\n```\n"
    output = md_kx.text(md, options={"indent_width": 4})
    assert output == "# T\n\n```\ncode line\n  indented line\n```\n"


def test_indent_width_cli():
    """AC-004：CLI 指定缩进宽度。"""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(NESTED_MD)
        path = f.name
    try:
        assert run((path, "--indent-width=4")) == 0
        with open(path) as fh:
            content = fh.read()
        assert content == "- a\n    - b\n        - c\n    - d\n"
    finally:
        os.unlink(path)


def test_indent_width_config_file():
    """AC-004：配置文件指定缩进宽度。"""
    with tempfile.TemporaryDirectory() as d:
        conf = os.path.join(d, ".md_kx.toml")
        with open(conf, "w") as fh:
            fh.write("indent_width = 4\n")
        path = os.path.join(d, "test.md")
        with open(path, "w") as fh:
            fh.write(NESTED_MD)
        assert run((path,)) == 0
        with open(path) as fh:
            content = fh.read()
        assert content == "- a\n    - b\n        - c\n    - d\n"


def test_indent_width_below_marker_falls_back():
    """AC-002 兜底：N 小于 marker 宽度时取 marker 宽度，不破坏嵌套。"""
    # N=1 < marker 宽度 2，兜底为 2 空格，嵌套结构保留
    output = md_kx.text(NESTED_MD, options={"indent_width": 1})
    assert output == NESTED_MD
