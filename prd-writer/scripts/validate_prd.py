#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PRD 结构校验器（validate_prd.py）

用途：对按 prd-writer 技能生成的 PRD Markdown 做结构与一致性自动校验，
      覆盖质量门禁 G1–G5、G9 中可机械判断的部分；内容质量仍需人工按
      references/quality-checklist.md 核对。

用法：
    python validate_prd.py <PRD.md> [<PRD2.md> ...]   # 校验 PRD 文件
    python validate_prd.py --skill prd-writer/SKILL.md  # 校验技能文件
    python validate_prd.py --strict prd-writer/examples/PRD-*.md   # WARN 也视为失败
    python validate_prd.py --json prd-writer/examples/PRD-*.md     # 输出 JSON

退出码：0 = 无 ERROR（--strict 时还需无 WARN）；1 = 存在失败项；2 = 用法/文件错误。

仅依赖 Python 3.8+ 标准库。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

ERROR = "ERROR"
WARN = "WARN"
INFO = "INFO"

PRIORITIES = {"P0", "P1", "P2"}
SCENARIO_TYPES = {"正常流程", "异常操作", "边界条件", "权限校验"}

REQUIRED_TOP_SECTIONS = ["一、产品需求背景", "二、通用设计机制", "三、功能详细描述"]
REQUIRED_BG_SECTIONS = [
    "一句话价值", "文档说明", "业务背景", "产品目标", "版本目标",
    "使用角色", "功能清单", "功能框架图", "迭代规划",
]
REQUIRED_FIELDS = [
    "更新时间", "优先级", "迭代版本", "任务规划", "功能描述",
    "核心流程", "具体说明", "限制条件",
]
FEATURE_LIST_HEADER = ["序号", "功能模块", "功能名称", "所属迭代", "优先级", "备注"]
FEATURE_TABLE_HEADER = ["原型展示图", "功能描述"]
ROLE_TABLE_HEADER = ["角色", "权限与使用场景"]
ITER_PLAN_HEADER = ["迭代", "时间范围", "发布目标"]
REVISION_HEADER = ["版本", "日期", "修改人", "变更内容"]
PENDING_HEADER = ["序号", "文档位置", "待确认问题", "影响", "建议确认人"]
TESTCASE_REQUIRED = ["序号", "关联功能点", "用例名称", "场景类型", "前置条件", "测试步骤", "预期结果", "优先级"]

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
RANGE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}——\d{4}-\d{2}-\d{2}$")
ITER_RE = re.compile(r"^迭代\s*(\d+)$")
BUMP_RE = re.compile(r"^(\d+)\.(\d+)\s*【?\s*(.+?)\s*】?$")
FIELD_RE = re.compile(r"^\*\*\s*([^*]{1,12}?)\s*[：:]\s*\*\*\s*(.*)$")
NUM_RE = re.compile(r"^( *)(\d+(?:\.\d+)*)(\.?)\s+(.*)$")
PRIORITY_RE = re.compile(r"(P[0-2])")
PLACEHOLDER_PATTERNS = [
    (re.compile(r"【产品/模块名称】"), "模板占位符 【产品/模块名称】"),
    (re.compile(r"【大功能点名称】"), "模板占位符 【大功能点名称】"),
    (re.compile(r"【子功能名称】"), "模板占位符 【子功能名称】"),
    (re.compile(r"【此处插入原型图"), "模板占位符 【此处插入原型图】"),
    (re.compile(r"【角色名】|【模块】|【功能名称】|【修改人】"), "模板占位符"),
    (re.compile(r"(?<![A-Za-z0-9])x{3,}(?![A-Za-z0-9])", re.I), "模板占位符 xxx"),
]
# 日期占位符只在“字段值/区间”语境下判定为错误，避免误伤数据格式约定（如「时间 yyyy-mm-dd hh:mm:ss」）
DATE_PLACEHOLDER_ERROR = re.compile(
    r"(更新时间|任务规划|撰写日期|文档日期|修订日期)[：:]\s*\**\s*yyyy-mm-dd"
    r"|yyyy-mm-dd——yyyy-mm-dd"
)
DATE_PLACEHOLDER_ANY = re.compile(r"yyyy-mm-dd")
ENTITY_RE = re.compile(r"&(gt|lt|amp|quot|#\d+);")


def norm_name(text: str) -> str:
    """归一化功能名称用于跨章节比对：去括号、空白与标点。"""
    text = text.replace("【", "").replace("】", "").replace("《", "").replace("》", "")
    return re.sub(r"[\W_]+", "", text)


# --------------------------------------------------------------------------- #
# 数据结构
# --------------------------------------------------------------------------- #
@dataclass
class Issue:
    level: str
    check: str
    message: str
    line: int = 0

    def as_dict(self) -> dict:
        return {"level": self.level, "check": self.check, "line": self.line, "message": self.message}


@dataclass
class Row:
    cells: List[str]
    line: int


@dataclass
class Table:
    header: List[str]
    rows: List[Row]
    line: int


@dataclass
class Heading:
    level: int
    text: str
    line: int


