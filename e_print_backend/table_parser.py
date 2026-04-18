"""
使用 PyMuPDF 表格提取功能解析订单 PDF
"""
import fitz
from typing import Dict, Any, List


def parse_order_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    从 PDF 文件中提取订单信息（使用表格提取）

    Args:
        pdf_path: PDF 文件路径

    Returns:
        符合 IOrder 接口的字典数据
    """
    doc = fitz.open(pdf_path)
    order_data = {}

    # 遍历所有页面
    for page_num in range(len(doc)):
        page = doc[page_num]
        tables = page.find_tables()

        if not tables.tables:
            continue

        for table in tables.tables:
            table_data = table.extract()
            
            # 解析表格数据
            parse_table_data(table_data, order_data)

    doc.close()
    return order_data


def parse_table_data(table_data: List[List[str]], order_data: Dict[str, Any]):
    """
    从表格数据中提取订单字段

    策略：遍历表格的每个单元格，根据字段名动态查找对应的值
    跳过 None（合并单元格），查找下一个非空值

    Args:
        table_data: 表格数据（二维数组）
        order_data: 订单数据字典（会被修改）
    """
    # 首先找到"要求日期"和"CPC承诺日期"的列索引
    required_date_col = None
    promise_date_col = None

    for row in table_data:
        for col_idx, cell in enumerate(row):
            if cell:
                if '要求日期' in cell:
                    required_date_col = col_idx
                elif 'CPC承诺日期' in cell or 'CPC承诺' in cell:
                    promise_date_col = col_idx
        if required_date_col is not None and promise_date_col is not None:
            break

    # 遍历表格的每一行
    for row_idx, row in enumerate(table_data):
        # import ipdb;ipdb.set_trace()
        if not row:
            continue

        # 遍历这一行的每个单元格，查找字段名
        for col_idx, cell in enumerate(row):
            if not cell:
                continue

            field_name = clean_text(cell)

            # 辅助函数：查找下一个非空单元格的值
            def get_next_value(start_col):
                """从 start_col 开始查找下一个非 None 且非空的值"""
                for i in range(start_col, len(row)):
                    if row[i] is not None and row[i].strip():
                        return clean_text(row[i])
                return ''

            # 辅助函数：根据列索引提取日期
            def get_date_by_column(col_index):
                """从指定列索引提取日期"""
                if col_index is not None and col_index < len(row):
                    val = row[col_index]
                    if val and '-' in str(val) and len(str(val)) >= 8:
                        return clean_text(val)
                return ''

            # 根据字段名提取对应的值
            if field_name == '客户':
                order_data['customer'] = get_next_value(col_idx + 1)

            elif field_name == '成品名称':
                order_data['productName'] = get_next_value(col_idx + 1)

            elif field_name == '订单号':
                order_data['order_id'] = get_next_value(col_idx + 1)

            elif field_name == '旧编码':
                order_data['jiuBianMa'] = get_next_value(col_idx + 1)

            elif field_name == 'ISBN':
                order_data['isbn'] = get_next_value(col_idx + 1)

            elif field_name == '客户PO':
                order_data['customerPO'] = get_next_value(col_idx + 1)

            elif field_name == '报价单号':
                order_data['baoJiaDanHao'] = get_next_value(col_idx + 1)

            elif field_name == '系列单名':
                order_data['xiLieDanMing'] = get_next_value(col_idx + 1)

            elif field_name == '其他识别':
                order_data['qiTaShiBie'] = get_next_value(col_idx + 1)

            elif field_name == '产品大类':
                order_data['chanPinDaLei'] = get_next_value(col_idx + 1)

            elif field_name == '子类型':
                order_data['ziLeiXing'] = get_next_value(col_idx + 1)

            elif field_name == 'FSC类型':
                order_data['fscType'] = get_next_value(col_idx + 1)

            elif field_name == '装订方式':
                order_data['zhuangDingFangShi'] = get_next_value(col_idx + 1)

            elif field_name == '跟色指示':
                order_data['genSeZhiShi'] = get_next_value(col_idx + 1)

            elif field_name == '用途':
                order_data['yongTu'] = get_next_value(col_idx + 1)

            elif field_name == '客来信息':
                order_data['keLaiXinxi'] = get_next_value(col_idx + 1)

            elif field_name == '是否需要保留签色':
                order_data['baoLiuQianSe'] = get_next_value(col_idx + 1)

            elif field_name == '分版说明':
                order_data['fenBanShuoMing'] = get_next_value(col_idx + 1)

            # 数量字段
            elif field_name == '订单数量':
                order_data['dingDanShuLiang'] = safe_number(get_next_value(col_idx + 1))

            elif field_name == '出样数量':
                order_data['chuYangShuLiang'] = safe_number(get_next_value(col_idx + 1))

            elif field_name == '超比例数量':
                order_data['chaoBiLiShuLiang'] = safe_number(get_next_value(col_idx + 1))

            elif field_name == '备品数量':
                order_data['beiPinShuLiang'] = safe_number(get_next_value(col_idx + 1))

            elif field_name == '特殊留样张':
                order_data['teShuLiuYangZhang'] = safe_number(get_next_value(col_idx + 1))

            elif field_name == '特殊留书样':
                order_data['teShuLiuShuYang'] = safe_number(get_next_value(col_idx + 1))

            elif field_name == '总数量':
                order_data['zongShuLiang'] = safe_number(get_next_value(col_idx + 1))

            elif field_name == '出货':
                # 出货字段后面有数量和日期
                order_data['chuHuoShuLiang'] = safe_number(get_next_value(col_idx + 1))
                # 根据列索引提取日期
                order_data['chuHuoRiqiRequired'] = get_date_by_column(required_date_col)
                order_data['chuHuoRiqiPromise'] = get_date_by_column(promise_date_col)

            elif field_name == '出样说明':
                order_data['chuYangShuoMing'] = get_next_value(col_idx + 1)

            # 规格字段
            elif field_name == '高':
                order_data['guigeGaoMm'] = safe_number(get_next_value(col_idx + 1))

            elif field_name == '宽':
                order_data['guigeKuanMm'] = safe_number(get_next_value(col_idx + 1))

            elif field_name == '厚':
                order_data['guigeHouMm'] = safe_number(get_next_value(col_idx + 1))

            # 日期字段 - 根据列索引提取
            elif field_name == '下资料袋日期':
                order_data['xiaZiliaodaiRiqiRequired'] = get_date_by_column(required_date_col)
                order_data['xiaZiliaodaiRiqiPromise'] = get_date_by_column(promise_date_col)

            elif field_name == '印张日期':
                order_data['yinzhangRiqiRequired'] = get_date_by_column(required_date_col)
                order_data['yinzhangRiqiPromise'] = get_date_by_column(promise_date_col)

            elif field_name == '折排日期':
                order_data['zhepaiRiqiRequired'] = get_date_by_column(required_date_col)
                order_data['zhepaiRiqiPromise'] = get_date_by_column(promise_date_col)

            elif field_name == '出样日期：':
                order_data['chuyangRiqiRequired'] = get_date_by_column(required_date_col)
                order_data['chuyangRiqiPromise'] = get_date_by_column(promise_date_col)

            # 说明字段
            elif field_name == '辅料说明':
                order_data['fuLiaoShuoMing'] = get_next_value(col_idx + 1)

            elif field_name == '产品明细特别说明':
                order_data['chanPinMingXiTeBieShuoMing'] = get_next_value(col_idx + 1)

            elif field_name == '物料说明':
                order_data['wuLiaoShuoMing'] = get_next_value(col_idx + 1)

            elif field_name == '印刷和跟色要求':
                order_data['yinShuaGenSeYaoQiu'] = get_next_value(col_idx + 1)

            elif field_name == '装订/手工':
                order_data['zhuangDingShouGongYaoQiu'] = get_next_value(col_idx + 1)

            elif field_name == '其他':
                order_data['qiTa'] = get_next_value(col_idx + 1)

            elif field_name == '质量要求':
                order_data['zhiLiangYaoQiu'] = get_next_value(col_idx + 1)

            elif field_name == '客户反馈':
                order_data['keHuFanKui'] = get_next_value(col_idx + 1)

            elif field_name == '特殊要求':
                order_data['teShuYaoQiu'] = get_next_value(col_idx + 1)

            elif field_name == '控制方法':
                order_data['kongZhiFangFa'] = get_next_value(col_idx + 1)

            elif field_name in ['订单\n特别\n说明', '订单特别说明']:
                order_data['dingDanTeBieShuoMing'] = get_next_value(col_idx + 1)

            elif field_name == '样品评审信息':
                order_data['yangPinPingShenXinXi'] = get_next_value(col_idx + 1)

            elif field_name == '订单评审信息':
                order_data['dingDanPingShenXinXi'] = get_next_value(col_idx + 1)

            # 产品明细表头
            elif field_name == '内文' and '报价用纸尺寸' in str(row):
                # 这是产品明细的表头行，下一行开始是数据
                if 'chanPinMingXi' not in order_data:
                    order_data['chanPinMingXi'] = []
                # 从下一行开始解析产品明细，传入表头行用于动态查找列索引
                parse_product_details(table_data, row_idx, order_data)

    # 设置默认值
    set_defaults(order_data)


def parse_product_details(table_data: List[List[str]], header_row_idx: int, order_data: Dict[str, Any]):
    """
    解析产品明细数据

    根据 IProductDetail 接口定义的 14 个字段进行结构化提取
    动态查找列索引，而不是使用硬编码的列号
    """
    details = []

    # 获取表头行
    header_row = table_data[header_row_idx]

    # 动态查找每个字段的列索引
    col_map = {}
    field_mappings = {
        '内文': 'neiWen',
        '报价用纸尺寸': 'yongZhiChiCun',
        '厚度': 'houDu',
        '克重': 'keZhong',
        '产地': 'chanDi',
        '品牌': 'pinPai',
        '纸类': 'zhiLei',
        'FSC': 'FSC',
        '页数': 'yeShu',
        '印色': 'yinSe',
        '专色': 'zhuanSe',
        '表面处理': 'biaoMianChuLi',
        '装订工': 'zhuangDingGongYi',
        '备注': 'beiZhu'
    }

    # 遍历表头，找到每个字段的列索引
    for col_idx, cell in enumerate(header_row):
        if not cell:
            continue
        cell_text = clean_text(cell)
        for key, field_name in field_mappings.items():
            if key in cell_text:
                col_map[field_name] = col_idx
                break

    # 从表头的下一行开始解析数据
    for row_idx in range(header_row_idx + 1, len(table_data)):
        row = table_data[row_idx]

        if not row or not row[0]:
            continue

        # 如果遇到 "辅料说明"，停止解析
        if '辅料说明' in clean_text(row[0]):
            break

        # 使用动态列索引提取数据
        detail = {
            'neiWen': clean_text(row[col_map.get('neiWen', 0)]) if col_map.get('neiWen', 0) < len(row) else '',
            'yongZhiChiCun': clean_text(row[col_map.get('yongZhiChiCun', 1)]) if col_map.get('yongZhiChiCun', 1) < len(row) else '',
            'houDu': safe_number(row[col_map.get('houDu', 4)]) if col_map.get('houDu', 4) < len(row) else 0,
            'keZhong': safe_number(row[col_map.get('keZhong', 6)]) if col_map.get('keZhong', 6) < len(row) else 0,
            'chanDi': clean_text(row[col_map.get('chanDi', 8)]) if col_map.get('chanDi', 8) < len(row) else '',
            'pinPai': clean_text(row[col_map.get('pinPai', 9)]) if col_map.get('pinPai', 9) < len(row) else '',
            'zhiLei': clean_text(row[col_map.get('zhiLei', 11)]) if col_map.get('zhiLei', 11) < len(row) else '',
            'FSC': clean_text(row[col_map.get('FSC', 13)]) if col_map.get('FSC', 13) < len(row) else '',
            'yeShu': safe_number(row[col_map.get('yeShu', 14)]) if col_map.get('yeShu', 14) < len(row) else 0,
            'yinSe': clean_text(row[col_map.get('yinSe', 15)]) if col_map.get('yinSe', 15) < len(row) else '',
            'zhuanSe': clean_text(row[col_map.get('zhuanSe', 17)]) if col_map.get('zhuanSe', 17) < len(row) else '',
            'biaoMianChuLi': clean_text(row[col_map.get('biaoMianChuLi', 20)]) if col_map.get('biaoMianChuLi', 20) < len(row) else '',
            'zhuangDingGongYi': clean_text(row[col_map.get('zhuangDingGongYi', 22)]) if col_map.get('zhuangDingGongYi', 22) < len(row) else '',
            'beiZhu': clean_text(row[col_map.get('beiZhu', 24)]) if col_map.get('beiZhu', 24) < len(row) else '',
        }

        details.append(detail)

    order_data['chanPinMingXi'] = details if details else [create_empty_detail()]


def create_empty_detail() -> Dict[str, Any]:
    """创建空的产品明细行"""
    return {
        'neiWen': '',
        'yongZhiChiCun': '',
        'houDu': 0,
        'keZhong': 0,
        'chanDi': '',
        'pinPai': '',
        'zhiLei': '',
        'FSC': '',
        'yeShu': 0,
        'yinSe': '',
        'zhuanSe': '',
        'biaoMianChuLi': '',
        'zhuangDingGongYi': '',
        'beiZhu': '',
    }


def clean_text(text: str) -> str:
    """清理文本，去除多余的空白和换行"""
    if not text:
        return ''
    return ' '.join(text.split())


def safe_number(value: str) -> float:
    """安全转换为数字（保留小数）"""
    if not value:
        return 0
    try:
        # 保留小数点，移除其他非数字字符
        cleaned = ''.join(c for c in str(value) if c.isdigit() or c == '.' or c == '-')
        if cleaned:
            return float(cleaned)
        return 0
    except (ValueError, AttributeError):
        return 0


def safe_int(value: str) -> int:
    """安全转换为整数"""
    if not value:
        return 0
    try:
        # 先转换为浮点数（处理小数），再转为整数
        cleaned = ''.join(c for c in str(value) if c.isdigit() or c == '.')
        if cleaned:
            return int(float(cleaned))
        return 0
    except (ValueError, AttributeError):
        return 0


def set_defaults(order_data: Dict[str, Any]):
    """设置默认值"""
    defaults = {
        'customer': '',
        'productName': '',
        'order_id': '',
        'jiuBianMa': '',
        'isbn': '',
        'customerPO': '',
        'baoJiaDanHao': '',
        'xiLieDanMing': '',
        'qiTaShiBie': '',
        'chanPinDaLei': '',
        'ziLeiXing': '',
        'fscType': '',
        'zhuangDingFangShi': '',
        'genSeZhiShi': '',
        'yongTu': '',
        'keLaiXinxi': '',
        'baoLiuQianSe': '',
        'dingZhiBeiZhu': '',
        'dingDanShuLiang': 0,
        'chuYangShuLiang': 0,
        'chaoBiLiShuLiang': 0,
        'beiPinShuLiang': 0,
        'teShuLiuYangZhang': 0,
        'teShuLiuShuYang': 0,
        'zongShuLiang': 0,
        'chuHuoShuLiang': 0,
        'guigeGaoMm': 0,
        'guigeKuanMm': 0,
        'guigeHouMm': 0,
        'xiaZiliaodaiRiqiRequired': '',
        'yinzhangRiqiRequired': '',
        'zhepaiRiqiRequired': '',
        'chuyangRiqiRequired': '',
        'chuHuoRiqiRequired': '',
        'xiaZiliaodaiRiqiPromise': '',
        'yinzhangRiqiPromise': '',
        'zhepaiRiqiPromise': '',
        'chuyangRiqiPromise': '',
        'chuHuoRiqiPromise': '',
        'chuYangShuoMing': '',
        'fuLiaoShuoMing': '',
        'chanPinMingXiTeBieShuoMing': '',
        'fenBanShuoMing': '',
        'wuLiaoShuoMing': '',
        'yinShuaGenSeYaoQiu': '',
        'zhuangDingShouGongYaoQiu': '',
        'qiTa': '',
        'zhiLiangYaoQiu': '',
        'keHuFanKui': '',
        'teShuYaoQiu': '',
        'kongZhiFangFa': '',
        'dingDanTeBieShuoMing': '',
        'yangPinPingShenXinXi': '',
        'dingDanPingShenXinXi': '',
        'cpcQueRen': False,
        'waixiaoFlag': False,
        'cpsiaYaoqiu': False,
        'chanPinMingXi': [create_empty_detail()],
    }

    for key, default_value in defaults.items():
        if key not in order_data:
            order_data[key] = default_value
