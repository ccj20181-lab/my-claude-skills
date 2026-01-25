#!/usr/bin/env python3
"""
小红书图文笔记转PDF工具
使用命令行参数将小红书笔记转换为PDF文档
"""

import argparse
import json
import os
import re
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
    try:
        from PIL import Image as PILImage
    except ImportError:
        PILImage = None
except ImportError as e:
    print(f"错误: 缺少必要的依赖库")
    print(f"请安装: pip3 install reportlab requests pillow")
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
        print("🔍 正在检测中文字体...")

        # 扩展字体路径列表（按优先级排序）
        font_paths = [
            # macOS - 用户字体目录（优先，避免权限问题）
            os.path.expanduser("~/Library/Fonts/PingFangSC-Regular.ttf"),
            os.path.expanduser("~/Library/Fonts/PingFang-SC-Regular.ttf"),
            os.path.expanduser("~/Library/Fonts/PingFangSC-Medium.ttf"),
            os.path.expanduser("~/Library/Fonts/PingFang-SC-Medium.ttf"),
            os.path.expanduser("~/Library/Fonts/Microsoft Yahei.ttf"),
            # macOS - 系统字体目录
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/PingFang.ttc",
            # Linux
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            # Windows
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/msyhbd.ttc",
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/simhei.ttf",
        ]

        self.font_registered = False

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    # 优先尝试直接注册TTF
                    pdfmetrics.registerFont(TTFont("ChineseFont", font_path))
                    self.font_registered = True
                    print(f"✓ 已注册中文字体: {font_path}")
                    break
                except Exception as e:
                    # 如果失败，尝试注册TTC的第一个子字体
                    try:
                        pdfmetrics.registerFont(TTFont("ChineseFont", font_path, subfontIndex=0))
                        self.font_registered = True
                        print(f"✓ 已注册中文字体(TTC子字体): {font_path}")
                        break
                    except Exception as e2:
                        continue

        if not self.font_registered:
            print("⚠ 警告: 未找到可用的中文字体")
            print("   PDF将使用默认字体，中文可能显示异常")
            print("   建议安装中文字体:")
            print("   - macOS: PingFang SC, STHeiti")
            print("   - Linux: fonts-wqy-microhei (sudo apt install fonts-wqy-microhei)")
            print("   - Windows: Microsoft YaHei")

    def download_image(self, url, index):
        """下载图片到临时目录"""
        try:
            # 不再截断 URL，保持完整以通过签名验证
            # clean_url = url.split('!')[0] if '!' in url else url
            clean_url = url

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://www.xiaohongshu.com/",
                "Origin": "https://www.xiaohongshu.com",
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
            }

            response = requests.get(clean_url, headers=headers, timeout=30)
            response.raise_for_status()

            # 检测内容类型
            content_type = response.headers.get('Content-Type', '').lower()
            ext = ".jpg"
            if "png" in content_type or "png" in url.lower():
                ext = ".png"
            elif "webp" in content_type or "webp" in url.lower():
                ext = ".webp"

            filename = f"image_{index}{ext}"
            filepath = os.path.join(self.temp_dir, filename)

            with open(filepath, "wb") as f:
                f.write(response.content)

            # 如果是 WebP，尝试转换为 PNG
            if ext == ".webp":
                if PILImage:
                    try:
                        png_filepath = os.path.join(self.temp_dir, f"image_{index}.png")
                        img = PILImage.open(filepath)
                        img.save(png_filepath, "PNG")
                        return png_filepath
                    except Exception as e:
                        print(f"⚠ 转换 WebP 图片失败: {e}")
                        return filepath
                else:
                    print("⚠ 缺少 PIL 库，无法转换 WebP 图片，PDF 生成可能会失败")
                    return filepath

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
            # 标题样式 - 更大更醒目
            styles.add(ParagraphStyle(
                name="ChineseTitle",
                parent=styles["Heading1"],
                fontName="ChineseFont",
                fontSize=20,
                textColor="#2c3e50",
                spaceAfter=12,
                leading=24,
            ))
            # 正文样式 - 改进行距和间距
            styles.add(ParagraphStyle(
                name="ChineseNormal",
                parent=styles["Normal"],
                fontName="ChineseFont",
                fontSize=11,
                leading=18,
                spaceAfter=10,
                textColor="#34495e",
            ))
            # 副标题样式（作者、标签等）
            styles.add(ParagraphStyle(
                name="ChineseSubTitle",
                parent=styles["Normal"],
                fontName="ChineseFont",
                fontSize=10,
                leading=14,
                spaceAfter=6,
                textColor="#7f8c8d",
            ))
            title_style = styles["ChineseTitle"]
            content_style = styles["ChineseNormal"]
            subtitle_style = styles["ChineseSubTitle"]
        else:
            title_style = styles["Heading1"]
            content_style = styles["Normal"]
            subtitle_style = styles["Normal"]

        # 构建内容
        story = []

        # 标题
        title = feed_data.get("title", "小红书笔记")
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.5 * cm))

        # 作者信息
        author = feed_data.get("author", {})
        author_name = author.get("nickname", "未知作者")
        story.append(Paragraph(f"<b>作者:</b> {author_name}", subtitle_style))
        story.append(Spacer(1, 0.3 * cm))

        # 正文内容（改进格式化）
        desc = feed_data.get("desc", "")
        if desc:
            # 移除话题标签 (#xxx) 和多余的空行
            desc = re.sub(r'#[^\s#]+', '', desc)  # 移除话题标签
            desc = re.sub(r'\n{3,}', '\n\n', desc)  # 合并多余空行
            desc = desc.strip()

            if desc:
                story.append(Paragraph("<b>正文内容</b>", title_style))
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

            # A4 宽度约 21cm, 减去边距 4cm = 17cm
            # A4 高度约 29.7cm, 减去边距 4cm = 25.7cm
            max_width = 17 * cm
            max_height = 20 * cm  # 限制最大高度，避免图片过大无法放置

            for idx, img_url in enumerate(images):
                img_path = self.download_image(img_url, idx)
                if img_path and os.path.exists(img_path):
                    try:
                        img = Image(img_path)
                        img_width, img_height = img.drawWidth, img.drawHeight

                        # 缩放图片: 保持宽度适应页面，同时限制高度
                        ratio_width = max_width / img_width
                        ratio_height = max_height / img_height
                        ratio = min(ratio_width, ratio_height)

                        # 如果图片本身就很小，就不放大
                        if ratio > 1:
                            ratio = 1

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
