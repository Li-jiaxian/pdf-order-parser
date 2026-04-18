from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from pathlib import Path
from extract_pdf import extract_text_from_pdf, is_text_pdf
import json
import logging
from datetime import datetime

# 配置日志
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# 创建日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"api_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8'),
        logging.StreamHandler()  # 同时输出到控制台
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI()

# 配置 CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vue 开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/order/parse-pdf")
async def parse_order_pdf(file: UploadFile = File(...)):
    """
    接收 PDF 文件，提取文本，使用 AI 解析订单信息
    """
    logger.info(f"========== 新的解析请求 ==========")
    logger.info(f"收到文件: {file.filename}")

    # 1. 验证文件类型
    if not file.filename.endswith('.pdf'):
        logger.error(f"文件类型错误: {file.filename}")
        raise HTTPException(status_code=400, detail="只支持 PDF 文件")

    try:
        # 2. 保存临时文件
        logger.info("正在保存临时文件...")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        logger.info(f"临时文件路径: {tmp_path}")

        # 3. 检查是否为文本型 PDF
        logger.info("检查 PDF 类型...")
        if not is_text_pdf(tmp_path):
            logger.error("该 PDF 不是文本型 PDF")
            os.unlink(tmp_path)
            raise HTTPException(status_code=400, detail="该 PDF 不是文本型 PDF，无法提取")
        logger.info("✓ PDF 类型检查通过")

        # 4. 提取 PDF 文本
        logger.info("开始提取 PDF 文本...")
        pdf_text = extract_text_from_pdf(tmp_path)
        logger.info(f"✓ 提取完成，文本长度: {len(pdf_text)} 字符")

        # 保存提取的文本到日志文件
        text_log_path = log_dir / f"extracted_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        text_log_path.write_text(pdf_text, encoding='utf-8')
        logger.info(f"✓ 提取的文本已保存到: {text_log_path}")

        # 5. 使用 AI 解析文本，提取订单字段
        logger.info("开始 AI 解析...")
        order_data = parse_order_with_ai(pdf_text)
        logger.info(f"✓ AI 解析完成，提取字段数: {len(order_data)}")
        logger.info(f"解析结果: {json.dumps(order_data, ensure_ascii=False, indent=2)}")

        # 6. 清理临时文件
        os.unlink(tmp_path)
        logger.info("✓ 临时文件已清理")

        # 7. 返回结构化数据
        logger.info("========== 解析成功 ==========\n")
        return order_data

    except Exception as e:
        logger.error(f"解析失败: {str(e)}", exc_info=True)
        # 清理临时文件
        if 'tmp_path' in locals():
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


def parse_order_with_ai(pdf_text: str) -> dict:
    """
    使用 AI（如 Claude API）从 PDF 文本中提取订单字段

    这里需要调用 LLM API，给它 PDF 文本和字段定义，让它返回结构化 JSON
    """
    logger.info("进入 parse_order_with_ai 函数")
    logger.info(f"输入文本长度: {len(pdf_text)} 字符")

    # TODO: 这里是你需要实现的核心逻辑
    # 可以使用 Claude API、OpenAI API 等

    # 示例：构造 prompt
    prompt = f"""
你是一个订单信息提取助手。请从以下 PDF 文本中提取订单信息，返回 JSON 格式。

PDF 文本内容：
{pdf_text}

请提取以下字段（如果文本中没有，则不返回该字段）：
- customer: 客户名称
- productName: 成品名称
- order_id: 订单号
- isbn: ISBN
- dingDanShuLiang: 订单数量（数字）
- guigeGaoMm: 规格高度（数字，单位MM）
- guigeKuanMm: 规格宽度（数字，单位MM）
- zhuangDingFangShi: 装订方式
- fscType: FSC类型
- chanPinMingXi: 产品明细数组

只返回 JSON，不要其他解释。
"""

    logger.info("Prompt 已构造")
    logger.debug(f"Prompt 内容:\n{prompt}")

    # 调用 AI API（这里需要你实现）
    # response = call_claude_api(prompt)
    # order_data = json.loads(response)

    # 临时返回示例数据（实际使用时替换为 AI 调用）
    logger.info("使用示例数据（TODO: 替换为真实 AI 调用）")
    order_data = {
        "customer": "当纳利亚洲印务有限公司",
        "productName": "从PDF中提取的产品名称",
        "order_id": "25025769",
        "dingDanShuLiang": 30000,
    }

    logger.info(f"返回数据: {order_data}")
    return order_data


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
