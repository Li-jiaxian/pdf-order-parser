# PDF Order Parser

基于 PyMuPDF 的 PDF 订单表格解析工具，用于从 PDF 订单文件中自动提取结构化数据。

## 📋 项目简介

本项目为 E_Print 订单管理系统提供 PDF 解析服务，能够：
- 从 PDF 订单文件中提取表格数据
- 自动识别并填充 50+ 个订单字段
- 支持产品明细表格的结构化提取（14 个字段）
- 处理合并单元格和复杂表格结构
- 区分"要求日期"和"CPC承诺日期"等多列数据

## 🏗️ 项目结构

```
pdf-order-parser/
├── e_print_backend/          # E_Print 后端服务
│   ├── pdf_parser_service.py # Flask API 服务
│   ├── table_parser.py        # 核心解析逻辑（表格提取）
│   ├── order_parser.py        # 旧版解析逻辑（文本提取）
│   ├── requirements.txt       # Python 依赖
│   ├── start_service.sh       # 启动脚本
│   └── logs/                  # 日志目录
├── extract_pdf.py             # PDF 文本提取工具
├── docs/                      # 示例 PDF 文档
└── PDF解析问题与解决方案.md  # 技术文档
```

## 🚀 快速开始

### 环境要求

- Python >= 3.8
- PyMuPDF (fitz) >= 1.23.0
- Flask >= 3.0.0
- Flask-CORS >= 4.0.0

### 安装依赖

```bash
cd e_print_backend
pip install -r requirements.txt
```

### 启动服务

```bash
# 方式 1：使用启动脚本
./start_service.sh

# 方式 2：直接运行
python3 pdf_parser_service.py
```

服务将运行在 `http://localhost:8000`

### API 使用

**端点：** `POST /api/order/parse-pdf`

**请求：** 
- Content-Type: `multipart/form-data`
- 字段名: `file`
- 文件类型: PDF

**响应：**
```json
{
  "customer": "当纳利亚洲印务有限公司",
  "order_id": "25025769",
  "productName": "绿女巫塔罗牌",
  "dingDanShuLiang": 30000,
  "guigeGaoMm": 127,
  "guigeKuanMm": 88.9,
  "chanPinMingXi": [
    {
      "neiWen": "封面",
      "keZhong": 300,
      "yeShu": 4,
      ...
    }
  ],
  ...
}
```

## 🔧 核心技术

### 表格提取

使用 PyMuPDF 的 `page.find_tables()` API 进行结构化表格提取：

```python
tables = page.find_tables()
for table in tables.tables:
    table_data = table.extract()  # 返回二维数组
```

### 动态列索引

不使用硬编码列位置，而是动态查找字段列索引：

```python
# 查找"要求日期"和"CPC承诺日期"的列索引
for row in table_data:
    for col_idx, cell in enumerate(row):
        if '要求日期' in cell:
            required_date_col = col_idx
        elif 'CPC承诺日期' in cell:
            promise_date_col = col_idx
```

### 合并单元格处理

实现 `get_next_value()` 函数跳过 None 值（合并单元格）：

```python
def get_next_value(start_col):
    """从 start_col 开始查找下一个非 None 且非空的值"""
    for i in range(start_col, len(row)):
        if row[i] is not None and row[i].strip():
            return clean_text(row[i])
    return ''
```

### 数字精度保留

使用 `float` 而非 `int` 保留小数：

```python
def safe_number(value: str) -> float:
    """安全转换为数字（保留小数）"""
    cleaned = ''.join(c for c in str(value) if c.isdigit() or c == '.' or c == '-')
    return float(cleaned) if cleaned else 0
```

## 📚 技术文档

详细的问题解决过程和技术决策请参考：
- [PDF解析问题与解决方案.md](./PDF解析问题与解决方案.md)

该文档记录了开发过程中遇到的 5 个主要问题及其解决方案：
1. 产品明细表格显示空行
2. 多个字段未填充
3. 日期填充到错误的列
4. 小数点丢失
5. 不同 PDF 的产品明细解析失败

## 🎯 设计理念

### 参考 TypeScript 接口定义

解析逻辑参考前端 TypeScript 接口定义（`IOrder` 和 `IProductDetail`），确保提取的数据结构与前端完全匹配。

### 动态而非硬编码

避免硬编码列索引，通过表头动态查找字段位置，适应不同 PDF 的表格结构变化。

### 结构化优于文本

使用表格提取而非文本提取，保留 PDF 的结构信息，提高解析准确性。

## 📝 示例文档

`docs/` 目录包含多个测试用 PDF 文档：
- 绿女巫塔罗牌订单
- 产品包装指示
- 成品指示卡
- 工程单

## 🔗 相关项目

本项目为 [E_Print](https://github.com/Li-jiaxian/E_Print) 订单管理系统的后端解析服务。

## 📄 License

MIT

## 👤 Author

Li-jiaxian

---

**创建时间：** 2026-04-19  
**最后更新：** 2026-04-19
