import fitz
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.platypus import Paragraph

try:
    pdfmetrics.registerFont(TTFont('SimSun', 'msyh.ttc'))
except Exception as e:
    print("⚠️ 字体加载失败，请确保字体文件存在：", e)
    # 回退到默认字体（但中文仍会显示方块）
    USE_CHINESE_FONT = False
else:
    USE_CHINESE_FONT = True



def get_segment_from_pdf(pdf_path):
    """
    从PDF中提取段落，并记录每个段落的颜色
    """
    doc = fitz.open(pdf_path)
    results = []

    for page_num, page in enumerate(doc):
        # 获取页面文本字典（包含字符级信息）
        text_dict = page.get_text("dict")

        for block in text_dict["blocks"]:
            if "lines" not in block:
                continue  # 跳过图像块

            # 每个 block 通常对应一个视觉段落
            paragraph_text = ""
            colors = []

            for line in block["lines"]:
                line_text = ""
                line_colors = []

                for span in line["spans"]:
                    # span 是相同字体、大小、颜色的文本片段
                    line_text += span["text"]
                    # span["color"] 是一个整数，表示 RGB 编码：0xRRGGBB
                    rgb = span["color"]
                    r = (rgb >> 16) & 0xFF
                    g = (rgb >> 8) & 0xFF
                    b = rgb & 0xFF
                    color_tuple = (r, g, b)
                    # 同一 span 内颜色一致，可记录一次
                    line_colors.extend([color_tuple] * len(span["text"]))

                paragraph_text += line_text
                colors.extend(line_colors)

            if paragraph_text.strip():
                para_color = list(set(colors))
                results.append({
                    "text": paragraph_text.strip(),
                    "color": para_color,
                    "page": page_num + 1
                })

    return results


def process_segments(result):
    """
    处理提取的段落，将颜色信息转换为 ReportLab 需要的格式
    """
    segments = []
    for item in result:
        text = item["text"]
        color = item["color"]
        if len(color) <= 1:
            segments.append({
                "text": text,
                "color": [51, 51, 51]  # 黑色固定值
            })
        else:
            segments.append({
                "text": text,
                "color": [255, 0, 0]  # 红色
            })

            segments.append({
                "text": 'test' + text,
                "color": [0, 128, 0]  # 绿色
            })

    return segments

def rgb_to_reportlab_color(rgb):
    return Color(rgb[0]/255, rgb[1]/255, rgb[2]/255)


def create_pdf(segments, output_path):
    """
    将处理后的段落写入PDF文件
    """
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    y = height - 50
    line_height = 20
    left_margin = 50
    max_width = width - 2 * left_margin

    # 设置字体和样式
    if USE_CHINESE_FONT:
        font_name = 'SimSun'
        font_size = 12
    else:
        font_name = 'Helvetica'
        font_size = 12

    style = ParagraphStyle(
        name='Normal',
        fontName=font_name,
        fontSize=font_size,
        leading=font_size * 1.2,
        alignment=TA_LEFT,
        textColor=colors.black,  # 默认颜色，后面覆盖
    )

    for seg in segments:
        text = seg["text"]
        color = rgb_to_reportlab_color(seg["color"])
        style.textColor = color

        para = Paragraph(text, style)

        # 计算段落大小
        w, h = para.wrap(max_width, y)
        if y - h < 50:
            c.showPage()
            y = height - 50
        para.drawOn(c, left_margin, y - h)
        y -= (h + 5)  # 段间距5

    c.save()


if __name__ == '__main__':
    segments = get_segment_from_pdf("test.pdf")
    results = process_segments(segments)
    
    # create_pdf不需要，接口直接返回段落内容渲染
    # create_pdf(results, "output.pdf")

