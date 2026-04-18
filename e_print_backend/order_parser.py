"""
订单 PDF 解析模块
使用正则表达式从 PDF 文本中提取订单字段
"""
import re
from typing import Dict, Any, List, Optional


def parse_order_text(text: str) -> Dict[str, Any]:
    """
    从 PDF 提取的文本中解析订单信息

    Args:
        text: PDF 提取的原始文本

    Returns:
        符合 IOrder 接口的字典数据
    """
    order_data = {}

    # 基础信息字段 - 使用 next_line 方法
    order_data['customer'] = extract_field_next_line(text, '客户')
    order_data['order_id'] = extract_field_next_line(text, '订单号')
    order_data['productName'] = extract_field_next_line(text, '成品名称')
    order_data['jiuBianMa'] = extract_field_next_line(text, '旧编码')
    order_data['isbn'] = extract_field_next_line(text, 'ISBN')
    order_data['customerPO'] = extract_field_next_line(text, '客户PO')
    order_data['baoJiaDanHao'] = extract_field_next_line(text, '报价单号')
    order_data['xiLieDanMing'] = extract_field_next_line(text, '系列单名')
    order_data['qiTaShiBie'] = extract_field_next_line(text, '其他识别')
    order_data['chanPinDaLei'] = extract_field_next_line(text, '产品大类')
    order_data['ziLeiXing'] = extract_field_next_line(text, '子类型')
    order_data['fscType'] = extract_field_next_line(text, 'FSC类型')
    order_data['zhuangDingFangShi'] = extract_field_next_line(text, '装订方式')
    order_data['genSeZhiShi'] = extract_field_next_line(text, '跟色指示')
    order_data['yongTu'] = extract_field_next_line(text, '用途')
    order_data['keLaiXinxi'] = extract_field_next_line(text, '客来信息')
    order_data['baoLiuQianSe'] = extract_field_next_line(text, '是否需要保留签色')
    order_data['dingZhiBeiZhu'] = extract_field(text, r'订纸备注\s*\n\s*(.+?)(?:\n|$)')

    # 数量字段
    order_data['dingDanShuLiang'] = extract_number_next_line(text, '订单数量')
    order_data['chuYangShuLiang'] = extract_number_next_line(text, '出样数量')
    order_data['chaoBiLiShuLiang'] = extract_number_next_line(text, '超比例数量')
    order_data['beiPinShuLiang'] = extract_number_next_line(text, '备品数量')
    order_data['teShuLiuYangZhang'] = extract_number_next_line(text, '特殊留样张')
    order_data['teShuLiuShuYang'] = extract_number_next_line(text, '特殊留书样')
    order_data['zongShuLiang'] = extract_number_next_line(text, '总数量')

    # 出货数量需要特殊处理（在"出货"后面的数字）
    chuHuoMatch = re.search(r'出货\s*\n\s*(\d+)', text)
    order_data['chuHuoShuLiang'] = int(chuHuoMatch.group(1)) if chuHuoMatch else 0

    # 规格字段 (MM) - 需要找到"高 127 MM"这样的模式
    gaoMatch = re.search(r'高\s*\n\s*(\d+)\s*\n\s*MM', text)
    kuanMatch = re.search(r'宽\s*\n\s*(\d+)\s*\n\s*MM', text)
    houMatch = re.search(r'厚\s*\n\s*(\d+)\s*\n\s*MM', text)

    order_data['guigeGaoMm'] = int(gaoMatch.group(1)) if gaoMatch else 0
    order_data['guigeKuanMm'] = int(kuanMatch.group(1)) if kuanMatch else 0
    order_data['guigeHouMm'] = int(houMatch.group(1)) if houMatch else 0

    # 日期字段 - 需要特殊处理
    # 格式：下资料袋日期 2025-10-29
    order_data['xiaZiliaodaiRiqiRequired'] = extract_field_next_line(text, '下资料袋日期')
    order_data['yinzhangRiqiRequired'] = extract_field_next_line(text, '印张日期')
    order_data['zhepaiRiqiRequired'] = extract_field_next_line(text, '折排日期')

    # 出样日期格式：出样日期：2025-11-24
    chuYangDateMatch = re.search(r'出样日期[:：]\s*\n?\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})', text)
    order_data['chuyangRiqiRequired'] = chuYangDateMatch.group(1).replace('/', '-') if chuYangDateMatch else ''

    # 出货日期在"出货"行后面
    chuHuoDateMatch = re.search(r'出货\s*\n\s*\d+\s*\n\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})', text)
    order_data['chuHuoRiqiRequired'] = chuHuoDateMatch.group(1).replace('/', '-') if chuHuoDateMatch else ''

    # 承诺日期（暂时留空，PDF 中没有明确标注）
    order_data['xiaZiliaodaiRiqiPromise'] = ''
    order_data['yinzhangRiqiPromise'] = ''
    order_data['zhepaiRiqiPromise'] = ''
    order_data['chuyangRiqiPromise'] = ''
    order_data['chuHuoRiqiPromise'] = ''

    # 说明字段
    order_data['chuYangShuoMing'] = extract_field_next_line(text, '出样说明')
    order_data['fuLiaoShuoMing'] = extract_field_next_line(text, '辅料说明')
    order_data['chanPinMingXiTeBieShuoMing'] = extract_field_next_line(text, '产品明细特别说明')
    order_data['fenBanShuoMing'] = extract_field_next_line(text, '分版说明')
    order_data['wuLiaoShuoMing'] = extract_field_next_line(text, '物料说明')
    order_data['yinShuaGenSeYaoQiu'] = extract_field_next_line(text, '印刷和跟色要求')
    order_data['zhuangDingShouGongYaoQiu'] = extract_field_next_line(text, '装订/手工')
    order_data['qiTa'] = extract_field_next_line(text, '其他')
    order_data['zhiLiangYaoQiu'] = extract_field_next_line(text, '质量要求')
    order_data['keHuFanKui'] = extract_field_next_line(text, '客户反馈')
    order_data['teShuYaoQiu'] = extract_field_next_line(text, '特殊要求')
    order_data['kongZhiFangFa'] = extract_field_next_line(text, '控制方法')
    order_data['dingDanTeBieShuoMing'] = extract_field_next_line(text, '订单特别说明')
    order_data['yangPinPingShenXinXi'] = extract_field_next_line(text, '样品评审信息')
    order_data['dingDanPingShenXinXi'] = extract_field_next_line(text, '订单评审信息')

    # 布尔字段
    order_data['cpcQueRen'] = 'CPC已确认' in text or 'cpc确认' in text.lower()
    order_data['waixiaoFlag'] = 'OutSourcing' in text
    order_data['cpsiaYaoqiu'] = 'CPSIA' in text and '非CPSIA' not in text

    # 产品明细
    order_data['chanPinMingXi'] = parse_product_details(text)

    return order_data


