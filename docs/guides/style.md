# Formatting style

This document describes, demonstrates, and rationalizes the formatting style that md_kx follows.

Md_kx's formatting style is crafted so that writing, editing and collaborating on Markdown documents is as smooth as possible.
The style is consistent, and minimizes diffs (for ease of reviewing changes),
sometimes at the cost of some readability.

Md_kx makes sure to only change style, not content.
Once converted to HTML and rendered on screen,
formatted Markdown should yield a result that is visually identical to the unformatted document.
Md_kx CLI includes a safety check that will error and refuse to apply changes to a file
if Markdown AST is not equal before and after formatting.

## Headings

For consistency, only ATX headings are used.
Setext headings are reformatted using the ATX style.
ATX headings are used because they can be consistently used for any heading level,
whereas setext headings only allow level 1 and 2 headings.

Input:

```markdown
First level heading
===

Second level heading
---
```

Output:

```markdown
# First level heading

## Second level heading
```

## Bullet lists

Md_kx uses `-` as the bullet list marker.
In the case of consecutive bullet lists,
md_kx alternates between `-` and `*` markers.

## Ordered lists

Md_kx uses `.` as ordered list marker type.
In the case of consecutive ordered lists,
md_kx alternates between `.` and `)` types.

Md_kx uses `1.` or `1)` as the ordered list marker, also for noninital list items.

Input:

```markdown
1. Item A
2. Item B
3. Item C
```

Output:

```markdown
1. Item A
1. Item B
1. Item C
```

This "non-numbering" style was chosen to minimize diffs. But how exactly? Lets imagine we are listing the alphabets, using a proper consecutive numbering style:

```markdown
1. b
2. c
3. d
```

Now we notice an error was made, and that the first character "a" is missing.
We add it as the first item in the list.
As a result, the numbering of every subsequent item in the list will increase by one,
meaning that the diff will touch every line in the list.
The non-numbering style solves this issue: only the added line will show up in the diff.

Md_kx allows consecutive numbering via configuration.

## Code blocks

Only fenced code blocks are allowed.
Indented code blocks are reformatted as fenced code blocks.

Fenced code blocks are preferred because they allow setting an info string,
which indented code blocks do not support.

## Code spans

Length of a code span starting/ending backtick string is reduced to minimum.
Needless space characters are stripped from the front and back,
unless the content contains backticks.

Input:

`````markdown
````Backtick string is reduced.````

` Space is stripped from the front and back... `

```` ...unless a "`" character is present. ````
`````

Output:

```markdown
`Backtick string is reduced.`

`Space is stripped from the front and back...`

`` ...unless a "`" character is present. ``
```

## Inline links

Redundant angle brackets surrounding a link destination will be removed.

Input:

```markdown
[Python](<https://python.org>)
```

Output:

```markdown
[Python](https://python.org)
```

## Reference links

All link reference definitions are moved to the bottom of the document,
sorted by label. Unused and duplicate references are removed.

Input:

```markdown
[dupe ref]: https://gitlab.com
[dupe ref]: link1
[unused ref]: link2

Here's a link to [GitLab][dupe ref]
```

Output:

```markdown
Here's a link to [GitLab][dupe ref]

[dupe ref]: https://gitlab.com
```

## Paragraph word wrapping

Md_kx by default will not change word wrapping.
The rationale for this is to encourage and support [Semantic Line Breaks](https://sembr.org/),
a technique described by Brian Kernighan in the early 1970s,
yet still as relevant as ever today:

> **Hints for Preparing Documents**
>
> Most documents go through several versions (always more than you
> expected) before they are finally finished. Accordingly, you should
> do whatever possible to make the job of changing them easy.
>
> First, when you do the purely mechanical operations of typing, type
> so subsequent editing will be easy. Start each sentence on a new line.
> Make lines short, and break lines at natural places, such as after
> commas and semicolons, rather than
> randomly. Since
> most people change documents by rewriting phrases and adding, deleting
> and rearranging sentences, these precautions simplify any editing you
> have to do later.
>
> _— Brian W. Kernighan. "UNIX for Beginners". 1974_

Md_kx allows removing word wrap or setting a target wrap width via configuration.

## Thematic breaks

Thematic breaks are formatted as a 70 character wide string of underscores.
A wide thematic break is distinguishable,
and visually resembles how a corresponding HTML `<hr>` tag is typically rendered.

## Whitespace

Md_kx applies consistent whitespace across the board:

- Convert line endings to a single newline character
- Strip paragraph trailing and leading whitespace
- Indent contents of block quotes and list items consistently
- Always separate blocks with a single empty line
  (an exception being tight lists where the separator is a single newline character)
- Always end the document in a single newline character
  (an exception being an empty document)

## Hard line breaks

Hard line breaks are always a backslash preceding a line ending.
The alternative syntax,
two or more spaces before a line ending,
is not used because it is not visible.

Input:

```markdown
Hard line break is here:   
Can you see it?
```

Output:

```markdown
Hard line break is here:\
Can you see it?
```

## Fork 扩展风格

以下为本 fork（md_kx）在官方 mdformat 基础上新增的格式化行为。

### YAML front matter

文档开头的 YAML front matter（`---` 包裹，含 `key: value` 行）原样保留，不进入格式化管线。front matter 与正文的间隔空行保留。

### 嵌套列表缩进

默认 marker 对齐（`-` 项 2 空格/层、`1.` 项 3 空格/层）。设置 `indent_width` 后统一为指定宽度：

```markdown
# 默认：marker 对齐
- a
  - b

# indent_width = 4
- a
    - b
```

### 表格

默认 `table_mode = spaced`，单元格两侧各一个空格、不按列对齐。`compact` 单元格两侧零空格；`pad` 按列补齐、外层竖线对齐（含分隔行）。对齐冒号（`:---` / `:---:` / `---:`）在三种风格下均保留。

```markdown
# compact
|name|value|
|---|---|
|a|1|

# spaced（默认）
| name | value |
| --- | --- |
| a | 1 |

# pad
| name   | value |
| ------ | ----- |
| a      | 1     |
```
