from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = Workbook()
ws = wb.active
ws.title = "报价单"

# --- Styles ---
title_font = Font(name="Arial", size=18, bold=True, color="1F4E79")
header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
body_font = Font(name="Arial", size=10)
total_font = Font(name="Arial", size=11, bold=True, color="1F2937")
note_font = Font(name="Arial", size=9, italic=True, color="6B7280")

header_fill = PatternFill("solid", fgColor="1F4E79")
zebra_1 = PatternFill("solid", fgColor="FFFFFF")
zebra_2 = PatternFill("solid", fgColor="F2F7FB")
total_fill = PatternFill("solid", fgColor="EAF2FF")
title_fill = PatternFill("solid", fgColor="D6E4F0")

thin_border = Border(
    left=Side(style="thin", color="D9DEE7"),
    right=Side(style="thin", color="D9DEE7"),
    top=Side(style="thin", color="D9DEE7"),
    bottom=Side(style="thin", color="D9DEE7"),
)
top_emphasis = Border(
    left=Side(style="thin", color="D9DEE7"),
    right=Side(style="thin", color="D9DEE7"),
    top=Side(style="medium", color="1F4E79"),
    bottom=Side(style="thin", color="D9DEE7"),
)

center = Alignment(horizontal="center", vertical="center", wrap_text=True)
left = Alignment(horizontal="left", vertical="center", wrap_text=True)
right = Alignment(horizontal="right", vertical="center")

# --- Title Section ---
ws.merge_cells("A1:G1")
ws["A1"] = "OA 系统项目报价单"
ws["A1"].font = title_font
ws["A1"].alignment = center
ws["A1"].fill = title_fill
ws.row_dimensions[1].height = 40

ws.merge_cells("A2:G2")
ws["A2"] = "项目名称：OA 办公自动化系统部署与集成"
ws["A2"].font = Font(name="Arial", size=11, bold=True, color="374151")
ws["A2"].alignment = Alignment(horizontal="left", vertical="center")
ws.row_dimensions[2].height = 25

ws.merge_cells("A3:G3")
ws["A3"] = "报价日期：2026年11月19日"
ws["A3"].font = Font(name="Arial", size=10, color="6B7280")
ws["A3"].alignment = Alignment(horizontal="left", vertical="center")
ws.row_dimensions[3].height = 22

# --- Headers ---
headers = ["序号", "项目名称", "规格 / 说明", "数量", "单位", "单价（元）", "小计（元）"]
for col_idx, h in enumerate(headers, 1):
    cell = ws.cell(row=5, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = center
    cell.border = thin_border

ws.row_dimensions[5].height = 30

# --- Data Rows ---
items = [
    (1, "服务器", "项目专用服务器", 2, "台", 6000),
    (2, "OA 系统部署实施", "OA 系统安装、配置与初始化", 5, "套", 4000),
    (3, "用户登录集成代码修改", "统一身份认证 / SSO 集成开发", 1, "项", 8000),
    (4, "流程运行集成代码修改", "业务流程引擎对接与定制开发", 1, "项", 8000),
    (5, "年度技术维护服务", "自验收合格之日起 1 年", 1, "年", 7000),
]

start_row = 6
for i, (seq, name, desc, qty, unit, price) in enumerate(items):
    r = start_row + i
    fill = zebra_1 if i % 2 == 0 else zebra_2

    ws.cell(row=r, column=1, value=seq).alignment = center
    ws.cell(row=r, column=2, value=name).alignment = left
    ws.cell(row=r, column=3, value=desc).alignment = left
    ws.cell(row=r, column=4, value=qty).alignment = center
    ws.cell(row=r, column=5, value=unit).alignment = center
    ws.cell(row=r, column=6, value=price).alignment = right

    # 小计公式：数量 × 单价
    ws.cell(row=r, column=7, value=f"=D{r}*F{r}").alignment = right

    for c in range(1, 8):
        cell = ws.cell(row=r, column=c)
        cell.font = body_font
        cell.fill = fill
        cell.border = thin_border

    ws.row_dimensions[r].height = 28

# --- Total Row ---
total_row = start_row + len(items)

ws.merge_cells(f"A{total_row}:E{total_row}")
ws.cell(row=total_row, column=1, value="合  计").alignment = center
ws.cell(row=total_row, column=6, value="").alignment = right
ws.cell(row=total_row, column=7, value=f"=SUM(G{start_row}:G{total_row-1})").alignment = right

for c in range(1, 8):
    cell = ws.cell(row=total_row, column=c)
    cell.font = total_font
    cell.fill = total_fill
    cell.border = top_emphasis

ws.row_dimensions[total_row].height = 32

# --- Footer Notes ---
note_row = total_row + 2
ws.merge_cells(f"A{note_row}:G{note_row}")
ws.cell(row=note_row, column=1, value="备注：本报价有效期 30 天，最终以双方签订合同为准。以上报价含税。")
ws.cell(row=note_row, column=1).font = note_font

# --- Column Widths ---
widths = [6, 26, 38, 8, 8, 16, 16]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(i)].width = w

# --- Number Formatting ---
for r in range(start_row, total_row + 1):
    ws.cell(row=r, column=6).number_format = "#,##0"
    ws.cell(row=r, column=7).number_format = "#,##0"

wb.save("/workspace/OA系统报价单.xlsx")
print("报价单已生成")
