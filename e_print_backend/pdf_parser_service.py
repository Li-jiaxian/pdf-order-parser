"""
Flask PDF 解析服务
提供 /api/order/parse-pdf 接口，接收 PDF 文件并返回解析后的订单数据
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

# 添加 InStruct 目录到 Python 路径，以便导入 extract_pdf
sys.path.insert(0, '/Users/markov_lee/Code/InStruct')

# 导入本地解析模块
from table_parser import parse_order_from_pdf

# 配置日志
LOG_DIR = Path(__file__).parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# 创建日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"api_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8'),
        logging.StreamHandler()  # 同时输出到控制台
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# 配置 CORS，允许来自 Vite 开发服务器的请求
CORS(app, origins=['http://localhost:5173'])

# 配置上传文件夹
UPLOAD_FOLDER = Path(__file__).parent / 'temp'
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制 16MB


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/order/parse-pdf', methods=['POST'])
def parse_pdf():
    """
    解析上传的 PDF 订单文件

    接收: FormData 包含 'file' 字段
    返回: JSON 格式的订单数据
    """
    logger.info("========== 新的解析请求 ==========")

    try:
        # 检查是否有文件
        if 'file' not in request.files:
            logger.error("请求中没有文件")
            return jsonify({'error': '没有上传文件'}), 400

        file = request.files['file']

        # 检查文件名
        if file.filename == '':
            logger.error("文件名为空")
            return jsonify({'error': '文件名为空'}), 400

        if not allowed_file(file.filename):
            logger.error(f"不支持的文件类型: {file.filename}")
            return jsonify({'error': '只支持 PDF 文件'}), 400

        # 保存文件到临时目录
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        logger.info(f"收到文件: {filename}")

        # 使用表格提取方式解析订单数据
        try:
            order_data = parse_order_from_pdf(filepath)
            logger.info(f"✓ 成功解析订单数据，字段数: {len(order_data)}")

            # 记录解析结果（只记录非空字段）
            non_empty_fields = {k: v for k, v in order_data.items() if v and v != 0 and v != '' and v != []}
            logger.info(f"解析结果（非空字段）: {non_empty_fields}")

        except Exception as e:
            logger.error(f"订单数据解析失败: {e}", exc_info=True)
            return jsonify({'error': f'订单数据解析失败: {str(e)}'}), 500

        # 清理临时文件
        try:
            os.remove(filepath)
            logger.info(f"✓ 已删除临时文件: {filename}")
        except Exception as e:
            logger.warning(f"删除临时文件失败: {e}")

        # 返回解析结果
        logger.info("========== 解析成功 ==========\n")
        return jsonify(order_data), 200

    except Exception as e:
        logger.error(f"服务器错误: {e}", exc_info=True)
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'service': 'PDF Parser Service'}), 200


@app.route('/', methods=['GET'])
def index():
    """根路径"""
    return jsonify({
        'service': 'E_Print PDF Parser Service',
        'version': '1.0.0',
        'endpoints': {
            'parse': 'POST /api/order/parse-pdf',
            'health': 'GET /api/health'
        }
    }), 200


if __name__ == '__main__':
    logger.info('=' * 60)
    logger.info('E_Print PDF 解析服务启动中...')
    logger.info('=' * 60)
    logger.info(f'上传目录: {UPLOAD_FOLDER}')
    logger.info(f'日志目录: {LOG_DIR}')
    logger.info(f'允许的文件类型: {ALLOWED_EXTENSIONS}')
    logger.info(f'最大文件大小: {app.config["MAX_CONTENT_LENGTH"] / 1024 / 1024} MB')
    logger.info('=' * 60)
    logger.info('服务运行在: http://localhost:8000')
    logger.info('API 端点: http://localhost:8000/api/order/parse-pdf')
    logger.info('=' * 60)

    app.run(host='0.0.0.0', port=8000, debug=True)
