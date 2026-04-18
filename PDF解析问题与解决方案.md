# PDF 订单解析问题与解决方案总结

## 概述

本文档记录了 E_Print PDF 订单解析功能开发过程中遇到的所有问题及其解决方案。该功能使用 PyMuPDF (fitz) 库从 PDF 订单文件中提取表格数据，并自动填充到 Vue 前端表单中。

**核心技术栈：**
- 后端：Flask + PyMuPDF
- 前端：Vue 3 + TypeScript
- 解析方式：表格结构化提取

---

## 问题时间线

### 问题 1：产品明细表格显示空行

**时间：** 初期

**问题描述：**
前端产品明细表格显示空行，所有字段都未填充。用户上传 PDF 后，虽然其他字段（如客户、订单号）能正确填充，但产品明细部分完全为空。

**问题原因：**
最初使用文本提取方式（`extract_text_from_pdf()`），无法正确处理 PDF 中的多行表格格式。表格的表头和数据行在文本中是分离的，导致解析逻辑无法正确匹配字段和值。

**关键设计思路：**
参考前端 TypeScript 接口定义来指导解析结构。特别是 `IProductDetail` 接口定义了产品明细的 14 个字段：

```typescript
// /Users/markov_lee/Code/E_Print/src/types/Order.ts
interface IProductDetail {
  neiWen: string           // 内文
  yongZhiChiCun: string    // 报价用纸尺寸
  houDu: number            // 厚度
  keZhong: number          // 克重
  chanDi: string           // 产地
  pinPai: string           // 品牌
  zhiLei: string           // 纸类
  FSC: string              // FSC
  yeShu: number            // 页数
  yinSe: string            // 印色
  zhuanSe: string          // 专色
  biaoMianChuLi: string    // 表面处理
  zhuangDingGongYi: string // 装订工艺
  beiZhu: string           // 备注
}
```

这个接口定义明确了需要提取的字段结构，使得解析逻辑能够与前端数据结构完全匹配。

**解决方案：**
切换到 PyMuPDF 的结构化表格提取 API：
```python
tables = page.find_tables()
for table in tables.tables:
    table_data = table.extract()  # 返回二维数组
```

创建新文件 `table_parser.py` 替代原有的 `order_parser.py`，使用表格结构化数据进行解析。在 `parse_product_details()` 函数中，严格按照 `IProductDetail` 接口的 14 个字段进行数据提取和映射。

**相关文件：**
- `/Users/markov_lee/Code/E_Print/backend/table_parser.py` (新建)
- `/Users/markov_lee/Code/E_Print/backend/pdf_parser_service.py` (修改导入)
- `/Users/markov_lee/Code/E_Print/src/types/Order.ts` (参考接口定义)

---

### 问题 2：多个字段未填充（订单数量、出样数量、日期等）

**时间：** 表格提取实现后

**问题描述：**
切换到表格提取后，产品明细有数据了，但很多基础字段仍然为空或显示 0：
- 订单数量 (dingDanShuLiang)
- 出样数量 (chuYangShuLiang)
- 各种日期字段

**问题原因：**
PDF 表格中存在大量合并单元格，在提取的二维数组中表现为 `None` 值。代码使用硬编码的列索引（如 `col_idx + 1`）来获取字段值，但如果该位置是 `None`，就会提取失败。

**调试输出示例：**
```python
row = ['订单数量', None, '30000', None, '出样数量', None, '1', ...]
# 如果直接用 row[col_idx + 1]，当 col_idx=0 时会得到 None 而不是 '30000'
```

**解决方案：**
实现 `get_next_value()` 辅助函数，动态跳过 `None` 单元格：
```python
def get_next_value(start_col):
    """从 start_col 开始查找下一个非 None 且非空的值"""
    for i in range(start_col, len(row)):
        if row[i] is not None and row[i].strip():
            return clean_text(row[i])
    return ''
```

在所有字段提取处使用该函数：
```python
elif field_name == '订单数量':
    order_data['dingDanShuLiang'] = safe_number(get_next_value(col_idx + 1))
```

**相关文件：**
- `/Users/markov_lee/Code/E_Print/backend/table_parser.py`

---

### 问题 3：日期填充到错误的列

**时间：** 字段提取修复后

**问题描述：**
日期字段混乱，"CPC承诺日期"的值被填充到"要求日期"字段中。例如：
- PDF 中 CPC承诺日期列显示 `2025-11-24`
- 但前端的 `chuHuoRiqiRequired`（要求日期）显示了这个值
- 而 `chuHuoRiqiPromise`（承诺日期）反而是空的

**问题原因：**
代码按顺序提取日期（第一个日期作为 Required，第二个作为 Promise），但没有考虑表格的实际列结构。PDF 表格有固定的列：
- 第 20 列：要求日期
- 第 22 列：CPC承诺日期

如果某行的要求日期为空，只有承诺日期有值，按顺序提取就会出错。

**调试输出示例：**
```python
row = ['出货', '30000', None, '', None, '2025-11-24', None]
dates = ['2025-11-24']  # 只找到一个日期，但它在承诺日期列
```

**解决方案：**
1. 先遍历表格找到"要求日期"和"CPC承诺日期"的列索引：
```python
required_date_col = None
promise_date_col = None

for row in table_data:
    for col_idx, cell in enumerate(row):
        if cell:
            if '要求日期' in cell:
                required_date_col = col_idx
            elif 'CPC承诺日期' in cell or 'CPC承诺' in cell:
                promise_date_col = col_idx
```

