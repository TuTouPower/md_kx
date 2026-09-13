# test_table.py 按 t008 三风格语义整体重写：
# - 原 AC-001/002（table_mode=none 原样输出）随 none 风格删除而移除
# - 原 AC-003（compact 输出 `| a | b |`）语义重定义为零空格，断言全部更新
# - 旧断言与新语义矛盾，整体删除重写而非就地改预期（项目 TDD 规则）

import pytest

import md_kx
from md_kx._cli import run

TABLE_MD = "| a | b |\n| --- | --- |\n| 1 | 2 |\n"
MODES = ("compact", "spaced", "pad")


def test_default_mode_is_spaced():
    """AC-010：未指定风格时默认 spaced。"""
    assert md_kx.text(TABLE_MD) == md_kx.text(
        TABLE_MD, options={"table_mode": "spaced"}
    )


def test_compact_zero_padding():
    """AC-001/002：compact 单元格与分隔行两侧零空格。"""
    out = md_kx.text(TABLE_MD, options={"table_mode": "compact"})
    assert out == "|a|b|\n|---|---|\n|1|2|\n"


def test_spaced_one_padding():
    """AC-001/003：spaced 两侧各一空格，同列宽度可不一致。"""
    assert md_kx.text(TABLE_MD, options={"table_mode": "spaced"}) == TABLE_MD
    md = "| a | bb |\n| --- | --- |\n| ccc | d |\n"
    out = md_kx.text(md, options={"table_mode": "spaced"})
    assert out == md


def test_pad_aligned():
    """AC-001/004：pad 按列补齐，外层竖线对齐（含分隔行）。"""
    md = "| aaa | b |\n| --- | --- |\n| 1 | 2 |\n"
    out = md_kx.text(md, options={"table_mode": "pad"})
    assert out == "| aaa | b   |\n| --- | --- |\n| 1   | 2   |\n"


def test_pad_separator_tracks_column_width():
    """AC-004：分隔行长度随列宽走（分隔段参与列宽计算）。"""
    out = md_kx.text(TABLE_MD, options={"table_mode": "pad"})
    lines = out.split("\n")
    assert lines[0] == "| a   | b   |"
    assert lines[1] == "| --- | --- |"


def test_pad_wide_column_separator_stretches():
    """AC-004/005：列宽超过固定 marker 宽度时分隔段按列宽拉长、冒号贴边。"""
    md = "| abcdef | g | h |\n| :--- | :---: | ---: |\n| 1 | 2 | 3 |\n"
    out = md_kx.text(md, options={"table_mode": "pad"})
    lines = out.split("\n")
    # 列宽：列1 = max(4, 6)=6；列2 = max(5, 1)=5；列3 = max(4, 1)=4
    assert lines[0] == "| abcdef | g     | h    |"
    assert lines[1] == "| :----- | :---: | ---: |"
    assert lines[2] == "| 1      | 2     | 3    |"


def test_pad_center_marker_stretches():
    """AC-005：pad 居中标记宽度超 5 时横线拉长、冒号保留在两侧。"""
    md = "| a | b | c |\n| :--- | :---: | ---: |\n| 1 | longcell | 3 |\n"
    out = md_kx.text(md, options={"table_mode": "pad"})
    lines = out.split("\n")
    # 列 2 宽 8（longcell），居中标记 = ':' + 6 dash + ':'
    assert lines[1] == "| :--- | :------: | ---: |"


def test_pad_right_marker_stretches():
    """AC-005：pad 右对齐标记宽度超 4 时横线拉长、冒号贴右边界。"""
    md = "| a | b |\n| :--- | ---: |\n| 1 | longcell |\n"
    out = md_kx.text(md, options={"table_mode": "pad"})
    lines = out.split("\n")
    # 列 2 宽 8（longcell），右对齐标记 = 7 dash + ':'
    assert lines[1] == "| :--- | -------: |"


def test_pad_plain_wide_column():
    """AC-004：无对齐宽列纯文本分隔段按列宽拉长。"""
    md = "| abcdef | g |\n| --- | --- |\n| 1 | 2 |\n"
    out = md_kx.text(md, options={"table_mode": "pad"})
    lines = out.split("\n")
    # 列 1 宽 6（abcdef），无对齐标记 = 6 dash
    assert lines[1] == "| ------ | --- |"


def test_pad_wide_column_idempotent():
    """AC-008：宽列 pad 输出二次格式化无 diff。"""
    md = "| abcdef | g |\n| :--- | ---: |\n| 1 | 2 |\n"
    out = md_kx.text(md, options={"table_mode": "pad"})
    assert md_kx.text(out, options={"table_mode": "pad"}) == out


