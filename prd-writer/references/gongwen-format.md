# 公文版式规范（gongwen-format）

> **何时读取**：阶段 6 交付、把 Markdown 转成 Word 之前必读；任何需要调整 Word 字体、字号、页边距、行距、页码时读取。
>
> **依据**：GB/T 9704-2012《党政机关公文格式》规定的**字体族与版面**；但 **PRD 不是正式公文，字号不套用公文标准**（公文标题二号 22pt、正文三号 16pt 对 PRD 过大，已由用户确认改用阅读字号）。本文给出两套字号：公文原件字号仅作依据说明，**PRD 默认执行“PRD 阅读字号”**。
>
> 参考：[GB/T 9704-2012 条文摘录（保山学院）](http://jjsc.bsnc.cn/info/1010/1596.htm)、[党政机关公文格式（常州工学院）](https://dzbgs.ccit.edu.cn/info/1006/1861.htm)、[公文排版开源实现](https://github.com/pamelaaaaa1218/gongwen-format-skill)。

## 1. 用纸、版心与页面

| 项目 | 规范 |
|---|---|
| 用纸 | A4（210 mm × 297 mm） |
| 版心 | 156 mm × 225 mm |
| 页边距 | 上 3.7 cm、下 3.5 cm、左 2.8 cm、右 2.6 cm |
| 页脚 | 距页面下边缘 2.8 cm |
| 装订线 | 0 cm |
| 行距（PRD 默认） | 正文固定值 **22 磅**（12 pt 字号，约每面 28~30 行） |
| 文字颜色 | 黑色（技能规定的【待确认】红色标注除外） |

## 2. 字体与字号

### 2.1 字体族（沿用公文规范）

| 位置 | 中文字体 |
|---|---|
| 文档标题 / 附件标题 | 方正小标宋简体 |
| 正文、三级/四级标题、附件说明 | 仿宋_GB2312 |
| 一级标题（一、） | 黑体 |
| 二级标题（（一） / 1、） | 楷体_GB2312 |
| 页码 | 宋体 |
| 数字与英文 | Times New Roman（中文仍用上表字体） |

### 2.2 字号（PRD 默认执行，区别于公文原件字号）

> 用户已确认：PRD 字体仿照公文，但**字号不用公文标准**（太大），按下列 PRD 阅读字号执行。

| 位置 | PRD 阅读字号 | 对应字号名 | 其它要求 |
|---|---|---|---|
| 文档标题 | 18 pt | 小二 | 居中，行距固定值 30 磅，段后 12 磅 |
| 一级标题「一、」 | 15 pt | 小三 | 黑体，不加粗；段前 8 磅、段后 0 |
| 二级标题「1、」 | 14 pt | 四号 | 楷体_GB2312，不加粗；段前 6 磅、段后 0 |
| 三级标题「迭代N」 | 12 pt | 小四 | 仿宋_GB2312，**加粗**；段前 4 磅、段后 0 |
| 四级标题「N、」/「附件」 | 12 pt | 小四 | 仿宋_GB2312，不加粗；段前 2 磅、段后 0 |
| 正文 | 12 pt | 小四 | 仿宋_GB2312；首行缩进 2 字（24 pt）；固定行距 22 磅；段前段后 0；两端对齐 |
| 引用/说明（> 块） | 9 pt | 小五 | 仿宋_GB2312，灰色可选 |
| 表格（一般） | 10.5 pt | 五号 | 表头黑体、内容仿宋_GB2312；表内单倍行距 |
| 表格（功能详述等密集表） | 9 pt | 小五 | 同上 |
| 附件标题 | 16 pt | 三号 | 方正小标宋简体，居中 |
| 「附件N」标记 | 12 pt | 小四 | 黑体，版心左上角顶格 |
| 页码 | 10.5 pt | 五号 | 宋体半角阿拉伯数字，`— 1 —`，奇数页右空一字、偶数页左空一字 |
| 附件预览对象 | 15 cm 宽 | — | 居中，保持原图宽高比 |

> 参考：公文原件字号为标题二号、正文三号、页码四号——**不用于 PRD**。
>
> 字体缺失时按回退链替换并记录：方正小标宋简体 → 华文中宋 → 宋体加粗；仿宋_GB2312 → 仿宋（FangSong）；楷体_GB2312 → 楷体（KaiTi）；黑体 → SimHei。

## 3. PRD 层级映射

| PRD Markdown | Word 层级 | 字体 / 字号（PRD） |
|---|---|---|
| `# 《产品名》产品需求文档` | 文档标题 | 方正小标宋简体 18 pt，居中 |
| `## 一、…` | 一级标题 | 黑体 15 pt |
| `### 1、…` | 二级标题 | 楷体_GB2312 14 pt |
| `#### 迭代N功能描述` | 三级标题 | 仿宋_GB2312 12 pt 加粗 |
| `##### N、大功能点`、`##### 附件：…` | 四级标题 | 仿宋_GB2312 12 pt |
| 普通段落 | 正文 | 仿宋_GB2312 12 pt，首行缩进 2 字 |
| 两列功能表、清单表 | 表格 | 功能表 9 pt；一般表 10.5 pt；表头黑体 |

## 4. 段落、表格、图片、附件

1. 正文每个自然段左空二字（首行缩进 24 pt = 12 pt × 2），回行顶格；段前段后 0；固定行距 22 磅。
2. 表格：五号或小五，表头黑体、内容仿宋_GB2312；表内单倍行距、段前段后 0；表头跨页重复；表格居中。
3. 图片：居中，宽度不超过版心 15.6 cm；图注小五楷体_GB2312 居中。
4. 附件：另面编排；版心左上角「附件N」（黑体小四）、附件标题居中（16 pt 小标宋）、说明一行（小五仿宋）、嵌入对象（预览图 15 cm 宽）。
5. **测试用例附件**：每个迭代 1 个 xlsx（4 个工作表：正常流程 / 异常操作 / 边界条件 / 权限校验），以嵌入 Excel 对象插入附件位；Word 正文与附录区不得出现用例表格、用例截图或 Markdown 表格；用例条数增加不得增加 Word 页数。
6. 页码：`— N —`，宋体五号，奇数页右空一字、偶数页左空一字。

## 5. Word 实现要点（python-docx）

```python
from docx.shared import Cm, Pt
from docx.enum.text import WD_LINE_SPACING

# 页面
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.top_margin, sec.bottom_margin = Cm(3.7), Cm(3.5)
sec.left_margin, sec.right_margin = Cm(2.8), Cm(2.6)
sec.footer_distance = Cm(2.8)

# 中文字体：必须同时设置 eastAsia / ascii / hAnsi
def set_run_font(run, cn, size_pt, bold=False):
    run.font.name = 'Times New Roman'
    run.font.size = Pt(size_pt)
    run.bold = bold
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    rFonts.set(qn('w:eastAsia'), cn)
    rFonts.set(qn('w:ascii'), 'Times New Roman')
    rFonts.set(qn('w:hAnsi'), 'Times New Roman')

# 正文字号 12pt、固定行距 22pt、首行缩进 24pt
p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
p.paragraph_format.line_spacing = Pt(22)
p.paragraph_format.first_line_indent = Pt(24)
p.paragraph_format.space_before = Pt(0)
p.paragraph_format.space_after = Pt(0)
```

- 页码：设置 `w:evenAndOddHeaders`，奇数页页脚右对齐、偶数页左对齐，内容为 `— PAGE 域 —`，宋体 10.5 pt。
- 表格：`table.autofit = False`，按内容设置列宽；表头行设置 `tblHeader`；单元格段落单倍行距。
- **图片段落必须单倍行距**：Normal 样式若为固定行距，内嵌图片会被裁切成一条缝（Word/WPS 均如此）；内嵌图片所在段落需 `line_spacing_rule = SINGLE`、段前段后 0。
- 交付前用真实字体环境打开核对；字体缺失按回退链处理并记录。

## 6. 交付验收清单（版式）

- [ ] A4；页边距上 3.7 / 下 3.5 / 左 2.8 / 右 2.6 cm；页脚 2.8 cm
- [ ] 文档标题方正小标宋简体 18 pt 居中
- [ ] 正文仿宋_GB2312 12 pt、首行缩进 2 字、固定行距 22 磅
- [ ] 一级标题黑体 15 pt、二级楷体_GB2312 14 pt、三级仿宋加粗 12 pt、四级仿宋 12 pt
- [ ] 数字与英文 Times New Roman
- [ ] 页码宋体 10.5 pt、`— N —`、奇右偶左
- [ ] 表格 9~10.5 pt、表头黑体、跨页重复表头、表内单倍行距
- [ ] 图片不超版心、图注五号楷体居中
- [ ] 测试用例附件为嵌入 Excel 对象（每迭代 1 个 xlsx、4 个工作表），正文无用例表格/截图
- [ ] 字体缺失已回退并在交付说明中记录
