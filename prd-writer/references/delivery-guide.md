# 交付指南

> **何时读取本文件**：SKILL.md 阶段 6「交付」开始时读取——Markdown 草稿已获用户确认，需要转换为 Word、渲染功能框架图、把测试用例以嵌入 Excel 对象插入 Word、并在生成后自动用 WPS 打开。本文件提供可执行命令、Windows 与 macOS 差异、脚本骨架、失败降级路径与交付验证清单。 本文件中的引用路径均相对技能根目录（SKILL.md 所在目录）。

## 目录

1 交付物清单与生成顺序；2 依赖检查与安装；3 转换链路选择（3.1 docxtpl；3.2 WPS 双应用嵌入）；4 链路 A（pandoc）；5 链路 B（python-docx 自动多级编号）；6 功能框架图渲染为 PNG；7 测试用例嵌入 Excel 对象；8 生成后自动打开；9 失败降级策略；10 交付验证清单；11 交付说明话术模板。

## 1. 交付物清单与生成顺序

| 顺序 | 交付物 | 格式 | 生成方式 | 验证方式 |
|---|---|---|---|---|
| 1 | 功能框架图 | .png | 第 6 节渲染 | 目视核对大功能点/子功能数量 |
| 2 | Markdown 草稿（已确认） | .md | 起草阶段产出 | 质量门禁自查通过 |
| 3 | 测试用例表（按需） | .xlsx | openpyxl，8 列表头 | 表头、序号、场景类型核对 |
| 4 | Word 文档主体 | .docx | 链路 A / B / B2 | 第 10 节检查清单 |
| 5 | 嵌入 Excel 对象的 Word | .docx | 第 7 节 COM 或第 3.2 节 WPS 双应用 | 双击对象可编辑 |
| 6 | 自动打开 | — | 第 8 节命令 | 窗口可见 |

顺序硬约束：先渲染 PNG 与生成 xlsx，再合成 docx；否则需二次打开文档插入，增加出错面。Markdown 草稿中以图片语法引用 framework.png，转换时直接嵌入。产物命名遵循 `PRD-{产品/模块}-V{x.y}.docx`，建议输出到 `docs/prd/`；用户指定路径时以用户为准。

## 2. 依赖检查与安装

Windows 使用 `python` 与 PowerShell 7；macOS 使用 `python3` 与 zsh；装包统一用 `python -m pip`（macOS 为 `python3 -m pip`）。

| 依赖 | 用途 | 检查命令 | 未安装时 |
|---|---|---|---|
| Python 3.8+ | 运行校验脚本与交付脚本 | `python --version`<br>`python3 --version` | 安装 3.11+ 并加入 PATH（Windows 勾选 Add to PATH） |
| python-docx | 链路 B 生成 Word | `python -c "import docx; print(docx.__version__)"` | `python -m pip install python-docx` |
| openpyxl | 生成用例 xlsx | `python -c "import openpyxl"` | `python -m pip install openpyxl` |
| pandoc | 链路 A 转换 | `pandoc --version` | Windows `winget install --id JohnMacFarlane.Pandoc -e`；macOS `brew install pandoc`；不可安装改走链路 B |
| Node.js 与渲染工具 | 框架图渲染 | `node --version`<br>`mmdc --version`<br>`markmap --version` | `npm install -g @mermaid-js/mermaid-cli`；不可用时改用 `npm install -g markmap-cli` + 无头浏览器截图 |
| 浏览器 | 无头截图 | Windows 默认路径 `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`<br>macOS `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` | 用已装浏览器手动截图 |
| pywin32 | Word COM 嵌入对象 | `python -c "import win32com.client"` | `python -m pip install pywin32`；失败后执行 `python -m pywin32_postinstall -install` |
| WPS Office / Microsoft Word | 打开与 OLE 嵌入 | Windows `Get-Command wps`；macOS `ls /Applications` | 安装 WPS 或 Office；只能打开时按第 7、8 节降级 |

## 3. 转换链路选择

