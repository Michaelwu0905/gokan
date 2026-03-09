#!/usr/bin/env python3
"""
测试脚本：验证 FastAPI 后端服务
使用一张本地图片测试 /api/analyze 接口
"""

import os
import sys
import base64
import requests
from pathlib import Path


def create_test_image():
    """创建一个包含日文的测试图片"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # 创建一个白色背景的图片
        img = Image.new("RGB", (400, 200), color="white")
        draw = ImageDraw.Draw(img)

        # 尝试加载字体（如果有的话）
        try:
            # macOS 上的日文字体
            font = ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", 40)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 40)
            except:
                font = ImageFont.load_default()

        # 绘制日文文本
        text = "こんにちは"
        draw.text((50, 70), text, fill="black", font=font)

        # 保存图片
        test_image_path = Path(__file__).parent / "test_image.png"
        img.save(test_image_path)
        print(f"✅ 测试图片已创建: {test_image_path}")
        return str(test_image_path)

    except ImportError:
        print("⚠️  需要安装 Pillow 来创建测试图片")
        print("   运行: uv pip install Pillow")
        return None


def test_health_endpoint():
    """测试健康检查端点"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保服务已启动")
        print("   运行: python -m backend.main")
        return False


def test_analyze_endpoint(image_path: str):
    """测试分析端点"""
    # 读取图片并转为 base64
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()

    # 添加 data URI 前缀
    image_base64 = f"data:image/png;base64,{image_data}"

    # 发送请求
    payload = {"image_base64": image_base64, "context": ""}

    try:
        print("\n📤 发送分析请求...")
        response = requests.post("http://127.0.0.1:8000/api/analyze", json=payload, timeout=60)

        if response.status_code == 200:
            result = response.json()
            print("\n✅ 分析成功!")
            print("\n📊 结果:")
            print(f"   状态: {result['status']}")

            if result["status"] == "success" and result.get("data"):
                data = result["data"]
                print(f"\n📝 原文: {data.get('original_text', 'N/A')}")
                print(f"🌐 翻译: {data.get('translation', 'N/A')}")
                print(f"🔤 注音: {data.get('furigana', 'N/A')}")
                print(f"\n📚 语法分析:")
                for item in data.get("grammar_analysis", []):
                    print(f"   - {item['word']}: {item['explanation']}")

                example = data.get("example_sentence", {})
                print(f"\n💬 例句:")
                print(f"   日文: {example.get('japanese', 'N/A')}")
                print(f"   中文: {example.get('chinese', 'N/A')}")
            else:
                print(f"❌ 错误: {result.get('error', 'Unknown error')}")

            return True
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 请求出错: {e}")
        return False


def main():
    print("=" * 60)
    print("Japanese Learning Assistant - 后端测试")
    print("=" * 60)

    # 测试健康检查
    print("\n🏥 测试健康检查端点...")
    if not test_health_endpoint():
        sys.exit(1)

    # 创建测试图片
    print("\n🎨 创建测试图片...")
    test_image_path = create_test_image()

    if test_image_path and os.path.exists(test_image_path):
        # 测试分析端点
        print("\n🔍 测试分析端点...")
        test_analyze_endpoint(test_image_path)
    else:
        print("\n⚠️  跳过分析测试（需要手动准备测试图片）")
        print("   准备一张包含日文的图片，命名为 'test_japanese.png' 放在项目根目录")

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
