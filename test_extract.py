from pathlib import Path
from extract_pdf import is_text_pdf, extract_text_from_pdf


def test_pdfs_in_docs():
    docs_dir = Path("docs")
    output_dir = Path("extracted_texts")

    if not docs_dir.exists():
        print(f"错误: {docs_dir} 目录不存在")
        return

    # 创建输出目录
    output_dir.mkdir(exist_ok=True)

    pdf_files = list(docs_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"在 {docs_dir} 中没有找到 PDF 文件")
        return

    print(f"找到 {len(pdf_files)} 个 PDF 文件\n")
    print("=" * 80)

    for pdf_file in pdf_files:
        print(f"\n测试文件: {pdf_file.name}")
        print("-" * 80)

        try:
            # 检测是否为文本型 PDF
            is_text = is_text_pdf(str(pdf_file))
            print(f"是否为文本型 PDF: {'是' if is_text else '否'}")

            if is_text:
                # 生成输出文件名
                output_file = output_dir / f"{pdf_file.stem}.txt"

                # 提取文本并保存
                text = extract_text_from_pdf(str(pdf_file), str(output_file))

                # 显示提取的文本长度
                print(f"提取的文本长度: {len(text)} 字符")

                # 显示前 200 字符作为预览
                preview = text[:200].replace("\n", " ")
                print(f"文本预览: {preview}...")

                print(f"✓ 提取成功，已保存到: {output_file}")
            else:
                print("⚠ 该 PDF 不是文本型 PDF，跳过提取")

        except Exception as e:
            print(f"✗ 处理失败: {e}")

        print("-" * 80)

    print("\n" + "=" * 80)
    print(f"测试完成，提取的文本已保存到 {output_dir} 目录")


if __name__ == "__main__":
    test_pdfs_in_docs()