| 场景 | 推荐链路 | 原因 | 限制 |
|---|---|---|---|
| 要求「一、/1、/1.1 自动多级编号」「嵌入 Excel」，且本机只有 WPS | B3：WPS 文字 + WPS 表格双应用（见 3.2，无需 Microsoft Office） | 用 WPS 两个应用完成 OLE 嵌入；已验证可行 | 依赖 WPS COM；保存后需做每子功能编号重置后处理 |
| 要求「一、/1、/1.1 自动多级编号」「嵌入 Excel」且可准备一份 Word 模板 | B2：docxtpl + 预定义 Word 模板 | 编号与嵌入对象由模板预先定义，渲染只替换文本 | 需先维护一份模板 .docx |
| 结构标准、以标题与表格为主、接受参考样式 | A：pandoc + reference.docx | 一条命令转换，格式统一 | 自动多级编号需在 reference.docx 中预先绑定并实测 |
| 无法准备模板、要求完全代码化生成 | B：python-docx 脚本 | 精确控制编号定义、缩进与样式绑定 | 需维护脚本；复杂表格逐项构建 |
| 文档短、可接受人工排版 | C：Word/WPS 手工 | 零依赖 | 不可自动化，易漏编号 |

选择规则：本机只有 WPS 时优先 B3（无需 Microsoft Office）；能维护 Word 模板时选 B2；pandoc 默认输出不保证自动多级编号（见 pandoc issue #1413），因此除非已在 reference.docx 完成编号绑定并抽样验证，不要选链路 A。其余场景按 **B3 → B2 docxtpl → B python-docx → A pandoc → C 手工** 选择。

### 3.1 链路 B2：docxtpl + 预定义 Word 模板（优先推荐）

适用条件：本机有 Word 或 WPS 可编辑模板；需要同时满足「自动多级编号」与「嵌入 Excel」两项硬要求。

1. 制作模板 `prd-template.docx`：在 Word 中把「标题 1」到「标题 5」通过「开始 → 多级列表 → 定义新的多级列表」绑定层级编号（一、/ 1、/ 1.1 / 1.1.1 / 1.1.1.1），把「具体说明」条目绑定为独立的多级列表；在测试用例附件位手动插入一个空白 Excel 对象作为占位；保存为 `.docx` 模板。
2. 安装依赖：`python -m pip install docxtpl`（docxtpl 依赖 python-docx 与 Jinja2）。
3. 在模板中写 Jinja 标签（如 `{{ 一句话价值 }}`、`{%tr for f in features %}`），脚本把 PRD 结构化数据渲染进模板，生成 `PRD.docx`。
4. 用真实 xlsx 替换模板中的占位嵌入对象：**优先** `tpl.replace_zipname("word/embeddings/xxx.xlsx", "迭代1测试用例.xlsx")`，其中 xxx 从模板解压后的 `word/embeddings/` 目录中取得；Word 保存过的模板对 Excel 类嵌入对象常出现 CRC 不匹配，按 zip 路径替换更稳。若模板内对象名与需求匹配，也可用 `tpl.replace_embedded("embedded_dummy.xlsx", "迭代1测试用例.xlsx")`。仅对嵌入的 Office 文件有效，PDF/文本类对象不可替换。
5. 验证：解压生成物检查 `word/embeddings/*.xlsx` 存在、`word/numbering.xml` 有编号定义；用 Word/WPS 打开确认标题编号自动显示、双击 Excel 对象可编辑。docxtpl 替换嵌入对象后缩略图可能仍是旧图，双击激活即可刷新，交付前须确认。

优势：编号与对象都是 Word 自己产出的，不依赖手写 OOXML；缺点是需要维护模板文件，且模板样式变更需同步脚本。若无法维护模板，再按第 5 节用 python-docx 注入编号。

### 3.2 链路 B3：WPS 文字 + WPS 表格双应用嵌入（无需 Microsoft Office，已验证）

适用：本机只有 WPS（注册表存在 `KWPS.Application`、`KET.Application`），且必须满足「自动多级编号 + 嵌入 Excel 对象」。

