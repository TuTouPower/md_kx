import os
import tempfile

import md_kx
from md_kx._cli import run
from md_kx._util import is_md_equal

LIST_TABLE_MD = (
    "2. `review_level` 按风险判：\n|level|适用|\n|------|------|\n|`full`|安全|\n"
)


def test_list_table_validate_passes():
    """AC-001/002：列表项后 0 缩进表格行格式化后 validate 通过，HTML 不变。"""
    formatted = md_kx.text(
        LIST_TABLE_MD, options={"table_mode": "compact", "number": True}
    )
    assert is_md_equal(
        LIST_TABLE_MD, formatted, options={"table_mode": "compact", "number": True}
    )
    # 表格行不被拉进列表内部缩进
    lines = formatted.split("\n")
    assert lines[1].lstrip() == lines[1]  # |level| 行 0 缩进


def test_list_table_cli_exit_zero():
    """AC-001 CLI：格式化含该写法的文件退出码 0。"""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(LIST_TABLE_MD)
        path = f.name
    try:
        assert run((path, "--table-mode=compact", "--number")) == 0
    finally:
        os.unlink(path)


def test_none_mode_escape_preserved():
    """AC-003：none 模式转义保留不回退。"""
    md = "| a | b |\n| --- | --- |\n| x\\|y | z |\n"
    out = md_kx.text(md)
    assert "x\\|y" in out
    assert md_kx.text(out) == out


def test_table_modes_unchanged():
    """AC-004：独立表格三态行为不变。"""
    md = "| a | b |\n| --- | --- |\n| 1 | 2 |\n"
    for mode in ("none", "pad", "compact"):
        out = md_kx.text(md, options={"table_mode": mode})
        assert "|" in out
        assert md_kx.text(out, options={"table_mode": mode}) == out


def test_multiline_list_item_unchanged():
    """AC-005：正常多行段落列表项缩进行为不变。"""
    md = "1. 第一行\n   第二行内容延续\n2. 另一项\n"
    out = md_kx.text(md, options={"number": True})
    assert "   第二行内容延续" in out
    assert is_md_equal(md, out, options={"number": True})


def test_nested_table_in_list_kept():
    """列表内缩进嵌套表格保持列表内（守卫不误伤独立 table 子块）。"""
    md = "1. foo\n\n    | a | b |\n    | --- | --- |\n    | 1 | 2 |\n"
    out = md_kx.text(md, options={"table_mode": "compact"})
    assert is_md_equal(md, out, options={"table_mode": "compact"})
    # 表格行保持列表内缩进（非 0 缩进）
    assert out.split("\n")[2].startswith("   |")


def test_pipe_line_in_list_code_block_kept():
    """列表内代码块中 `|` 开头行保持缩进（守卫不误伤 fence 子块）。"""
    md = "1. example\n\n    ```\n    |code line|\n    ```\n"
    out = md_kx.text(md)
    assert is_md_equal(md, out)
    assert "   |code line|" in out


def test_list_item_first_line_pipe_no_crash():
    """列表项首行以 | 开头（非合法表格）不崩溃、格式化正常。"""
    md = "1. outer\n2. |x|y|\n"
    out = md_kx.text(md, options={"number": True})
    assert "2. |x|y|" in out


def test_indented_paragraph_pipe_kept():
    """列表内空行分隔的独立缩进段落（首字符 |）保持缩进，不被守卫降 0。"""
    md = "- foo\n\n  |bar\n"
    out = md_kx.text(md)
    assert is_md_equal(md, out)
    assert "  |bar" in out


def test_pipe_line_outside_list_no_crash():
    """非列表上下文（独立段落/引用块）`|` 续行不崩溃、正常格式化。"""
    for md in ("foo\n|bar\n", "> foo\n> |bar\n"):
        out = md_kx.text(md)
        assert "|bar" in out


def test_pipe_in_list_blockquote_no_crash():
    """列表内块引用中 `|` 行不崩溃（blockquote 子块不打 lazy 标记）。"""
    md = "- foo\n  > bar\n  > |baz\n"
    out = md_kx.text(md)
    assert "> |baz" in out


def test_multiline_paragraph_lazy_table_no_crash():
    """多行列表项段落 + 紧接 0 缩进表格不崩溃、validate 通过。"""
    md = "2. `review_level`\n按风险判：\n|level|适用|\n|------|------|\n|`full`|安全|\n"
    out = md_kx.text(md, options={"number": True})
    assert is_md_equal(md, out, options={"number": True})
    # 段落续行正常缩进，表格行保持 0 缩进
    lines = out.split("\n")
    assert lines[1].startswith("   按风险判：")
    assert lines[2].lstrip() == lines[2]