@dataclass
class Feature:
    iteration: str
    big_index: int
    big_name: str
    sub_index: int
    name: str
    priority: str
    fields: Dict[str, str]
    line: int

    @property
    def number(self) -> str:
        return f"{self.big_index}.{self.sub_index}"


@dataclass
class Report:
    path: Path
    issues: List[Issue] = field(default_factory=list)
    info: List[str] = field(default_factory=list)
    feature_list: List[dict] = field(default_factory=list)
    features: List[Feature] = field(default_factory=list)
    markmap: Dict[str, object] = field(default_factory=dict)

    def add(self, level: str, check: str, message: str, line: int = 0) -> None:
        self.issues.append(Issue(level, check, message, line))

    @property
    def errors(self) -> int:
        return sum(1 for i in self.issues if i.level == ERROR)

    @property
    def warnings(self) -> int:
        return sum(1 for i in self.issues if i.level == WARN)

    @property
    def passed(self) -> bool:
        return self.errors == 0


# --------------------------------------------------------------------------- #
# 解析
# --------------------------------------------------------------------------- #
def split_cells(line: str) -> List[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def is_separator(line: str) -> bool:
    return bool(re.match(r"^\s*\|[\s:|-]+\|\s*$", line)) and "-" in line


def parse_tables(lines: Sequence[str]) -> List[Table]:
    tables: List[Table] = []
    i = 0
    n = len(lines)
    while i < n - 1:
        if lines[i].strip().startswith("|") and is_separator(lines[i + 1]):
            header = split_cells(lines[i])
            table = Table(header=header, rows=[], line=i + 1)
            j = i + 2
            while j < n and lines[j].strip().startswith("|"):
                if is_separator(lines[j]):
                    j += 1
                    continue
                table.rows.append(Row(cells=split_cells(lines[j]), line=j + 1))
                j += 1
            tables.append(table)
            i = j
        else:
            i += 1
    return tables


def parse_headings(lines: Sequence[str]) -> List[Heading]:
    out: List[Heading] = []
    in_fence = False
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", stripped)
        if m:
            out.append(Heading(level=len(m.group(1)), text=m.group(2), line=idx))
    return out


def section_bounds(headings: Sequence[Heading], title_line: int, level: int) -> Tuple[int, int]:
    """返回标题行之后、同级下一个标题之前的行号区间（1 基，含首尾行号）。"""
    end = len(headings)
    for h in headings:
        if h.line > title_line and h.level <= level:
            end = h.line
            break
    return title_line + 1, end - 1


def find_heading(headings: Sequence[Heading], predicate) -> Optional[Heading]:
    for h in headings:
        if predicate(h):
            return h
    return None


def table_after_line(tables: Sequence[Table], line: int) -> Optional[Table]:
    for t in tables:
        if t.line > line:
            return t
    return None


# --------------------------------------------------------------------------- #
# 校验：基础结构
# --------------------------------------------------------------------------- #
def check_title(rep: Report, lines: Sequence[str]) -> None:
    first = next((ln.strip() for ln in lines if ln.strip()), "")
    if not re.match(r"^#\s+.+产品需求文档\s*$", first):
        rep.add(ERROR, "G1-结构", "首行应为一级标题「# 《产品/模块名称》产品需求文档」", 1)


def check_doc_header(rep: Report, lines: Sequence[str]) -> None:
    head = "\n".join(lines[:15])
    for key in ("文档版本", "撰写日期", "状态"):
        if key not in head:
            rep.add(WARN, "G1-结构", f"文档头部缺少「{key}」信息（建议在标题下以引用块给出）")


def check_top_sections(rep: Report, headings: Sequence[Heading], lines: Sequence[str]) -> None:
    h2 = [h for h in headings if h.level == 2]
    texts = [h.text for h in h2]
    for required in REQUIRED_TOP_SECTIONS:
        if not any(t.startswith(required) for t in texts):
            rep.add(ERROR, "G1-结构", f"缺少一级章节「{required}」")
    for h in h2:
        if any(h.text.startswith(r) for r in REQUIRED_TOP_SECTIONS):
            continue
        if h.text.startswith("附录"):
            continue
        rep.add(WARN, "G1-结构", f"出现模板之外的顶级章节「{h.text}」", h.line)
    ordered = [next((h for h in h2 if h.text.startswith(r)), None) for r in REQUIRED_TOP_SECTIONS]
    ordered = [h for h in ordered if h is not None]
    if [h.line for h in ordered] != sorted(h.line for h in ordered):
        rep.add(ERROR, "G1-结构", "一级章节顺序错误：应为 一、产品需求背景 → 二、通用设计机制 → 三、功能详细描述")


def check_background_sections(rep: Report, headings: Sequence[Heading], lines: Sequence[str]) -> None:
    bg = find_heading(headings, lambda h: h.level == 2 and h.text.startswith("一、产品需求背景"))
    if not bg:
        return
    start, end = section_bounds(headings, bg.line, 2)
    patched = [h for h in headings if h.level == 3 and start <= h.line <= end]
    names = [h.text for h in patched]
    for required in REQUIRED_BG_SECTIONS:
        if not any(required in name for name in names):
            rep.add(ERROR, "G1-结构", f"「一、产品需求背景」缺少小节「{required}」")
    if len(patched) != len(REQUIRED_BG_SECTIONS):
        rep.add(WARN, "G1-结构",
                f"「一、产品需求背景」小节数量为 {len(patched)}，模板要求 {len(REQUIRED_BG_SECTIONS)}")
    for idx, h in enumerate(patched, start=1):
        m = re.match(r"^(\d+)、", h.text)
        if not m or int(m.group(1)) != idx:
            rep.add(WARN, "G1-结构", f"小节编号不连续：「{h.text}」应为「{idx}、…」", h.line)


def check_markdown_tables(rep: Report, tables: Sequence[Table]) -> None:
    for t in tables:
        width = len(t.header)
        if not t.rows:
            rep.add(WARN, "G1-表格", f"表格只有表头没有数据行（表头：{' | '.join(t.header[:3])}…）", t.line)
        for row in t.rows:
            if len(row.cells) != width:
                rep.add(ERROR, "G1-表格",
                        f"表格列数不一致：表头 {width} 列，本行 {len(row.cells)} 列（单元格被未转义的 | 截断）",
                        row.line)


def check_heading_jumps(rep: Report, headings: Sequence[Heading]) -> None:
    prev: Optional[Heading] = None
    for h in headings:
        if prev and h.level - prev.level > 1:
            rep.add(WARN, "G1-结构", f"标题层级跳级：H{prev.level}「{prev.text}」→ H{h.level}「{h.text}」", h.line)
        prev = h


# --------------------------------------------------------------------------- #
# 校验：章节内容
# --------------------------------------------------------------------------- #
def check_revision_table(rep: Report, tables: Sequence[Table]) -> None:
    target = next((t for t in tables if t.header == REVISION_HEADER), None)
    if not target:
        rep.add(ERROR, "G3-字段", "「文档说明」缺少修订记录表（版本｜日期｜修改人｜变更内容）")
        return
    if not target.rows:
        rep.add(ERROR, "G3-字段", "修订记录表没有数据行")
        return
    for row in target.rows:
        if not DATE_RE.match(row.cells[1]):
            rep.add(WARN, "G3-字段", f"修订记录日期格式应为 yyyy-mm-dd：{row.cells[1]}", row.line)


def check_roles_table(rep: Report, tables: Sequence[Table]) -> None:
    if not any(t.header == ROLE_TABLE_HEADER for t in tables):
        rep.add(WARN, "G3-字段", "「使用角色」缺少角色表（角色｜权限与使用场景）")


def check_feature_list(rep: Report, tables: Sequence[Table]) -> None:
    table = next((t for t in tables if t.header == FEATURE_LIST_HEADER), None)
    if not table:
        rep.add(ERROR, "G2-功能清单", "未找到「功能清单」表（表头应为 序号｜功能模块｜功能名称｜所属迭代｜优先级｜备注）")
        return
    if not table.rows:
        rep.add(ERROR, "G2-功能清单", "「功能清单」表没有数据行")
    for idx, row in enumerate(table.rows, start=1):
        cells = row.cells
        if len(cells) < 6:
            continue
        if not cells[0].isdigit() or int(cells[0]) != idx:
            rep.add(WARN, "G2-功能清单", f"功能清单序号应为 {idx}，实际为「{cells[0]}」", row.line)
        if not cells[2]:
            rep.add(ERROR, "G2-功能清单", "功能清单存在空的功能名称", row.line)
        if cells[4] not in PRIORITIES:
            rep.add(ERROR, "G2-功能清单", f"功能清单优先级非法：「{cells[4]}」（应为 P0/P1/P2）", row.line)
        if not ITER_RE.match(re.sub(r"\s+", "", cells[3])):
            rep.add(WARN, "G2-功能清单", f"功能清单所属迭代格式应为「迭代N」：「{cells[3]}」", row.line)
        rep.feature_list.append({
            "name": cells[2], "iter": re.sub(r"\s+", "", cells[3]),
            "priority": cells[4], "line": row.line,
        })


def check_iteration_plan(rep: Report, tables: Sequence[Table]) -> None:
    table = next((t for t in tables if t.header == ITER_PLAN_HEADER), None)
    if not table:
        rep.add(ERROR, "G2-迭代规划", "未找到「迭代规划」表（表头应为 迭代｜时间范围｜发布目标）")
        return
    if not table.rows:
        rep.add(ERROR, "G2-迭代规划", "「迭代规划」表没有数据行")
    for row in table.rows:
        if len(row.cells) < 3:
            continue
        if not RANGE_RE.match(row.cells[1]):
            rep.add(WARN, "G2-迭代规划",
                    f"迭代时间范围格式应为 yyyy-mm-dd——yyyy-mm-dd：「{row.cells[1]}」", row.line)
        if not row.cells[2]:
            rep.add(WARN, "G2-迭代规划", "迭代「发布目标」为空", row.line)


def parse_markmap(rep: Report, lines: Sequence[str]) -> None:
    in_block = False
    items: List[Tuple[int, str, int]] = []
    fence_line = 0
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not in_block and re.match(r"^```markmap\s*$", stripped):
            in_block = True
            fence_line = idx
            continue
        if in_block and stripped.startswith("```"):
            in_block = False
            continue
        if in_block:
            m = re.match(r"^(#{1,4})\s+(.+?)\s*$", stripped)
            if m:
                items.append((len(m.group(1)), m.group(2), idx))
    if not items:
        rep.add(ERROR, "G2-框架图", "第 8 节缺少 markmap 代码块（功能框架图数据源）")
        return
    rep.markmap["fence_line"] = fence_line
    levels = [i[0] for i in items]
    if levels[0] != 1:
        rep.add(ERROR, "G2-框架图", "markmap 根节点应为一级标题（# 版本名）", items[0][2])
    prev_level = 0
    for level, text, line in items:
        if prev_level and level - prev_level > 1:
            rep.add(ERROR, "G2-框架图", f"markmap 层级跳级：H{prev_level}「{text}」前缺少 H{prev_level + 1} 父节点", line)
        prev_level = level
    iterations = [t for l, t, _ in items if l == 2]
    bigs = [t for l, t, _ in items if l == 3]
    subs = [t for l, t, _ in items if l == 4]
    if not iterations:
        rep.add(ERROR, "G2-框架图", "markmap 缺少迭代层（## 迭代N功能描述）")
    if not bigs:
        rep.add(ERROR, "G2-框架图", "markmap 缺少大功能点层（### 大功能点）")
    if not subs:
        rep.add(ERROR, "G2-框架图", "markmap 缺少子功能层（#### 子功能）")
    rep.markmap.update({"iterations": iterations, "bigs": bigs, "subs": subs, "items": items})


# --------------------------------------------------------------------------- #
# 校验：功能正文
# --------------------------------------------------------------------------- #
def _split_cell(cell: str) -> List[str]:
    """按 <br> 拆分单元格；保留缩进（具体说明靠行首空格表达层级）。"""
    return [seg.rstrip() for seg in re.split(r"<br\s*/?>", cell)]


def _parse_feature_cell(rep: Report, cells: List[str], row_line: int, iteration: str) -> None:
    right = cells[1]
    segments = _split_cell(right)
    if not segments or not segments[0].strip():
        rep.add(ERROR, "G3-字段", "功能描述单元格为空", row_line)
        return
    title = segments[0].strip()
    m = re.match(r"^\*\*\s*(\d+)\.(\d+)\s*【?\s*(.+?)\s*】?\s*\*\*$", title)
    if not m:
        rep.add(ERROR, "G3-字段", f"子功能首行应为加粗编号标题，如「**1.1【名称】**」，实际为「{title[:40]}」", row_line)
        return
    big_index, sub_index = int(m.group(1)), int(m.group(2))
    name = m.group(3).strip()
    fields: Dict[str, str] = {}
    current: Optional[str] = None
    for seg in segments[1:]:
        stripped = seg.strip()
        fm = FIELD_RE.match(stripped)
        if fm and fm.group(1).strip() in REQUIRED_FIELDS:
            current = fm.group(1).strip()
            fields.setdefault(current, "")
            if fm.group(2).strip():
                fields[current] += fm.group(2).strip()
        elif current:
            fields[current] += ("\n" if fields[current] else "") + seg
    for required in REQUIRED_FIELDS:
        if required not in fields or not fields[required].strip():
            rep.add(ERROR, "G3-字段", f"子功能 {big_index}.{sub_index}「{name}」缺少字段「{required}」或内容为空", row_line)
    feature = Feature(
        iteration=iteration, big_index=big_index, big_name="", sub_index=sub_index,
        name=name, priority=_extract_priority(fields.get("优先级", "")), fields=fields, line=row_line,
    )
    rep.features.append(feature)


def _extract_priority(text: str) -> str:
    m = PRIORITY_RE.search(text)
    return m.group(1) if m else text.strip().strip("* ")


def check_field_values(rep: Report, feature: Feature) -> None:
    f = feature.fields
    label = f"{feature.number}「{feature.name}」"
    if "更新时间" in f and not DATETIME_RE.match(f["更新时间"].strip().strip("*")):
        rep.add(ERROR, "G3-字段", f"{label} 更新时间格式应为 yyyy-mm-dd hh:mm:ss：「{f['更新时间'][:30]}」", feature.line)
    prio = _extract_priority(f.get("优先级", ""))
    if prio not in PRIORITIES:
        rep.add(ERROR, "G3-字段", f"{label} 优先级应为 P0/P1/P2：「{prio[:20]}」", feature.line)
    iter_text = f.get("迭代版本", "").strip().strip("*").replace(" ", "")
    if iter_text and not ITER_RE.match(iter_text):
        rep.add(WARN, "G3-字段", f"{label} 迭代版本格式应为「迭代N」：「{iter_text}」", feature.line)
    elif iter_text and iter_text != feature.iteration:
        rep.add(ERROR, "G3-字段", f"{label} 迭代版本「{iter_text}」与其所在章节「{feature.iteration}」不一致", feature.line)
    plan = f.get("任务规划", "").strip()
    if plan and not RANGE_RE.match(plan):
        rep.add(ERROR, "G3-字段", f"{label} 任务规划格式应为 yyyy-mm-dd——yyyy-mm-dd：「{plan[:40]}」", feature.line)
    desc = re.sub(r"[*`#>\s]+", "", f.get("功能描述", ""))
    if len(desc) > 150:
        rep.add(ERROR, "G3-字段", f"{label} 功能描述为 {len(desc)} 字，超过 150 字上限", feature.line)
    if "核心流程" in f and "→" not in f["核心流程"]:
        rep.add(WARN, "G3-字段", f"{label} 核心流程未使用「 → 」串联步骤", feature.line)
    check_spec_numbering(rep, feature)


def check_spec_numbering(rep: Report, feature: Feature) -> None:
    content = feature.fields.get("具体说明", "")
    items = [ln for ln in content.split("\n") if ln.strip()]
    if not items:
        return
    seen: Dict[Tuple[int, ...], int] = {}
    last_depth = 0
    for raw in items:
        line_text = raw.replace("&nbsp;", " ").rstrip()
        m = NUM_RE.match(line_text)
        if not m:
            rep.add(ERROR, "G4-编号",
                    f"{feature.number}「{feature.name}」具体说明存在无法识别的编号行：「{line_text[:40]}」", feature.line)
            continue
        indent = len(m.group(1))
        path = tuple(int(x) for x in m.group(2).split("."))
        depth = len(path)
        has_dot = bool(m.group(3))
        if depth == 1 and not has_dot:
            rep.add(ERROR, "G4-编号", f"{feature.number} 一级编号应带「.」：「{line_text[:40]}」", feature.line)
        if depth > 1 and has_dot:
            rep.add(ERROR, "G4-编号", f"{feature.number} 二/三/四级编号不应带「.」：「{line_text[:40]}」", feature.line)
        expected_indent = (depth - 1) * 4
        if indent != expected_indent:
            rep.add(ERROR, "G4-编号",
                    f"{feature.number} 编号「{m.group(2)}」缩进 {indent} 空格，应为 {expected_indent} 空格", feature.line)
        if depth > last_depth + 1:
            rep.add(ERROR, "G4-编号",
                    f"{feature.number} 编号跳级：「{m.group(2)}」直接出现在深度 {last_depth} 之后", feature.line)
        last_depth = depth
        parent = path[:-1]
        expected = seen.get(parent, 0) + 1
        if path[-1] != expected:
            rep.add(ERROR, "G4-编号",
                    f"{feature.number} 编号不连续：期望 {'.'.join(map(str, parent + (expected,)))}，实际 {m.group(2)}",
                    feature.line)
        seen[parent] = path[-1]


def check_body(rep: Report, headings: Sequence[Heading], tables: Sequence[Table],
               lines: Sequence[str]) -> None:
    body = find_heading(headings, lambda h: h.level == 2 and h.text.startswith("三、功能详细描述"))
    if not body:
        return
    start, end = section_bounds(headings, body.line, 2)
    body_headings = [h for h in headings if start <= h.line <= end]
    iterations = [h for h in body_headings if h.level == 4]
    if not iterations:
        rep.add(ERROR, "G1-结构", "「三、功能详细描述」下缺少「#### 迭代N功能描述」章节")
        return
    for h in iterations:
        if not re.match(r"^迭代\s*\d+\s*功能描述$", h.text):
            rep.add(WARN, "G1-结构", f"迭代章节标题应为「迭代N功能描述」：「{h.text}」", h.line)
    for iter_h in iterations:
        iter_name = re.sub(r"\s+", "", iter_h.text.replace("功能描述", ""))
        next_iter = next((h for h in iterations if h.line > iter_h.line), None)
        limit = next_iter.line if next_iter else end
        bigs = [h for h in body_headings
                if h.line > iter_h.line and h.line < limit and h.level == 5
                and not h.text.startswith("附件")]
        if not bigs:
            rep.add(ERROR, "G1-结构", f"{iter_name} 下没有任何「##### N、大功能点」章节", iter_h.line)
            continue
        expected_big = 1
        for big in bigs:
            m = re.match(r"^(\d+)、\s*(.+)$", big.text)
            if not m:
                rep.add(ERROR, "G1-结构", f"大功能点标题应为「N、名称」：「{big.text}」", big.line)
                continue
            if int(m.group(1)) != expected_big:
                rep.add(ERROR, "G1-结构", f"{iter_name} 大功能点编号不连续：应为 {expected_big}，实际 {m.group(1)}", big.line)
            expected_big = int(m.group(1)) + 1
            big_index, big_name = int(m.group(1)), m.group(2)
            table = table_after_line(tables, big.line)
            next_big = next((h.line for h in bigs if h.line > big.line), limit)
            if not table or table.line >= next_big:
                rep.add(ERROR, "G1-结构", f"{iter_name} 大功能点「{big.text}」下缺少两列功能表", big.line)
                continue
            if table.header != FEATURE_TABLE_HEADER:
                rep.add(ERROR, "G1-结构",
                        f"{iter_name} 大功能点「{big.text}」表格表头应为「原型展示图｜功能描述」，实际为「{' | '.join(table.header)}」",
                        table.line)
                continue
            for row in table.rows:
                if len(row.cells) < 2:
                    rep.add(ERROR, "G1-表格", "功能表行缺少单元格", row.line)
                    continue
                before = len(rep.features)
                _parse_feature_cell(rep, row.cells, row.line, iter_name)
                if len(rep.features) > before:
                    rep.features[-1].big_index = big_index
                    rep.features[-1].big_name = big_name
    # 子功能编号连续性
    by_iter: Dict[str, List[Feature]] = {}
    for f in rep.features:
        by_iter.setdefault(f.iteration, []).append(f)
    for iteration, feats in by_iter.items():
        for f in feats:
            check_field_values(rep, f)
        current_big = None
        expected_sub = 1
        for f in feats:
            if current_big != f.big_index:
                current_big, expected_sub = f.big_index, 1
            if f.sub_index != expected_sub:
                rep.add(ERROR, "G4-编号",
                        f"{iteration} 大功能点 {f.big_index} 下子功能编号不连续：应为 {f.big_index}.{expected_sub}，实际 {f.number}",
                        f.line)
            expected_sub += 1


def check_consistency(rep: Report) -> None:
    if not rep.feature_list or not rep.features:
        return
    if len(rep.feature_list) != len(rep.features):
        rep.add(ERROR, "G2-一致性",
                f"功能数量不一致：功能清单 {len(rep.feature_list)} 项，正文 {len(rep.features)} 项")
    list_names = [norm_name(item["name"]) for item in rep.feature_list]
    body_names = [norm_name(f.name) for f in rep.features]
    missing_in_body = [n for n in list_names if n not in body_names]
    missing_in_list = [n for n in body_names if n not in list_names]
    if missing_in_body:
        rep.add(ERROR, "G2-一致性", f"功能清单中有、正文中未找到：{'、'.join(missing_in_body[:5])}")
    if missing_in_list:
        rep.add(ERROR, "G2-一致性", f"正文中有、功能清单中未找到：{'、'.join(missing_in_list[:5])}")
    list_priority = {norm_name(i["name"]): i["priority"] for i in rep.feature_list}
    for f in rep.features:
        prio = list_priority.get(norm_name(f.name))
        if prio and prio != f.priority:
            rep.add(ERROR, "G2-一致性", f"「{f.name}」优先级不一致：清单 {prio}，正文 {f.priority}", f.line)
    list_iter = {norm_name(i["name"]): i["iter"] for i in rep.feature_list}
    for f in rep.features:
        it = list_iter.get(norm_name(f.name))
        if it and it != f.iteration:
            rep.add(ERROR, "G2-一致性", f"「{f.name}」所属迭代不一致：清单 {it}，正文 {f.iteration}", f.line)
    # 迭代覆盖
    body_iters = sorted({f.iteration for f in rep.features}, key=lambda s: int(re.sub(r"\D", "", s) or 0))
    list_iters = {i["iter"] for i in rep.feature_list}
    for it in body_iters:
        if it not in list_iters:
            rep.add(WARN, "G2-一致性", f"正文迭代「{it}」在功能清单中无对应功能")
    # markmap
    subs = rep.markmap.get("subs") or []
    if subs:
        if len(subs) != len(rep.features):
            rep.add(ERROR, "G2-框架图",
                    f"功能框架图子功能数 {len(subs)} 与正文子功能数 {len(rep.features)} 不一致")
        mark_names = {norm_name(s) for s in subs}
        for f in rep.features:
            if norm_name(f.name) not in mark_names:
                rep.add(WARN, "G2-框架图", f"功能框架图缺少子功能「{f.name}」（或命名不一致）", f.line)


def check_pending(rep: Report, lines: Sequence[str], tables: Sequence[Table]) -> None:
    text = "\n".join(lines)
    pending_count = len(re.findall(r"【待确认", text))
    appendix = next((t for t in tables if t.header == PENDING_HEADER), None)
    if pending_count and not appendix:
        rep.add(ERROR, "G5-待确认", f"正文存在 {pending_count} 处【待确认】，但缺少「附录 A、待确认清单」表")
    if appendix and not appendix.rows:
        rep.add(WARN, "G5-待确认", "附录 A 待确认清单没有数据行")
    if appendix:
        rep.add(INFO, "G5-待确认", f"待确认清单记录 {len(appendix.rows)} 条，正文【待确认】标注 {pending_count} 处")


def check_placeholders(rep: Report, lines: Sequence[str]) -> None:
    in_fence = False
    for idx, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        for pattern, message in PLACEHOLDER_PATTERNS:
            if pattern.search(line):
                rep.add(ERROR, "G9-占位", f"存在未替换的{message}", idx)
        if DATE_PLACEHOLDER_ERROR.search(line):
            rep.add(ERROR, "G9-占位", "存在未替换的日期占位符 yyyy-mm-dd", idx)
        elif DATE_PLACEHOLDER_ANY.search(line):
            rep.add(INFO, "G9-占位",
                    "出现 yyyy-mm-dd：若为数据格式说明可忽略，若为日期字段残留请替换为真实日期")
        for m in ENTITY_RE.finditer(line):
            rep.add(ERROR, "G9-占位", f"存在字面量 HTML 实体「&{m.group(1)};」，应使用真实字符或 <br>", idx)
    if in_fence:
        rep.add(ERROR, "G9-格式", "代码块未闭合（缺少结束的 ```）")


def check_testcases(rep: Report, tables: Sequence[Table]) -> None:
    found = 0
    for t in tables:
        if "关联功能点" not in t.header:
            continue
        found += 1
        if t.header != TESTCASE_REQUIRED:
            rep.add(ERROR, "G7-测试用例", f"测试用例表头应为 8 列固定顺序，实际为「{' | '.join(t.header)}」", t.line)
            continue
        if not t.rows:
            rep.add(WARN, "G7-测试用例", "测试用例表没有数据行", t.line)
        feature_numbers = {f.number for f in rep.features}
        feature_numbers |= {str(f.big_index) for f in rep.features}
        expected_seq = 1
        for row in t.rows:
            cells = row.cells
            if len(cells) < 8:
                continue
            if not cells[0].isdigit() or int(cells[0]) != expected_seq:
                rep.add(WARN, "G7-测试用例", f"用例序号应为 {expected_seq}，实际「{cells[0]}」", row.line)
            expected_seq = int(cells[0]) + 1 if cells[0].isdigit() else expected_seq + 1
            if not cells[1]:
                rep.add(ERROR, "G7-测试用例", "关联功能点为空", row.line)
            else:
                m = re.match(r"^(\d+\.\d+)(?:-\d+(?:\.\d+)*)?$", cells[1].strip())
                if not m:
                    rep.add(WARN, "G7-测试用例",
                            f"关联功能点格式应为「1.2」或「1.2-2.2.1」：「{cells[1]}」", row.line)
                elif m.group(1) not in feature_numbers:
                    rep.add(WARN, "G7-测试用例",
                            f"关联功能点「{cells[1]}」在正文中找不到对应子功能", row.line)
            if cells[3] not in SCENARIO_TYPES:
                rep.add(ERROR, "G7-测试用例",
                        f"场景类型非法：「{cells[3]}」（应为 {'/'.join(sorted(SCENARIO_TYPES))}）", row.line)
            if cells[7] not in PRIORITIES:
                rep.add(ERROR, "G7-测试用例", f"用例优先级非法：「{cells[7]}」", row.line)
            if not cells[5] or not cells[6]:
                rep.add(ERROR, "G7-测试用例", "测试步骤或预期结果为空", row.line)
            if not cells[4]:
                rep.add(WARN, "G7-测试用例", "前置条件为空（无法独立执行）", row.line)
    if found:
        rep.add(INFO, "G7-测试用例", f"共发现 {found} 张测试用例表")


# --------------------------------------------------------------------------- #
# 校验：技能文件（--skill）
# --------------------------------------------------------------------------- #
def check_skill_file(path: Path) -> Report:
    rep = Report(path=path)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        rep.add(ERROR, "SK-元数据", "SKILL.md 必须以 YAML frontmatter（---）开头", 1)
        return rep
    end = next((i for i, ln in enumerate(lines[1:], start=2) if ln.strip() == "---"), None)
    if end is None:
        rep.add(ERROR, "SK-元数据", "frontmatter 未闭合（缺少结束的 ---）", 1)
        return rep
    meta: Dict[str, str] = {}
    for idx in range(2, end):
        raw = lines[idx - 1].rstrip()
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if raw[:1] in (" ", "\t"):
            continue  # 缩进行属于嵌套映射（如 metadata 内部），不计为顶层字段
        m = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if m:
            meta[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    name = meta.get("name", "")
    if not name:
        rep.add(ERROR, "SK-元数据", "frontmatter 缺少必填字段 name", 1)
    elif not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", name):
        rep.add(ERROR, "SK-元数据", f"name 只能包含小写字母、数字与连字符：「{name}」", 1)
    elif len(name) > 64:
        rep.add(ERROR, "SK-元数据", f"name 长度 {len(name)} 超过 64 字符", 1)
    if name and path.parent.name and name != path.parent.name:
        rep.add(WARN, "SK-元数据", f"name「{name}」与父目录名「{path.parent.name}」不一致（规范要求一致）", 1)
    if "version" in meta:
        rep.add(WARN, "SK-元数据",
                "顶层 version 不是 Agent Skills 规范字段（claude.ai 上传/Skills API 会报 Unexpected key），"
                "应改为 metadata.version", 1)
    if "metadata" not in meta:
        rep.add(WARN, "SK-元数据", "建议用 metadata.version 记录技能版本")
    desc = meta.get("description", "")
    if not desc:
        rep.add(ERROR, "SK-元数据", "frontmatter 缺少必填字段 description", 1)
    elif len(desc) > 1024:
        rep.add(ERROR, "SK-元数据", f"description 长度 {len(desc)} 超过 1024 字符", 1)
    else:
        rep.add(INFO, "SK-元数据", f"name={name}，description {len(desc)} 字符")
    if len(lines) > 500:
        rep.add(WARN, "SK-结构", f"SKILL.md 共 {len(lines)} 行，超过渐进披露建议的 500 行，建议拆分到 references/")
    skill_dir = path.parent
    refs = set(re.findall(r"`((?:templates|references|scripts|examples)/[^`\s]*)`", text))
    for ref in sorted(refs):
        target = skill_dir / ref
        if target.exists():
            continue
        kind = "目录" if ref.endswith("/") else "文件"
        rep.add(ERROR, "SK-引用", f"引用的{kind}不存在：{ref}（相对 SKILL.md）")
    if not refs:
        rep.add(WARN, "SK-结构", "SKILL.md 未引用任何 templates/references/scripts 文件，未使用渐进披露")
    rep.add(INFO, "SK-引用", f"检查 {len(refs)} 个引用路径")
    return rep


# --------------------------------------------------------------------------- #
# 主流程
# --------------------------------------------------------------------------- #
def validate_prd(path: Path) -> Report:
    rep = Report(path=path)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    headings = parse_headings(lines)
    tables = parse_tables(lines)
    rep.__dict__["_tables"] = tables
    if not text.strip():
        rep.add(ERROR, "文件", "文件为空")
        return rep
    check_title(rep, lines)
    check_doc_header(rep, lines)
    check_top_sections(rep, headings, lines)
    check_background_sections(rep, headings, lines)
    check_heading_jumps(rep, headings)
    check_markdown_tables(rep, tables)
    check_revision_table(rep, tables)
    check_roles_table(rep, tables)
    check_feature_list(rep, tables)
    check_iteration_plan(rep, tables)
    parse_markmap(rep, lines)
    check_body(rep, headings, tables, lines)
    check_consistency(rep)
    check_pending(rep, lines, tables)
    check_placeholders(rep, lines)
    check_testcases(rep, tables)
    return rep


def print_report(report: Report, verbose: bool = True) -> None:
    order = {ERROR: 0, WARN: 1, INFO: 2}
    issues = sorted(report.issues, key=lambda i: (order.get(i.level, 9), i.line))
    print(f"\n== 校验文件：{report.path} ==")
    shown = [i for i in issues if i.level != INFO or verbose]
    for issue in shown:
        loc = f"L{issue.line}" if issue.line else "-"
        print(f"[{issue.level:<5}] ({loc}) {issue.check}: {issue.message}")
    if not shown:
        print("未发现问题。")
    if verbose:
        for info in report.info:
            print(f"[INFO ] {info}")
    print(f"-- 汇总：ERROR {report.errors} / WARN {report.warnings} / "
          f"功能清单 {len(report.feature_list)} 项 / 正文子功能 {len(report.features)} 项 --")
    print("-- 结论：" + ("通过" if report.passed else "不通过（存在 ERROR）") + " --")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="PRD 结构校验器（prd-writer 技能配套工具）",
        epilog="示例：python validate_prd.py prd-writer/examples/PRD-示例-在线考试系统.md",
    )
    parser.add_argument("files", nargs="+", help="待校验的 PRD Markdown 文件")
    parser.add_argument("--skill", action="store_true", help="按技能文件（SKILL.md）模式校验")
    parser.add_argument("--strict", action="store_true", help="WARN 也视为失败")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    parser.add_argument("--quiet", action="store_true", help="隐藏 INFO 信息")
    args = parser.parse_args(argv)

    reports: List[Report] = []
    for raw in args.files:
        path = Path(raw)
        if not path.exists():
            print(f"[ERROR] 文件不存在：{path}", file=sys.stderr)
            return 2
        if args.skill or path.name == "SKILL.md":
            reports.append(check_skill_file(path))
        else:
            if path.suffix.lower() != ".md":
                print(f"[WARN ] 跳过非 Markdown 文件：{path}", file=sys.stderr)
                continue
            reports.append(validate_prd(path))

    if args.json:
        payload = {
            "passed": all(r.passed for r in reports),
            "reports": [
                {
                    "path": str(r.path),
                    "errors": r.errors,
                    "warnings": r.warnings,
                    "issues": [i.as_dict() for i in r.issues],
                }
                for r in reports
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for report in reports:
            print_report(report, verbose=not args.quiet)

    failed = any((r.errors > 0) or (args.strict and r.warnings > 0) for r in reports)
    if len(reports) > 1 and not args.json:
        print(f"\n== 总计：{len(reports)} 个文件，"
              f"{sum(r.errors for r in reports)} 个 ERROR，"
              f"{sum(r.warnings for r in reports)} 个 WARN ==")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