1. 用 python-docx 生成 Word 主体（标题、表格、框架图 PNG；测试用例位置保留占位段 `@@TESTCASE_OLE@@`）。标题编号可按第 5 节注入；不要依赖 Word 生成。
2. WPS 文字打开 docx：`$writer = New-Object -ComObject KWPS.Application`，`$doc = $writer.Documents.Open("<docx>")`；**必须 `$writer.Visible = $true` 并 `$doc.Activate()`**，否则 `$doc.Selection` 为 null。
3. WPS 表格打开 xlsx 并复制区域：`$sheet = New-Object -ComObject KET.Application`，`$worksheet.UsedRange.Copy()`。
4. 在 WPS 文字中定位占位段、清空后执行 `$writer.Selection.PasteSpecial(0, $false, 0, $false, 0)`，把区域粘贴为 OLE 对象；`$doc.SaveAs("<docx>", 16)` 保存。
5. **编号重置后处理（必做）**：WPS 保存会把同一 `abstractNum` 的列表归并成一个 `numId`，导致不同子功能的「具体说明」「限制条件」连续编号。保存后须遍历功能表，为每个子功能克隆独立的 `abstractNum` + `numId`（各层 `w:start=1`），并把该子功能的列表段落重新挂到自己的 `numId`。
6. 验收：解压 docx 检查 `word/embeddings/oleObject1.bin`、`<o:OLEObject ... ProgID="Excel.Sheet.12">`、`word/media/image1.png`；确认每个子功能的「具体说明」「限制条件」`numId` 互不相同且 `w:start=1`；最后用 WPS 打开，双击对象确认可编辑。

注意：WPS 文字 COM 的 `InlineShapes.AddOLEObject` 不支持（返回 E_FAIL），不要走该 API；跨应用剪贴板粘贴是已验证的替代。WPS 进程会附加到用户已打开的实例，自动化前先记录进程 ID，结束后只清理本次新建的进程，避免影响用户正在编辑的文档。

## 4. 链路 A：pandoc + reference.docx

1. 验证 pandoc：`pandoc --version` 应返回 3.x（旧版参数为 `--reference-docx`）。不要依赖 pandoc 的 `--number-sections` 产出 Word 自动多级编号，该能力在 docx 中不可靠，须以第 5 节方式或实测结论为准。
2. 生成参考文档。用二进制安全的方式重定向：PowerShell 7.4+ 可直接 `pandoc --print-default-data-file reference.docx > reference.docx`（7.4 起原生命令重定向保持字节）；更早版本用 `cmd /c "pandoc --print-default-data-file reference.docx > reference.docx"`；macOS / Linux 直接 `pandoc --print-default-data-file reference.docx > reference.docx`。不要用文本管道（如 `| Set-Content`），会按文本解码并损坏 docx。
3. 用 Word 或 WPS 打开 reference.docx，设置 Heading 1–4 的字体与间距，并通过「开始 → 多级列表 → 定义新的多级列表」把级别 1–4 链接到「标题 1–4」样式，保存为模板复用。
4. 转换：`pandoc prd.md -f gfm -t docx --reference-doc=reference.docx -o PRD.docx`。
5. 抽样验证：`<br>` 是否成为单元格内换行、表格列数是否完整、标题编号是否自动显示。若 `<br>` 变字面文本，改用行尾反斜杠或两个空格换行后重转；若标题无自动编号，改走链路 B。

## 5. 链路 B：python-docx 自动多级编号

python-docx 未提供多级编号高层 API，需直接操作编号部件（numbering.xml）并绑定标题样式。以下骨架在 python-docx 1.x 上已完成编号构造与保存验证（默认模板自带编号部件，注入后可正常保存与重开）；编号显示效果仍需按执行要点第 4、5 条在 Word 中确认。

