#!/usr/bin/env python3
"""
小红书图文笔记转PDF工具
使用命令行参数将小红书笔记转换为PDF文档
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# 尝试导入必要库
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.enums import TA_LEFT
    import requests
except ImportError as e:
    print(f"错误: 缺少必要的依赖库")
    print(f"请安装: pip3 install reportlab requests")
    sys.exit(1)


class XiaohongshuToPDF:
    """小红书笔记转PDF转换器"""

    def __init__(self, feed_id, xsec_token, output_path=None):
        self.feed_id = feed_id
        self.xsec_token = xsec_token
        self.output_path = output_path or str(Path.home() / "Desktop")

        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp(prefix="xhs_pdf_")

        # 注册中文字体
        self._register_fonts()

    def _register_fonts(self):
        """注册中文字体"""
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",  # macOS
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",  # Linux
            "C:/Windows/Fonts/msyh.ttc",  # Windows
        ]

        self.font_registered = False
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont("ChineseFont", font_path))
                    self.font_registered = True
                    print(f"✓ 已注册中文字体: {font_path}")
                    break
                except Exception as e:
                    continue

        if not self.font_registered:
            print("⚠ 警告: 未找到中文字体,PDF可能无法正确显示中文")

    def download_image(self, url, index):
        """下载图片到临时目录"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            ext = ".jpg"
            if "png" in url.lower():
                ext = ".png"

            filename = f"image_{index}{ext}"
            filepath = os.path.join(self.temp_dir, filename)

            with open(filepath, "wb") as f:
                f.write(response.content)

            return filepath
        except Exception as e:
            print(f"⚠ 下载图片失败: {e}")
            return None

    def fetch_feed_data(self):
        """通过MCP获取笔记数据（模拟）"""
        # 注意: 实际使用时需要通过MCP工具调用
        # 这里返回占位符,实际数据由MCP工具提供
        print(f"⚠ 提示: 请使用MCP工具 mcp__xiaohongshu__get_feed_detail 获取笔记数据")
        return None

    def create_pdf(self, feed_data):
        """创建PDF文档"""
        if not feed_data:
            raise ValueError("笔记数据为空")

        # 生成文件名
        safe_title = "".join(c for c in feed_data.get("title", "小红书笔记") if c.isalnum() or c in (" ", "-", "_"))
        safe_title = safe_title[:50]  # 限制长度
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"{safe_title}_{timestamp}.pdf"
        pdf_path = os.path.join(self.output_path, pdf_filename)

        # 创建PDF
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        # 样式
        styles = getSampleStyleSheet()
        if self.font_registered:
            styles.add(ParagraphStyle(
                name="ChineseTitle",
                parent=styles["Heading1"],
                fontName="ChineseFont",
                fontSize=18,
                textColor="#333333",
                spaceAfter=12,
            ))
            styles.add(ParagraphStyle(
                name="ChineseNormal",
                parent=styles["Normal"],
                fontName="ChineseFont",
                fontSize=11,
                leading=16,
                spaceAfter=8,
            ))
            title_style = styles["ChineseTitle"]
            content_style = styles["ChineseNormal"]
        else:
            title_style = styles["Heading1"]
            content_style = styles["Normal"]

        # 构建内容
        story = []

        # 标题
        title = feed_data.get("title", "小红书笔记")
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.5 * cm))

        # 作者信息
        author = feed_data.get("author", {})
        author_name = author.get("nickname", "未知作者")
        story.append(Paragraph(f"<b>作者:</b> {author_name}", content_style))
        story.append(Spacer(1, 0.3 * cm))

        # 正文内容
        desc = feed_data.get("desc", "")
        if desc:
            story.append(Paragraph("<b>内容:</b>", content_style))
            story.append(Spacer(1, 0.2 * cm))
            paragraphs = desc.split("\n")
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para, content_style))
            story.append(Spacer(1, 0.5 * cm))

        # 图片
        images = feed_data.get("images", [])
        if images:
            story.append(Paragraph("<b>配图:</b>", content_style))
            story.append(Spacer(1, 0.3 * cm))

            max_width = 14 * cm
            max_height = 10 * cm

            for idx, img_url in enumerate(images):
                img_path = self.download_image(img_url, idx)
                if img_path and os.path.exists(img_path):
                    try:
                        img = Image(img_path)
                        img_width, img_height = img.drawWidth, img.drawHeight

                        # 缩放图片
                        ratio = min(max_width / img_width, max_height / img_height, 1)
                        img.drawWidth = img_width * ratio
                        img.drawHeight = img_height * ratio

                        story.append(img)
                        story.append(Spacer(1, 0.3 * cm))
                    except Exception as e:
                        print(f"⚠ 添加图片失败: {e}")

        # 生成PDF
        try:
            doc.build(story)
            print(f"✓ PDF已生成: {pdf_path}")
            return pdf_path
        except Exception as e:
            raise RuntimeError(f"PDF生成失败: {e}")

    def cleanup(self):
        """清理临时文件"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"⚠ 清理临时文件失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="小红书笔记转PDF工具")
    parser.add_argument("--feed-id", required=True, help="小红书笔记ID")
    parser.add_argument("--xsec-token", required=True, help="访问令牌")
    parser.add_argument("--output", help="PDF输出目录（默认: 桌面）")

    args = parser.parse_args()

    # 创建转换器
    converter = XiaohongshuToPDF(
        feed_id=args.feed_id,
        xsec_token=args.xsec_token,
        output_path=args.output
    )

    print(f"小红书笔记转PDF工具")
    print(f"笔记ID: {args.feed_id}")
    print(f"输出目录: {converter.output_path}")
    print(f"临时目录: {converter.temp_dir}")
    print()

    # 注意: 实际使用需要通过MCP工具获取数据
    print("请通过MCP工具获取笔记数据后,调用 converter.create_pdf(feed_data) 方法生成PDF")

    converter.cleanup()


if __name__ == "__main__":
    main()
