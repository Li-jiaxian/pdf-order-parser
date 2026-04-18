# E_Print PDF 解析服务

这是一个轻量级的 Flask 服务，用于解析订单 PDF 文件并自动填充表单。

## 功能

- 接收上传的 PDF 订单文件
- 使用 PyMuPDF 提取文本内容
- 基于正则表达式解析订单字段
- 返回符合前端 IOrder 接口的 JSON 数据

## 安装依赖

```bash
cd backend
pip3 install -r requirements.txt
```

## 启动服务

### 方式 1：使用启动脚本

```bash
cd backend
./start_service.sh
```

### 方式 2：直接运行

```bash
cd backend
python3 pdf_parser_service.py
```

服务将在 `http://localhost:8000` 启动。

## API 端点

### 1. 解析 PDF

**端点：** `POST /api/order/parse-pdf`

**请求：**
- Content-Type: `multipart/form-data`
- Body: `file` 字段包含 PDF 文件

**响应：**
```json
{
  "customer": "客户名称",
  "order_id": "订单号",
  "productName": "产品名称",
  "dingDanShuLiang": 5000,
  "guigeGaoMm": 210,
  "guigeKuanMm": 297,
  "chanPinMingXi": [
    {
      "neiWen": "封面",
      "keZhong": 250,
      "yeShu": 4
    }
  ]
}
```

### 2. 健康检查

**端点：** `GET /api/health`

**响应：**
```json
{
  "status": "ok",
  "service": "PDF Parser Service"
}
```

## 前端集成

前端已配置 Vite 代理，所有 `/api` 请求会自动转发到 `http://localhost:8000`。

在 `OrderInfo.vue` 中使用：

```typescript
const response = await fetch('/api/order/parse-pdf', {
  method: 'POST',
  body: formData,
})
```

## 使用流程

1. **启动 Python 服务：**
   ```bash
   cd backend
   ./start_service.sh
   ```

2. **启动前端开发服务器：**
   ```bash
   npm run dev
   ```

3. **测试解析功能：**
   - 打开浏览器访问 `http://localhost:5173`
   - 进入订单创建页面
   - 上传 PDF 文件
   - 点击"AI解析并填充表格"按钮

## 目录结构

```
backend/
├── pdf_parser_service.py   # Flask 服务主文件
├── order_parser.py          # 订单解析逻辑
├── requirements.txt         # Python 依赖
├── start_service.sh         # 启动脚本
├── temp/                    # 临时文件目录（自动创建）
└── README.md                # 本文件
```

## 注意事项

- 服务需要在前端启动前运行
- 临时上传的 PDF 文件会在解析后自动删除
- 最大文件大小限制为 16MB
- 只支持 PDF 格式文件
- 基于规则的解析适合格式固定的订单 PDF

## 调试

服务运行时会在控制台输出详细日志：

```
[INFO] 收到文件: 案例_订单.pdf
[INFO] 成功提取文本，长度: 1234 字符
[INFO] 成功解析订单数据，字段数: 50
[INFO] 已删除临时文件: 案例_订单.pdf
```

## 自定义解析规则

如果需要调整解析规则，编辑 `order_parser.py` 中的正则表达式：

```python
order_data['customer'] = extract_field(text, r'客户[:：]\s*(.+?)(?:\n|$)')
```

## 升级建议

如果需要更智能的解析，可以考虑：

1. 集成 OpenAI GPT-4 或 Claude API
2. 使用 OCR 处理扫描版 PDF
3. 添加机器学习模型进行字段识别