```python
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ABS_ID = NUM_ID = 90

def build_numbering(doc):
    numbering = doc.part.numbering_part.element
    abstract = OxmlElement("w:abstractNum")
    abstract.set(qn("w:abstractNumId"), str(ABS_ID))
    mlt = OxmlElement("w:multiLevelType"); mlt.set(qn("w:val"), "multilevel"); abstract.append(mlt)
    # 编号样式示例：一、/ 1、/ 1.1 / 1.1.1；按模板实际标题层级调整 formats
    formats = [("chineseCounting", "%1、"), ("decimal", "%2、"),
               ("decimal", "%2.%3"), ("decimal", "%2.%3.%4")]
    for ilvl, (fmt, text) in enumerate(formats):
        lvl = OxmlElement("w:lvl"); lvl.set(qn("w:ilvl"), str(ilvl))
        for tag, val in (("w:start", "1"), ("w:numFmt", fmt), ("w:lvlText", text), ("w:lvlJc", "left")):
            el = OxmlElement(tag); el.set(qn("w:val"), val); lvl.append(el)
        ppr = OxmlElement("w:pPr"); ind = OxmlElement("w:ind")
        ind.set(qn("w:left"), str(720 * (ilvl + 1))); ind.set(qn("w:hanging"), "420")
        ppr.append(ind); lvl.append(ppr); abstract.append(lvl)
    first_num = numbering.find(qn("w:num"))
    if first_num is None:
        numbering.append(abstract)
    else:
        first_num.addprevious(abstract)
    num = OxmlElement("w:num"); num.set(qn("w:numId"), str(NUM_ID))
    ref = OxmlElement("w:abstractNumId"); ref.set(qn("w:val"), str(ABS_ID)); num.append(ref)
    numbering.append(num)

def bind_heading_styles(doc):
    for ilvl, name in enumerate(["Heading 1", "Heading 2", "Heading 3", "Heading 4"]):
        ppr = doc.styles[name].element.get_or_add_pPr()
        numpr = OxmlElement("w:numPr")
        for tag, val in (("w:ilvl", str(ilvl)), ("w:numId", str(NUM_ID))):
            el = OxmlElement(tag); el.set(qn("w:val"), val); numpr.append(el)
        # numPr 须位于 schema 规定位置：紧跟 keepNext 等元素之后
        ppr.insert_element_before(numpr, "w:pBdr", "w:shd", "w:tabs", "w:spacing",
                                  "w:ind", "w:jc", "w:outlineLvl", "w:rPr", "w:sectPr")
```

执行要点：

1. 默认模板无编号部件时（`doc.part.numbering_part` 报错），先插入任意带编号列表，或换用自带列表样式的模板，再注入。
2. 表格内换行用 `w:br` 或单元格内多个段落实现，与 Markdown 的 `<br>` 一一对应；不要写入字面量转义字符。
3. 测试用例表固定 8 列表头，不合并单元格；表格样式统一设置边框与表头底纹。
4. 写完必须验证编号：在 Word 中点击任意标题序号，序号应与样式绑定；全选复制到钉钉文档，序号仍为可续排列表。验证不通过视为交付失败。
5. `formats` 与绑定层级必须与模板实际标题层级一致：模板中「迭代N功能描述」不编号时，为其单独设置样式（不绑定编号）或调整层级映射；以 Word 实际显示为准。

## 6. 功能框架图渲染为 PNG

输入源：PRD 第 8 节的 Markdown 代码块，层级为版本 → 迭代 → 大功能点 → 子功能（`#`/`##`/`###`/`####`）。

方案一：mermaid-cli 直出 PNG（首选，依赖少、命令最简单）。framework.mmd 使用 `mindmap` 语法，根节点为版本号，逐层缩进写迭代、大功能点、子功能。

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i framework.mmd -o framework.png -b white -w 1920
```

首次运行 mmdc 会下载 Chromium；下载失败时指向本机浏览器（Windows 用 `$env:PUPPETEER_EXECUTABLE_PATH = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"`，macOS 用 `export PUPPETEER_EXECUTABLE_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`），再重跑 mmdc。

方案二：markmap-cli + 无头浏览器截图（保真 mindmap 样式，备选）

```text
npm install -g markmap-cli
markmap framework.md -o framework.html --no-open
# Windows（PowerShell 7）：Edge 无头截图（路径按实际安装位置调整）
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --disable-gpu `
  --hide-scrollbars --window-size=1920,2400 --virtual-time-budget=5000 `
  --screenshot="D:\out\framework.png" "file:///D:/out/framework.html"
# macOS：Chrome 无头截图
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --hide-scrollbars --window-size=1920,2400 --virtual-time-budget=5000 \
  --screenshot=framework.png "file:///tmp/framework.html"
```

截图参数说明：`--window-size` 按节点数量放大，避免截断；`--virtual-time-budget` 给脚本渲染留时间，截图空白时增大到 8000。

降级顺序：mermaid-cli → markmap-cli + 无头截图 → 浏览器打开 framework.html 手动截图 → Word 中手工绘制结构图。最后一级降级必须在交付说明中标注「框架图为手工绘制，已人工核对节点数量」。不论哪种方案，生成后必须核对：大功能点与子功能的数量、命名与「一、7 功能清单」及正文完全一致；发现清单外节点先回问用户，不得擅自增删。

## 7. 测试用例以嵌入 Excel 对象插入 Word