def test_alignment_colons_compact():
    """AC-005：compact 对齐冒号贴竖线内侧不加空格。"""
    md = "| a | b | c |\n| :--- | :---: | ---: |\n| 1 | 2 | 3 |\n"
    out = md_kx.text(md, options={"table_mode": "compact"})
    assert out == "|a|b|c|\n|:---|:---:|---:|\n|1|2|3|\n"


def test_alignment_colons_spaced():
    """AC-005：spaced 对齐冒号外侧各一空格。"""
    md = "| a | b | c |\n| :--- | :---: | ---: |\n| 1 | 2 | 3 |\n"
    out = md_kx.text(md, options={"table_mode": "spaced"})
    assert out == md


def test_alignment_colons_pad():
    """AC-005：pad 保留冒号并按列宽拉长分隔段。"""
    md = "| a | b | c |\n| :--- | :---: | ---: |\n| 1 | 2 | 3 |\n"
    out = md_kx.text(md, options={"table_mode": "pad"})
    lines = out.split("\n")
    assert lines[0] == "| a    | b     | c    |"
    assert lines[1] == "| :--- | :---: | ---: |"


def test_escaped_pipe_preserved():
    """AC-006：转义竖线三种风格下保留、不拆列，且幂等。"""
    md = "| a | b |\n| --- | --- |\n| x\\|y | z |\n"
    expected = {
        "compact": "|a|b|\n|---|---|\n|x\\|y|z|",
        "spaced": "| a | b |\n| --- | --- |\n| x\\|y | z |",
        # pad 列宽：列1 max(3, a=1, x\|y=4)=4；列2 max(3, b=1, z=1)=3
        "pad": "| a    | b   |\n| ---- | --- |\n| x\\|y | z   |",
    }
    for mode in MODES:
        out = md_kx.text(md, options={"table_mode": mode}).rstrip("\n")
        # 整行精确断言：转义保留、不拆列、列结构不变
        assert out == expected[mode], f"mode={mode}: {out!r}"
        assert md_kx.text(out + "\n", options={"table_mode": mode}) == md_kx.text(
            md, options={"table_mode": mode}
        )


def test_empty_cells():
    """AC-007：空单元格 compact 相邻竖线、spaced 两侧各一空格、pad 按列宽补空格。"""
    md = "| a | |\n| --- | --- |\n| 1 | |\n"
    assert (
        md_kx.text(md, options={"table_mode": "compact"}) == "|a||\n|---|---|\n|1||\n"
    )
    assert (
        md_kx.text(md, options={"table_mode": "spaced"})
        == "| a |  |\n| --- | --- |\n| 1 |  |\n"
    )
    pad_out = md_kx.text(md, options={"table_mode": "pad"})
    assert pad_out == "| a   |     |\n| --- | --- |\n| 1   |     |\n"


def test_idempotent():
    """AC-008：三种风格各自二次格式化无 diff。"""
    for mode in MODES:
        out = md_kx.text(TABLE_MD, options={"table_mode": mode})
        out2 = md_kx.text(out, options={"table_mode": mode})
        assert out == out2, f"mode={mode} 非幂等"


def test_no_table_output_identical():
    """AC-009：不含表格文档三种风格输出一致。"""
    md = "# Title\n\nSome **text**.\n"
    outputs = [md_kx.text(md, options={"table_mode": mode}) for mode in MODES]
    assert outputs[0] == outputs[1] == outputs[2]


def test_cli_override_conf(tmp_path):
    """AC-011：命令行优先于仓库配置。"""
    (tmp_path / ".md_kx.toml").write_text("table_mode = 'pad'")
    file_path = tmp_path / "t.md"
    file_path.write_text(TABLE_MD)
    assert run((str(file_path), "--table-mode=compact")) == 0
    assert file_path.read_text() == "|a|b|\n|---|---|\n|1|2|\n"
    # 不带 CLI 参数时配置生效
    assert run((str(file_path),)) == 0
    assert file_path.read_text() == "| a   | b   |\n| --- | --- |\n| 1   | 2   |\n"


def test_invalid_mode_rejected_cli(tmp_path):
    """AC-012：none 及非法风格名 CLI 拒绝，文件不改。"""
    file_path = tmp_path / "t.md"
    file_path.write_text(TABLE_MD)
    for bad in ("none", "wide", " "):
        with pytest.raises(SystemExit):
            run((str(file_path), f"--table-mode={bad}"))
        assert file_path.read_text() == TABLE_MD


def test_invalid_mode_rejected_conf(tmp_path, capsys):
    """AC-012：none 及非法风格名配置拒绝，文件不改。"""
    file_path = tmp_path / "t.md"
    file_path.write_text(TABLE_MD)
    for bad in ("none", "wide"):
        (tmp_path / ".md_kx.toml").write_text(f"table_mode = '{bad}'")
        assert run((str(file_path),)) == 1
        assert "Invalid 'table_mode' value" in capsys.readouterr().err
        assert file_path.read_text() == TABLE_MD