def extract_field(text: str, pattern: str) -> str:
    """提取文本字段"""
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else ''


def extract_field_next_line(text: str, keyword: str) -> str:
    """
    提取字段值（字段名和值在不同行）
    例如：
    客户
    当纳利亚洲印务有限公司

    如果下一行是另一个字段名或为空，则返回空字符串
    """
    pattern = rf'{keyword}\s*\n\s*(.+?)(?:\n|$)'
    match = re.search(pattern, text, re.IGNORECASE)

    if not match:
        return ''

    value = match.group(1).strip()

    # 常见的字段名列表（如果提取到的是字段名，说明原字段为空）
    field_names = [
        '客户', '订单号', '成品名称', '旧编码', 'ISBN', '客户PO', '报价单号',
        '系列单名', '其他识别', '产品大类', '子类型', 'FSC类型', '装订方式',
        '跟色指示', '用途', '客来信息', '是否需要保留签色', '订纸备注',
        '订单数量', '出样数量', '超比例数量', '备品数量', '特殊留样张',
        '特殊留书样', '总数量', '出货', '规格规格', '高', '宽', '厚',
        '下资料袋日期', '印张日期', '折排日期', '出样日期', '要求日期',
        'CPC承诺日期', '出样说明', '辅料说明', '产品明细特别说明',
        '分版说明', '物料说明', '印刷和跟色要求', '装订/手工', '其他',
        '质量要求', '客户反馈', '特殊要求', '控制方法', '订单特别说明',
        '样品评审信息', '订单评审信息', '配套包装', '成品规格'
    ]

    # 如果提取到的值是字段名，说明原字段为空
    for field_name in field_names:
        if value == field_name or value.startswith(field_name):
            return ''

    # 如果提取到的值看起来像是表格列名或单位，也认为是空值
    if value in ['MM', 'FSC', '规格', '高', '宽', '厚', '用途']:
        return ''

    return value


