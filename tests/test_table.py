import os
import tempfile

import md_kx
from md_kx._cli import run

TABLE_MD = "| a | b |\n| --- | --- |\n| 1 | 2 |\n"


def test_table_none_untouched():
    """AC-001：table_mode=none（默认）表格原样输出。"""
    assert md_kx.text(TABLE_MD) == TABLE_MD


def test_table_none_untouched_explicit():
    """AC-001：显式 table_mode=none 表格原样输出。"""
    assert md_kx.text(TABLE_MD, options={"table_mode": "none"}) == TABLE_MD


def test_table_pad_aligned():
    """AC-002：table_mode=pad 表格单元格补空格对齐。"""
    md = "| aaa | b |\n| --- | --- |\n| 1 | 2 |\n"
    output = md_kx.text(md, options={"table_mode": "pad"})
    # 第 1 列宽 3（aaa），短单元格补空格对齐；分隔行用 --- 对齐
    assert "| aaa | b |" in output
    assert "| 1   | 2 |" in output


def test_table_compact():
    """AC-003：table_mode=compact 表格保持紧凑不 pad。"""
    output = md_kx.text(
        "| a | b |\n| --- | --- |\n| 1 | 2 |\n", options={"table_mode": "compact"}
    )
    assert "| a | b |" in output
    assert "| 1 | 2 |" in output


def test_table_syntax_valid():
    """AC-004：三态下表格语法正确、二次解析仍为合法表格。"""
    for mode in ("none", "pad", "compact"):
        out = md_kx.text(TABLE_MD, options={"table_mode": mode})
        # 二次格式化幂等，表格结构保持
        out2 = md_kx.text(out, options={"table_mode": mode})
        assert out == out2
        assert "| --- |" in out


def test_no_table_no_regression():
    """AC-005：不含表格文档任意开关下输出一致。"""
    md = "# Title\n\nSome **text**.\n"
    baseline = md_kx.text(md)
    for mode in ("none", "pad", "compact"):
        assert md_kx.text(md, options={"table_mode": mode}) == baseline


def test_table_mode_cli():
    """table_mode 可通过 CLI 指定。"""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write("| a | b |\n| --- | --- |\n| 1 | 2 |\n")
        path = f.name
    try:
        assert run((path, "--table-mode=compact")) == 0
        with open(path) as fh:
            content = fh.read()
        assert "| a | b |" in content
    finally:
        os.unlink(path)


def test_escaped_pipe_preserved():
    """单元格内转义管道在各态下保留，二次格式化幂等。"""
    md = "| a | b |\n| --- | --- |\n| x\\|y | z |\n"
    for mode in ("none", "pad", "compact"):
        out = md_kx.text(md, options={"table_mode": mode})
        assert "x\\|y" in out, f"mode={mode} 转义管道丢失: {out!r}"
        out2 = md_kx.text(out, options={"table_mode": mode})
        assert out == out2, f"mode={mode} 非幂等"


def test_alignment_colons_preserved():
    """对齐冒号在各态下保留（:--- / :---: / ---:）。"""
    md = "| a | b | c |\n| :--- | :---: | ---: |\n| 1 | 2 | 3 |\n"
    for mode in ("none", "pad", "compact"):
        out = md_kx.text(md, options={"table_mode": mode})
        # 完整分隔行匹配，独立验证左/中/右对齐
        assert "| :--- | :---: | ---: |" in out, f"mode={mode} 对齐冒号丢失: {out!r}"
