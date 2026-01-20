#!/usr/bin/env python3
"""
中文字体检测和验证工具
用于检测系统中可用的中文字体
"""

import os
import sys
from pathlib import Path

# 中文字体列表（按优先级排序）
FONT_CONFIGS = [
    # macOS - 用户字体目录（优先）
    {
        "path": "~/Library/Fonts/PingFangSC-Regular.ttf",
        "platform": "macOS",
        "name": "PingFang SC Regular",
        "type": "TTF",
        "recommended": True,
    },
    {
        "path": "~/Library/Fonts/PingFang-SC-Regular.ttf",
        "platform": "macOS",
        "name": "PingFang SC Regular (alternate)",
        "type": "TTF",
        "recommended": True,
    },
    {
        "path": "~/Library/Fonts/PingFangSC-Medium.ttf",
        "platform": "macOS",
        "name": "PingFang SC Medium",
        "type": "TTF",
        "recommended": True,
    },
    {
        "path": "~/Library/Fonts/PingFang-SC-Medium.ttf",
        "platform": "macOS",
        "name": "PingFang SC Medium (alternate)",
        "type": "TTF",
        "recommended": True,
    },
    {
        "path": "~/Library/Fonts/Microsoft Yahei.ttf",
        "platform": "macOS",
        "name": "Microsoft YaHei",
        "type": "TTF",
        "recommended": False,
    },
    # macOS - 系统字体目录
    {
        "path": "/System/Library/Fonts/STHeiti Medium.ttc",
        "platform": "macOS",
        "name": "STHeiti Medium",
        "type": "TTC",
        "recommended": True,
    },
    {
        "path": "/System/Library/Fonts/STHeiti Light.ttc",
        "platform": "macOS",
        "name": "STHeiti Light",
        "type": "TTC",
        "recommended": True,
    },
    {
        "path": "/System/Library/Fonts/PingFang.ttc",
        "platform": "macOS",
        "name": "PingFang",
        "type": "TTC",
        "recommended": False,
    },
    # Linux
    {
        "path": "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "platform": "Linux",
        "name": "Droid Sans Fallback",
        "type": "TTF",
        "recommended": True,
    },
    {
        "path": "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "platform": "Linux",
        "name": "WQY MicroHei",
        "type": "TTC",
        "recommended": True,
    },
    {
        "path": "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "platform": "Linux",
        "name": "WQY ZenHei",
        "type": "TTC",
        "recommended": True,
    },
    # Windows
    {
        "path": "C:/Windows/Fonts/msyh.ttc",
        "platform": "Windows",
        "name": "Microsoft YaHei",
        "type": "TTC",
        "recommended": True,
    },
    {
        "path": "C:/Windows/Fonts/msyhbd.ttc",
        "platform": "Windows",
        "name": "Microsoft YaHei Bold",
        "type": "TTC",
        "recommended": False,
    },
    {
        "path": "C:/Windows/Fonts/simsun.ttc",
        "platform": "Windows",
        "name": "SimSun",
        "type": "TTC",
        "recommended": True,
    },
    {
        "path": "C:/Windows/Fonts/simhei.ttf",
        "platform": "Windows",
        "name": "SimHei",
        "type": "TTF",
        "recommended": True,
    },
]


def detect_platform():
    """检测当前操作系统"""
    platform = sys.platform
    if platform == "darwin":
        return "macOS"
    elif platform.startswith("linux"):
        return "Linux"
    elif platform == "win32":
        return "Windows"
    else:
        return "Unknown"


def check_font(font_config):
    """检查单个字体是否存在"""
    font_path = os.path.expanduser(font_config["path"])
    exists = os.path.exists(font_path)
    return {
        **font_config,
        "expanded_path": font_path,
        "exists": exists,
    }


def test_font_registration(font_path):
    """测试字体是否可以被reportlab注册"""
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        # 尝试直接注册TTF
        try:
            pdfmetrics.registerFont(TTFont("TestFont", font_path))
            return True, "TTF直接注册成功"
        except Exception:
            # 尝试注册TTC的第一个子字体
            try:
                pdfmetrics.registerFont(TTFont("TestFont", font_path, subfontIndex=0))
                return True, "TTC子字体注册成功"
            except Exception as e:
                return False, f"注册失败: {str(e)[:50]}"
    except ImportError:
        return None, "reportlab未安装"


def print_section(title):
    """打印分节标题"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def main():
    """主函数"""
    print_section("中文字体检测工具")

    # 检测平台
    current_platform = detect_platform()
    print(f"当前操作系统: {current_platform}")
    print(f"Python版本: {sys.version.split()[0]}")

    # 检查reportlab
    try:
        import reportlab
        print(f"ReportLab版本: {reportlab.Version}")
    except ImportError:
        print("⚠ ReportLab未安装，跳过字体注册测试")
        print("   安装命令: pip3 install reportlab")

    # 检测所有字体
    print_section("字体检测结果")

    available_fonts = []
    recommended_fonts = []

    for font_config in FONT_CONFIGS:
        result = check_font(font_config)

        # 只显示当前平台的字体（或已存在的字体）
        if result["platform"] == current_platform or result["exists"]:
            status_icon = "✅" if result["exists"] else "❌"
            rec_icon = "⭐" if result["recommended"] else "  "

            print(f"{status_icon} {rec_icon} {result['name']}")
            print(f"   平台: {result['platform']} | 类型: {result['type']}")
            print(f"   路径: {result['expanded_path']}")

            if result["exists"]:
                available_fonts.append(result)
                if result["recommended"]:
                    recommended_fonts.append(result)
            print()

    # 统计信息
    print_section("检测统计")

    total_count = len([f for f in FONT_CONFIGS if f["platform"] == current_platform])
    available_count = len(available_fonts)
    recommended_count = len(recommended_fonts)

    print(f"当前平台({current_platform})字体总数: {total_count}")
    print(f"可用字体数量: {available_count}")
    print(f"推荐字体数量: {recommended_count}")

    # 推荐
    if recommended_fonts:
        print_section("推荐使用的字体")
        for font in recommended_fonts[:3]:  # 只显示前3个
            print(f"⭐ {font['name']}")
            print(f"   路径: {font['expanded_path']}")

    # 测试字体注册
    if available_fonts:
        print_section("字体注册测试")
        for font in available_fonts[:3]:  # 只测试前3个
            success, message = test_font_registration(font["expanded_path"])
            if success is True:
                print(f"✅ {font['name']}: {message}")
            elif success is False:
                print(f"⚠ {font['name']}: {message}")
            else:
                print(f"⊘ {font['name']}: {message}")
            break  # 只测试第一个可用字体

    # 建议
    print_section("建议")

    if available_count == 0:
        print("❌ 未找到可用的中文字体！")
        print("\n安装建议:")
        if current_platform == "macOS":
            print("  1. 确保系统已安装PingFang SC字体")
            print("  2. 或从系统字体目录复制STHeiti到用户目录")
        elif current_platform == "Linux":
            print("  1. sudo apt-get install fonts-wqy-microhei")
            print("  2. sudo apt-get install fonts-wqy-zenhei")
        elif current_platform == "Windows":
            print("  1. 确保系统已安装Microsoft YaHei字体")
            print("  2. 或从网上下载SimSun字体")
    else:
        print("✅ 系统已安装中文字体，PDF生成应该正常")
        if recommended_count < available_count:
            print(f"\n💡 提示: 当前有{available_count}个字体可用，建议优先使用推荐字体")


if __name__ == "__main__":
    main()