def extract_number_next_line(text: str, keyword: str) -> int:
    """提取数字字段（字段名和值在不同行）"""
    value = extract_field_next_line(text, keyword)
    try:
        return int(re.sub(r'[^\d]', '', value))
    except (ValueError, AttributeError):
        return 0


def extract_number(text: str, pattern: str) -> int:
    """提取数字字段"""
    match = re.search(pattern, text, re.IGNORECASE)
    return int(match.group(1)) if match else 0


def extract_date(text: str, pattern: str) -> str:
    """提取日期字段，转换为 YYYY-MM-DD 格式"""
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        date_str = match.group(1).replace('/', '-')
        return date_str
    return ''


def check_checkbox(text: str, keyword: str) -> bool:
    """检查复选框是否勾选"""
    # 简单检查关键词是否存在
    return keyword.lower() in text.lower()


def parse_product_details(text: str) -> List[Dict[str, Any]]:
    """
    解析产品明细表格
    PDF格式：列标题在前，每列数据在后面的行中
    """
    details = []

    # 查找产品明细部分
    detail_section = re.search(r'产品明细(.*?)(?:辅料说明|$)', text, re.DOTALL | re.IGNORECASE)
    if not detail_section:
        return [create_empty_detail()]

    detail_text = detail_section.group(1)
    lines = [line.strip() for line in detail_text.strip().split('\n') if line.strip()]

    # 定义列标题关键词（按顺序）
    headers = [
        '内文', '报价用纸尺寸', '厚度', '克重', '产地', '品牌', '纸类',
        'FSC', '页数', '印色', '专色', '表面处理', '装订工艺', '备注'
    ]

    # 找到第一个数据行的起始位置（跳过所有标题行）
    data_start_idx = 0
    for i, line in enumerate(lines):
        # 如果这行不是任何标题关键词，说明数据开始了
        is_header = False
        for header in headers:
            if header in line:
                is_header = True
                break

        if not is_header and line and not line.startswith('产品明细'):
            data_start_idx = i
            break

    # 提取数据行
    data_lines = lines[data_start_idx:]

    if not data_lines:
        return [create_empty_detail()]

    # 每14行为一个产品明细记录
    num_fields = len(headers)
    num_records = len(data_lines) // num_fields

    for record_idx in range(num_records):
        start_idx = record_idx * num_fields
        end_idx = start_idx + num_fields

        if end_idx > len(data_lines):
            break

        record_data = data_lines[start_idx:end_idx]

        detail = create_empty_detail()
        detail['neiWen'] = record_data[0] if len(record_data) > 0 else ''
        detail['yongZhiChiCun'] = record_data[1] if len(record_data) > 1 else ''
        detail['houDu'] = safe_int(record_data[2]) if len(record_data) > 2 else 0
        detail['keZhong'] = safe_int(record_data[3]) if len(record_data) > 3 else 0
        detail['chanDi'] = record_data[4] if len(record_data) > 4 else ''
        detail['pinPai'] = record_data[5] if len(record_data) > 5 else ''
        detail['zhiLei'] = record_data[6] if len(record_data) > 6 else ''
        detail['FSC'] = record_data[7] if len(record_data) > 7 else ''
        detail['yeShu'] = safe_int(record_data[8]) if len(record_data) > 8 else 0
        detail['yinSe'] = record_data[9] if len(record_data) > 9 else ''
        detail['zhuanSe'] = record_data[10] if len(record_data) > 10 else ''
        detail['biaoMianChuLi'] = record_data[11] if len(record_data) > 11 else ''
        detail['zhuangDingGongYi'] = record_data[12] if len(record_data) > 12 else ''
        detail['beiZhu'] = record_data[13] if len(record_data) > 13 else ''

        details.append(detail)

    # 如果没有解析到任何明细，返回一个空行
    if not details:
        details.append(create_empty_detail())

    return details


def parse_detail_line(line: str) -> Optional[Dict[str, Any]]:
    """解析产品明细的一行（已废弃，保留以防需要）"""
    return None


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


def safe_int(value: str) -> int:
    """安全转换为整数"""
    try:
        return int(re.sub(r'[^\d]', '', value))
    except (ValueError, AttributeError):
        return 0
