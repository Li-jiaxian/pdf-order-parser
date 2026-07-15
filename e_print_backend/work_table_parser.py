"""
工程单（IWorkOrder）解析器

复用 table_parser 的订单表格提取能力，将解析结果 best-effort 映射为前端
IWorkOrder 结构：表头公共字段（客户、PO、成品名称、数量、日期等）+
将产品明细行映射为 intermedia（IIM）数组。解析不出的字段返回空值/0，
前端 Object.assign 时不会破坏已有表单内容。
"""
from table_parser import parse_order_from_pdf


def _product_to_iim(product: dict, index: int) -> dict:
    """订单产品明细行 -> 工程单工序行（与前端 OrderReviewer.productToIIM 保持一致）"""
    yin_se = product.get('yinSe') or ''
    zhuan_se = product.get('zhuanSe') or ''
    if zhuan_se and zhuan_se != '/':
        yin_shua_yan_se = f"{yin_se} 专色:{zhuan_se}" if yin_se else zhuan_se
    else:
        yin_shua_yan_se = yin_se

    ke_zhong = product.get('keZhong') or 0
    yong_zhi = product.get('yongZhiChiCun') or ''
    cai_liao_gui_ge = ' '.join(x for x in [f"{ke_zhong}g" if ke_zhong else '', yong_zhi] if x)

    return {
        'intermediaID': index,
        'buJianMingCheng': product.get('neiWen') or '',
        'yinShuaYanSe': yin_shua_yan_se,
        'wuLiaoMingCheng': product.get('zhiLei') or '',
        'pinPai': product.get('pinPai') or '',
        'caiLiaoGuiGe': cai_liao_gui_ge,
        'FSC': product.get('FSC') or '',
        'kaiShu': 0,
        'shangJiChiCun': '',
        'paiBanMuShu': 0,
        'yinChuShu': 0,
        'yinSun': 0,
        'lingLiaoShu': 0,
        'biaoMianChuLi': product.get('biaoMianChuLi') or '',
        'yinShuaBanShu': 0,
        'shengChanLuJing': '',
        'paiBanFangShi': '',
        'yiGouJianShu': 0,
        'head_PUR': '',
        'kaiShiRiQi': '',
        'yuQiJieShu': '',
        'dangQianJinDu': 0,
        'head_OUT': '',
    }


def parse_work_order_from_pdf(filepath: str) -> dict:
    """解析 PDF 并映射为 IWorkOrder 字段字典"""
    order = parse_order_from_pdf(filepath)

    products = order.get('chanPinMingXi') or []
    intermedia = [_product_to_iim(p, i) for i, p in enumerate(products)]

    return {
        'gongDanLeiXing': order.get('chanPinDaLei') or '',
        'caiLiao': '',
        'chanPinLeiXing': order.get('chanPinDaLei') or '',
        'customer': order.get('customer') or '',
        'customerPO': order.get('customerPO') or '',
        'productName': order.get('productName') or '',
        'chanPinGuiGe': '',
        'dingDanShuLiang': order.get('dingDanShuLiang') or 0,
        'chuYangShuLiang': order.get('chuYangShuLiang') or 0,
        'chaoBiLiShuLiang': order.get('chaoBiLiShuLiang') or 0,
        'benChangFangSun': 0,
        'chuYangRiqiRequired': order.get('chuyangRiqiRequired') or '',
        'chuHuoRiqiRequired': order.get('chuHuoRiqiRequired') or '',
        'intermedia': intermedia,
    }