2. 实现按列索引提取日期的函数：
```python
def get_date_by_column(col_index):
    """从指定列索引提取日期"""
    if col_index is not None and col_index < len(row):
        val = row[col_index]
        if val and '-' in str(val) and len(str(val)) >= 8:
            return clean_text(val)
    return ''
```

3. 使用列索引提取日期：
```python
elif field_name == '出货':
    order_data['chuHuoShuLiang'] = safe_number(get_next_value(col_idx + 1))
    order_data['chuHuoRiqiRequired'] = get_date_by_column(required_date_col)
    order_data['chuHuoRiqiPromise'] = get_date_by_column(promise_date_col)
```

**相关文件：**
- `/Users/markov_lee/Code/E_Print/backend/table_parser.py`

---

### 问题 4：小数点丢失

**时间：** 日期问题修复后

**问题描述：**
带小数的数字在填充时丢失了小数点。例如：
- PDF 中显示 `88.9`
- 前端显示 `889`

**问题原因：**
使用 `safe_int()` 函数转换数字，该函数移除了所有非数字字符，包括小数点：
```python
def safe_int(value: str) -> int:
    cleaned = ''.join(c for c in str(value) if c.isdigit())
    # 小数点被移除了！
```

**解决方案：**
创建新的 `safe_number()` 函数，保留小数点并转换为 `float`：
```python
def safe_number(value: str) -> float:
    """安全转换为数字（保留小数）"""
    if not value:
        return 0
    try:
        cleaned = ''.join(c for c in str(value) if c.isdigit() or c == '.' or c == '-')
        if cleaned:
            return float(cleaned)
        return 0
    except (ValueError, AttributeError):
        return 0
```

将所有数字字段的提取从 `safe_int()` 改为 `safe_number()`：
```python
order_data['guigeKuanMm'] = safe_number(get_next_value(col_idx + 1))  # 88.9 保持为 88.9
order_data['keZhong'] = safe_number(row[col_idx])  # 115.5 保持为 115.5
```

**相关文件：**
- `/Users/markov_lee/Code/E_Print/backend/table_parser.py`

---

### 问题 5：不同 PDF 的产品明细解析失败

**时间：** 最近

**问题描述：**
某个新的 PDF 文件（绿女巫塔罗牌）的产品明细无法正确解析，但之前的 PDF（案例_订单.pdf）可以正常工作。

**调试输出：**
```python
# 表头行
row = ['内文', '报价用纸尺寸', None, None, '厚度', None, '克重', None, '产地', '品牌', ...]

# 代码期望的列索引：
# 列3: 厚度
# 列5: 克重
# 列7: 产地

# 实际的列索引：
# 列4: 厚度  ❌
# 列6: 克重  ❌
# 列8: 产地  ❌
```

**问题原因：**
`parse_product_details()` 函数使用硬编码的列索引来提取产品明细字段：
```python
detail = {
    'houDu': safe_number(row[3]) if len(row) > 3 else 0,  # 假设厚度在第3列
    'keZhong': safe_number(row[5]) if len(row) > 5 else 0,  # 假设克重在第5列
    # ...
}
```

但不同 PDF 的表格结构可能不同，合并单元格的位置不同，导致列索引不匹配。

**解决方案：**
动态从表头行查找每个字段的列索引：

1. 定义字段映射：
```python
field_mappings = {
    '内文': 'neiWen',
    '报价用纸尺寸': 'yongZhiChiCun',
    '厚度': 'houDu',
    '克重': 'keZhong',
    '产地': 'chanDi',
    # ...
}
```

2. 遍历表头行，建立列索引映射：
```python
col_map = {}
for col_idx, cell in enumerate(header_row):
    if not cell:
        continue
    cell_text = clean_text(cell)
    for key, field_name in field_mappings.items():
        if key in cell_text:
            col_map[field_name] = col_idx
            break
```

3. 使用动态列索引提取数据：
```python
detail = {
    'houDu': safe_number(row[col_map.get('houDu', 4)]) if col_map.get('houDu', 4) < len(row) else 0,
    'keZhong': safe_number(row[col_map.get('keZhong', 6)]) if col_map.get('keZhong', 6) < len(row) else 0,
    # ...
}
```

这样无论表格结构如何变化，都能正确找到对应的列。

**相关文件：**
- `/Users/markov_lee/Code/E_Print/backend/table_parser.py` - `parse_product_details()` 函数

---

## 核心经验总结

### 1. 表格提取优于文本提取
对于结构化的 PDF 表格，使用 `page.find_tables()` 比文本提取更可靠。

### 2. 避免硬编码列索引
PDF 表格结构可能因合并单元格而变化，应该动态查找列索引而非使用固定位置。

### 3. 处理合并单元格
提取的表格数据中，合并单元格表现为 `None`，需要实现跳过逻辑。

### 4. 按列索引提取而非按顺序
对于有明确列结构的数据（如日期列），应该先找到列索引，再按索引提取，而不是按出现顺序。

### 5. 保留数据精度
数字转换时要考虑小数，使用 `float` 而非 `int`。

---

## 相关文件清单

| 文件路径 | 说明 |
|---------|------|
| `/Users/markov_lee/Code/E_Print/backend/table_parser.py` | 核心解析逻辑，包含所有问题的解决方案 |
| `/Users/markov_lee/Code/E_Print/backend/pdf_parser_service.py` | Flask 服务入口 |
| `/Users/markov_lee/Code/E_Print/src/types/Order.ts` | TypeScript 接口定义，指导解析结构 |

---

**文档创建时间：** 2026-04-19  
**最后更新：** 2026-04-19
