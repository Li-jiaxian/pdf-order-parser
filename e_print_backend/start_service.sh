#!/bin/bash
cd "$(dirname "$0")"
echo "启动 E_Print PDF 解析服务..."
python3 pdf_parser_service.py