目标：在 Word 对应迭代附件位插入可双击编辑的 Embedded Microsoft Excel Worksheet，保留 8 列表头与排序规则（字段与场景规则见 `references/testcase-spec.md`）。链路：openpyxl 生成 xlsx → Word COM 嵌入；Python 无法直接生成 OLE 对象，只能走 COM 或人工插入。

1. 生成 xlsx（8 列表头固定，序号连续，按关联功能点排序）：

```python
from openpyxl import Workbook
wb = Workbook(); ws = wb.active; ws.title = "迭代1测试用例"
ws.append(["序号", "关联功能点", "用例名称", "场景类型",
           "前置条件", "测试步骤", "预期结果", "优先级"])
ws.append([1, "1.1-2.1", "点击开始作答激活输入框", "正常流程",
           "已进入作答页", "1. 点击【开始作答】按钮", "输入框激活，倒计时启动", "P0"])
wb.save("迭代1测试用例.xlsx")
```

2. 安装并验证 pywin32：`python -m pip install pywin32`，`python -c "import win32com.client"` 无报错。
3. 在 Markdown 附件位写占位文本（如「【插入迭代1测试用例 Excel 对象】」），转换后在 Word 中定位该段落并插入对象：

```python
import os, win32com.client as win32

word = win32.gencache.EnsureDispatch("Word.Application")
word.Visible = False
doc = word.Documents.Open(os.path.abspath("PRD.docx"))
rng = doc.Content
rng.Find.Text = "【插入迭代1测试用例 Excel 对象】"
if not rng.Find.Execute():
    raise RuntimeError("未找到附件位占位文本")
doc.InlineShapes.AddOLEObject(ClassType="Excel.Sheet", FileName=os.path.abspath("迭代1测试用例.xlsx"),
                              LinkToFile=False, DisplayAsIcon=False, Range=rng)
doc.Save(); doc.Close(False); word.Quit()
```

4. 验证嵌入成功：解压检查 `word/embeddings/` 是否含 xlsx、`word/numbering.xml` 是否有编号定义（`python -c "import zipfile; z=zipfile.ZipFile('PRD.docx'); print([n for n in z.namelist() if 'embeddings' in n], 'word/numbering.xml' in z.namelist())"`）；再打开 Word 双击对象，确认可编辑、可筛选。
5. WPS 兼容性：WPS 文字 COM 不支持 `InlineShapes.AddOLEObject`（返回 E_FAIL）。已验证的 WPS 原生做法见 3.2「WPS 文字 + WPS 表格双应用」：WPS 表格复制区域 → WPS 文字 `Selection.PasteSpecial` 粘贴为 OLE 对象，全程无需 Microsoft Office。若以上均不可用，再人工插入：WPS 文字 → 插入 → 对象 → 由文件创建 → 选择 xlsx → 取消勾选「显示为图标」→ 确定。
6. 降级：COM 与人工均不可用时，将 xlsx 作为独立附件交付，Word 附件位写「【测试用例未嵌入：见附件〈文件名〉】」，并在交付说明中明确原因，由用户决定是否接受。
7. 替代方案（半自动，纯 Python）：用 docxtpl 的 `replace_zipname` / `replace_embedded` 替换模板中预置的嵌入 xlsx——先人工制作含占位嵌入对象的模板 .docx，生成时由 Python 替换，生成端无需 COM。优先 `replace_zipname`（Word 保存过的模板对 Excel 类嵌入对象可能出现 CRC 不匹配），`replace_embedded` 作为对象名匹配时的备选。该能力仅对嵌入的 Office 文件有效，使用前须在目标机器小样验证。

## 8. 生成后自动打开

Windows：

```powershell
wps "D:\docs\PRD.docx"                        # WPS 已在 PATH
$root = (Get-ItemProperty "HKCU:\Software\Kingsoft\Office\6.0\common" -ErrorAction SilentlyContinue).InstallRoot
& "$root\office6\wps.exe" "D:\docs\PRD.docx"  # 未在 PATH 时（WPS 12.x 路径结构；$root 为空则改用默认关联）
Start-Process "D:\docs\PRD.docx"              # 按默认关联打开
Start-Process winword "D:\docs\PRD.docx"      # 仅安装 Word 时
```

macOS：

