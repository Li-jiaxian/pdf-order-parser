#!/usr/bin/env python3
"""
测试 PDF 解析功能
"""
import sys
sys.path.insert(0, '/Users/markov_lee/Code/InStruct')

from extract_pdf import extract_text_from_pdf
from order_parser import parse_order_text

# 测试文件路径
test_pdf = '/Users/markov_lee/Code/E_Print/案例_订单.pdf'

print('=' * 60)
print('测试 PDF 解析功能')
print('=' * 60)

try:
    # 提取文本
    print(f'\n1. 提取 PDF 文本: {test_pdf}')
    text = extract_text_from_pdf(test_pdf)
    print(f'   ✓ 成功提取 {len(text)} 字符')
    print(f'\n前 500 字符预览:')
    print('-' * 60)
    print(text[:500])
    print('-' * 60)

    # 解析订单数据
    print(f'\n2. 解析订单数据...')
    order_data = parse_order_text(text)
    print(f'   ✓ 成功解析 {len(order_data)} 个字段')

    # 显示解析结果
    print(f'\n3. 解析结果预览:')
    print('-' * 60)
    for key, value in list(order_data.items())[:15]:
        if value:
            print(f'   {key}: {value}')
    print('-' * 60)

    print('\n✓ 测试通过！')

except Exception as e:
    print(f'\n✗ 测试失败: {e}')
    import traceback
    traceback.print_exc()
