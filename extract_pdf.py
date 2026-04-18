from pathlib import Path
import fitz


def is_text_pdf(pdf_path: str, min_chars: int = 20) -> bool:
    with fitz.open(pdf_path) as doc:
        total_text = ""
        for page in doc:
            total_text += page.get_text("text")
            if len(total_text.strip()) >= min_chars:
                return True
    return False


def extract_text_from_pdf(pdf_path: str, output_txt: str | None = None) -> str:
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"文件不存在: {pdf_path}")

    if not is_text_pdf(pdf_path):
        raise ValueError("该 PDF 似乎不是文本型 PDF，无法直接提取有效文字。")

    text_parts = []

    with fitz.open(pdf_file) as doc:
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            text_parts.append(f"\n===== 第 {page_num} 页 =====\n{text}")

    full_text = "\n".join(text_parts).strip()

    if output_txt:
        Path(output_txt).write_text(full_text, encoding="utf-8")

    return full_text


if __name__ == "__main__":
    pdf_path = "example.pdf"
    output_txt = "output.txt"

    try:
        text = extract_text_from_pdf(pdf_path, output_txt)
        print("提取成功")
        print(f"输出文件: {output_txt}")
    except Exception as e:
        print(f"失败: {e}")