```bash
open -a wpsoffice "~/Desktop/PRD.docx"     # 应用名为 wpsoffice
open -a "WPS Office" "~/Desktop/PRD.docx"  # 名称不匹配时尝试
open "~/Desktop/PRD.docx"                  # 用默认应用打开
```

判定标准：命令返回后任务栏或 Dock 出现 WPS/Word 窗口即视为成功。命令报错但进程已存在（如 `Get-Process wps` 或 `pgrep wpsoffice` 有结果）同样视为已打开，不要重复启动。若本机未安装 WPS，必须告知用户实际用何种应用打开。

## 9. 失败降级策略

| 失败点 | 判断信号 | 降级方案 | 交付说明须标注 |
|---|---|---|---|
| pandoc 不可用或转换失败 | `pandoc --version` 报不存在；转换退出码非 0 | 改走链路 B | 不标注（链路切换不影响质量） |
| 自动多级编号未生效 | 标题序号为手动文本、无序号或无法续排 | 用链路 B 重建，或修正 reference.docx 编号绑定 | 不标注（必须修复，不得降级交付） |
| mermaid-cli 安装失败 | npm 报错或超时 | 改用 markmap-cli + 无头截图，再不行手动截图 | 标注渲染方式 |
| 无头截图为空白 | PNG 尺寸异常或全白 | 增大 `--virtual-time-budget`、放大窗口重试；仍失败改手动截图 | 标注「手工截图」 |
| pywin32 安装失败 | `import win32com.client` 报 ModuleNotFoundError | 执行 `python -m pywin32_postinstall -install`；仍失败改人工插入 | 标注嵌入方式 |
| AddOLEObject 报 COM 异常 | 未安装 Excel 或 Word 版本不兼容 | 安装 Excel 后重试，或用 WPS 人工插入 | 标注「人工嵌入，需复核双击」 |
| WPS 未安装 | `Get-Command wps` 与安装路径均不存在 | 用 Word 或默认关联打开 | 标注实际打开方式 |
| 路径含中文或空格导致失败 | 找不到文件、COM 报错 | 使用绝对路径并整体加引号；必要时复制到无空格临时目录 | 标注处理方式 |
| 目标目录无写权限 | 保存报拒绝访问 | 换到桌面或用户文档目录再交付 | 标注最终路径 |

降级原则：格式类要求（自动编号、框架图转图片、用例嵌入对象）属于强制项，不得以降级方式交付；只有工具链缺失且用户明确接受时，才可用降级方案并在交付说明中逐条标注。

## 10. 交付验证清单

- [ ] .docx 可正常打开，无损坏提示，页数与文件大小合理
- [ ] 标题序号为自动多级编号，点击序号选中整段；全选复制到钉钉文档后序号仍可续排
- [ ] 表格列数与 Markdown 一致，单元格内换行正常，无断列
- [ ] 功能框架图为 PNG 图片而非代码块，大功能点/子功能数量与功能清单一致
- [ ] 测试用例为嵌入 Excel 对象，双击可编辑、可筛选，8 列表头与排序规则正确
- [ ] 未生成用例时附件位为「【测试用例待生成：demo 定型后统一生成】」，非空白
- [ ] 本次有改动或新增的功能条目，其「更新时间」与改动时间一致（增量更新时不要批量刷新未改动条目）
- [ ] 文档已用 WPS（或 Word）打开，窗口可见
- [ ] 中间产物（.md、.png、.xlsx）路径已记录，可随交付一并提供
- [ ] 遗留【待确认】项与所有降级项已写入交付说明

## 11. 交付说明话术模板

```
已完成《〈产品/模块名称〉》PRD 交付，文件如下：
1. Word：〈绝对路径〉（已用 WPS 打开）
2. 功能框架图：〈png 绝对路径〉，已插入「一、8 功能框架图」位置
3. 测试用例：〈xlsx 绝对路径〉，已作为嵌入 Excel 对象插入「迭代1」附件位（未生成时为待生成标注）

已执行质量门禁自查：章节完整、自动多级编号、功能清单与正文一致、框架图节点数量一致。
遗留待确认：〈逐条列出；无则写「无」〉
降级说明：〈逐条列出；无则写「无」〉

如需调整，请使用增量更新指令，例如「仅更新 1.2 子功能的限制条件，其他保持不变」。
```
