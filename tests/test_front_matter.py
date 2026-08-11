import mdformat

FRONT_MATTER_MD = """---
name: x
description: y
---
# Title

Some **bold** text.
"""

FRONT_MATTER_BLOCK = "---\nname: x\ndescription: y\n---\n"


def test_front_matter_preserved_byte_for_byte():
    """AC-001：front matter 与输入逐字节一致。"""
    output = mdformat.text(FRONT_MATTER_MD)
    assert output.startswith(FRONT_MATTER_BLOCK)


def test_body_formatted():
    """AC-002：front matter 之后正文照常格式化。"""
    output = mdformat.text(FRONT_MATTER_MD)
    # 正文部分 "# Title\n\nSome **bold** text.\n" 应为格式化后的规范输出
    body = output[len(FRONT_MATTER_BLOCK) :]
    assert body == "# Title\n\nSome **bold** text.\n"


def test_no_front_matter_unchanged():
    """AC-003：无 front matter 文档行为不变。"""
    md = "# A header\n\n---\n\n# B header\n"
    # 普通 --- 分隔线应保持 thematic break 行为（mdformat 渲染成 `___` 或 `---`）
    out = mdformat.text(md)
    assert "## " not in out  # 分隔线不被误解析成标题
    assert out.startswith("# A header\n\n")


def test_front_matter_content_not_formatted():
    """AC-004：front matter 内部内容不被格式化或改写。"""
    md = "---\nfoo: |\n  line1\n  line2\n---\n# Title\n"
    output = mdformat.text(md)
    fm_block = "---\nfoo: |\n  line1\n  line2\n---\n"
    assert output.startswith(fm_block)


def test_front_matter_trailing_blank_line_preserved():
    """front matter 后空行（连带剥离）在重组时保留。"""
    md = "---\nname: x\n---\n\n# Title\n"
    output = mdformat.text(md)
    assert output == "---\nname: x\n---\n\n# Title\n"


def test_front_matter_crlf_preserved():
    """AC-001 CRLF 变体：CRLF 行尾的 front matter 保留（LF 归一）。"""
    md = "---\r\nname: x\r\ndescription: y\r\n---\r\n# Title\r\n\r\nSome text.\r\n"
    output = mdformat.text(md)
    # text() 输出 front matter 归 LF（符合 text() LF 输出契约）
    fm_block = "---\nname: x\ndescription: y\n---\n"
    assert output.startswith(fm_block)
    # 正文仍正常格式化
    assert "# Title\n\nSome text.\n" in output


def test_blank_separator_not_front_matter():
    """AC-003：正文开头 `---`（非 front matter）不被误吞。"""
    md = "---\n\n# A header\n\n---\n\n# B header\n"
    output = mdformat.text(md)
    # 不剥离：分隔线被渲染成 thematic break（`_` 下划线串），标题正常格式化
    assert output.startswith("_")
    assert "# A header\n\n" in output and "# B header\n" in output
    assert "## " not in output


def test_file_crlf_end_of_line_keep():
    """AC-001 file() 路径：end_of_line=keep 时 CRLF front matter 写回不损坏。"""
    import os
    import tempfile

    md = "---\r\nname: x\r\n---\r\n# Title\r\n\r\nSome text.\r\n"
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(md)
        path = f.name
    try:
        mdformat.file(path, options={"end_of_line": "keep"})
        content = open(path, "rb").read().decode()
        # front matter 保持 CRLF，无 \r\r\n 加倍
        assert content.startswith("---\r\nname: x\r\n---\r\n")
        assert "\r\r\n" not in content
    finally:
        os.unlink(path)
