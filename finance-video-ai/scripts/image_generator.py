#!/usr/bin/env python3
"""
财经视频AI生成器 - AI图片生成模块
使用 Gemini API (via API易) 生成极简手绘简笔画风格图片

优化特性：
- 重试机制：失败自动重试最多3次
- 并行生成：多图同时生成加速
- 缓存机制：基于 prompt hash 避免重复生成
- 更好的错误处理和降级策略
"""
import asyncio
import base64
import hashlib
import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import aiohttp
import requests

from config import image_config
from content_generator import Scene


# 统一的风格约束前缀（基于参考视频分析）
STYLE_PREFIX = """极简手绘简笔画风格要求：
- 纯白色背景(#FFFFFF)，无任何渐变或纹理
- 黑色细线条(1-2px)，线条有手绘的随意感和轻微抖动
- 简笔人物：圆形头部 + 线条身体，无面部细节
- 用符号表达情绪（问号、感叹号、星星等）
- 大量留白，元素居中构图
- 无阴影、无填充色、无背景装饰
- 类似儿童涂鸦或表情包的随意感

请根据以下场景描述，生成一张符合上述风格的插画："""


# 全局缓存目录（优先使用 Codex 目录，兼容 Claude 目录）
_cache_base_candidates = [
    Path.home() / ".codex" / "cache",
    Path.home() / ".claude" / "cache",
]
_cache_base = next((p for p in _cache_base_candidates if p.exists()), _cache_base_candidates[0])
CACHE_DIR = _cache_base / "finance-video-ai" / "images"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_prompt_hash(prompt: str) -> str:
    """生成 prompt 的 hash 用于缓存"""
    return hashlib.md5(prompt.encode('utf-8')).hexdigest()


def get_cached_image(prompt: str) -> Optional[Path]:
    """检查缓存中是否有对应的图片"""
    prompt_hash = get_prompt_hash(prompt)
    cached_path = CACHE_DIR / f"{prompt_hash}.png"
    if cached_path.exists():
        return cached_path
    return None


def save_to_cache(prompt: str, image_path: Path) -> None:
    """保存生成的图片到缓存"""
    prompt_hash = get_prompt_hash(prompt)
    cached_path = CACHE_DIR / f"{prompt_hash}.png"
    # 复制到缓存目录
    import shutil
    shutil.copy2(image_path, cached_path)


@dataclass
class GenerationResult:
    """图片生成结果"""
    scene_id: str
    success: bool
    path: Optional[str] = None
    error: Optional[str] = None
    from_cache: bool = False


class AIImageGenerator:
    """使用Gemini API生成极简手绘简笔画风格图片"""

    def __init__(self, max_retries: int = 3, parallel: bool = True):
        """
        初始化图片生成器

        Args:
            max_retries: 最大重试次数（默认3次）
            parallel: 是否使用并行生成（默认开启）
        """
        if not image_config.is_configured:
            raise ValueError("图片生成 API 未配置，请设置 NANO_BANANA_API_KEY 和 NANO_BANANA_API_URL")

        self.api_url = image_config.api_url
        self.api_key = image_config.api_key
        self.timeout = image_config.timeout
        self.max_retries = max_retries
        self.parallel = parallel

    def generate(self, prompt: str, output_path: Path, use_cache: bool = True) -> bool:
        """
        生成单张图片（同步版本，带重试）

        Args:
            prompt: 场景描述（不包含风格约束）
            output_path: 输出路径
            use_cache: 是否使用缓存

        Returns:
            是否成功
        """
        # 检查缓存
        if use_cache:
            cached_path = get_cached_image(prompt)
            if cached_path:
                print(f"    ✓ 使用缓存")
                output_path.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(cached_path, output_path)
                return True

        # 添加统一风格前缀
        full_prompt = f"{STYLE_PREFIX}\n\n场景内容：{prompt}"

        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"]
            }
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        last_error = None
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    print(f"    🔄 重试 {attempt + 1}/{self.max_retries}...")

                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()

                # 提取图片数据
                for candidate in data.get("candidates", []):
                    for part in candidate.get("content", {}).get("parts", []):
                        if "inlineData" in part:
                            img_data = part["inlineData"].get("data", "")
                            mime_type = part["inlineData"].get("mimeType", "image/png")

                            if img_data:
                                output_path.parent.mkdir(parents=True, exist_ok=True)
                                output_path.write_bytes(base64.b64decode(img_data))

                                # 保存到缓存
                                if use_cache:
                                    save_to_cache(prompt, output_path)

                                return True

                # 如果没有找到图片数据
                last_error = "响应中没有图片数据"

            except requests.exceptions.Timeout:
                last_error = f"请求超时 (尝试 {attempt + 1}/{self.max_retries})"
            except requests.exceptions.RequestException as e:
                last_error = f"请求失败: {e}"
            except Exception as e:
                last_error = f"图片生成失败: {e}"

            # 如果不是最后一次尝试，等待一下再重试
            if attempt < self.max_retries - 1:
                import time
                time.sleep(1 * (attempt + 1))  # 指数退避: 1s, 2s

        # 所有重试都失败
        print(f"    ✗ 生成失败: {last_error}")
        return False

    async def generate_async(self, session: aiohttp.ClientSession, prompt: str, output_path: Path, use_cache: bool = True) -> bool:
        """
        生成单张图片（异步版本，带重试）

        Args:
            session: aiohttp 会话
            prompt: 场景描述
            output_path: 输出路径
            use_cache: 是否使用缓存

        Returns:
            是否成功
        """
        # 检查缓存
        if use_cache:
            cached_path = get_cached_image(prompt)
            if cached_path:
                print(f"    ✓ 使用缓存")
                output_path.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(cached_path, output_path)
                return True

        # 添加统一风格前缀
        full_prompt = f"{STYLE_PREFIX}\n\n场景内容：{prompt}"

        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"]
            }
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        last_error = None
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    print(f"    🔄 重试 {attempt + 1}/{self.max_retries}...")

                timeout = aiohttp.ClientTimeout(total=self.timeout)
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=timeout
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    # 提取图片数据
                    for candidate in data.get("candidates", []):
                        for part in candidate.get("content", {}).get("parts", []):
                            if "inlineData" in part:
                                img_data = part["inlineData"].get("data", "")
                                mime_type = part["inlineData"].get("mimeType", "image/png")

                                if img_data:
                                    output_path.parent.mkdir(parents=True, exist_ok=True)
                                    output_path.write_bytes(base64.b64decode(img_data))

                                    # 保存到缓存
                                    if use_cache:
                                        save_to_cache(prompt, output_path)

                                    return True

                    last_error = "响应中没有图片数据"

            except asyncio.TimeoutError:
                last_error = f"请求超时 (尝试 {attempt + 1}/{self.max_retries})"
            except aiohttp.ClientError as e:
                last_error = f"请求失败: {e}"
            except Exception as e:
                last_error = f"图片生成失败: {e}"

            # 如果不是最后一次尝试，等待一下再重试
            if attempt < self.max_retries - 1:
                await asyncio.sleep(1 * (attempt + 1))  # 指数退避

        print(f"    ✗ 生成失败: {last_error}")
        return False

    def generate_batch(
        self,
        scenes: List[Scene],
        output_dir: Path,
        use_cache: bool = True,
        max_concurrent: int = 3
    ) -> Dict[str, str]:
        """
        批量生成场景插画（支持并行）

        Args:
            scenes: 场景列表
            output_dir: 输出目录
            use_cache: 是否使用缓存
            max_concurrent: 最大并发数

        Returns:
            {scene_id: relative_path} 映射
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        results = {}

        total = len(scenes)
        print(f"  📦 开始生成 {total} 张图片 (并发数: {max_concurrent})")

        if self.parallel and total > 1:
            # 使用异步并行生成
            try:
                # 尝试获取当前 event loop
                loop = asyncio.get_running_loop()
                # 如果已经有 running loop，创建新任务
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(
                        asyncio.run,
                        self._generate_parallel(scenes, output_dir, use_cache, max_concurrent)
                    )
                    results = future.result()
            except RuntimeError:
                # 没有 running loop，可以安全使用 asyncio.run
                results = asyncio.run(self._generate_parallel(scenes, output_dir, use_cache, max_concurrent))
        else:
            # 串行生成
            results = self._generate_sequential(scenes, output_dir, use_cache)

        return results

    def _generate_sequential(
        self,
        scenes: List[Scene],
        output_dir: Path,
        use_cache: bool
    ) -> Dict[str, str]:
        """串行生成（带进度显示）"""
        results = {}
        total = len(scenes)

        for i, scene in enumerate(scenes, 1):
            print(f"  [{i}/{total}] 生成插画: {scene.id}")
            print(f"      描述: {scene.image_prompt[:50]}...")

            output_path = output_dir / f"{scene.id}.png"

            if self.generate(scene.image_prompt, output_path, use_cache):
                results[scene.id] = f"images/{scene.id}.png"
                print(f"      ✓ 成功")
            else:
                # 失败时创建占位图
                self._create_placeholder(output_path, scene.image_prompt)
                results[scene.id] = f"images/{scene.id}.png"
                print(f"      ⚠ 使用占位图")

        return results

    async def _generate_parallel(
        self,
        scenes: List[Scene],
        output_dir: Path,
        use_cache: bool,
        max_concurrent: int
    ) -> Dict[str, str]:
        """并行生成（使用 asyncio）"""
        results = {}
        total = len(scenes)

        # 创建信号量控制并发数
        semaphore = asyncio.Semaphore(max_concurrent)

        async def generate_with_semaphore(session: aiohttp.ClientSession, scene: Scene, index: int):
            async with semaphore:
                print(f"  [{index}/{total}] 生成插画: {scene.id}")
                print(f"      描述: {scene.image_prompt[:50]}...")

                output_path = output_dir / f"{scene.id}.png"

                success = await self.generate_async(session, scene.image_prompt, output_path, use_cache)

                if success:
                    results[scene.id] = f"images/{scene.id}.png"
                    print(f"      ✓ 成功")
                else:
                    self._create_placeholder(output_path, scene.image_prompt)
                    results[scene.id] = f"images/{scene.id}.png"
                    print(f"      ⚠ 使用占位图")

        # 创建异步任务
        timeout = aiohttp.ClientTimeout(total=self.timeout * self.max_retries)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = [
                generate_with_semaphore(session, scene, i)
                for i, scene in enumerate(scenes, 1)
            ]
            await asyncio.gather(*tasks, return_exceptions=True)

        return results

    def _create_placeholder(self, output_path: Path, prompt: str):
        """创建占位图（生成失败时使用）"""
        try:
            from PIL import Image, ImageDraw, ImageFont

            # 创建纯白背景
            img = Image.new('RGB', (1080, 1440), 'white')
            draw = ImageDraw.Draw(img)

            # 尝试使用系统字体
            try:
                font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 32)
            except:
                font = ImageFont.load_default()

            # 绘制边框
            draw.rectangle([50, 50, 1030, 1390], outline='black', width=2)

            # 绘制提示文字
            text = f"[AI Image Placeholder]\n\n{prompt[:100]}..."
            # 简单的文字居中
            lines = text.split('\n')
            y_offset = 600
            for line in lines:
                draw.text((540, y_offset), line, fill='black', anchor='mm', font=font)
                y_offset += 50

            img.save(output_path)

        except ImportError:
            # 如果没有PIL，创建一个空的PNG文件
            import struct
            import zlib

            # 最小有效PNG
            def create_minimal_png(width, height, color=(255, 255, 255)):
                def png_chunk(chunk_type, data):
                    chunk_len = len(data)
                    chunk = struct.pack('>I', chunk_len) + chunk_type + data
                    crc = zlib.crc32(chunk_type + data) & 0xffffffff
                    return chunk + struct.pack('>I', crc)

                raw_data = b''
                for y in range(height):
                    raw_data += b'\x00'  # filter type
                    for x in range(width):
                        raw_data += bytes(color)

                compressed = zlib.compress(raw_data, 9)

                png = b'\x89PNG\r\n\x1a\n'
                png += png_chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
                png += png_chunk(b'IDAT', compressed)
                png += png_chunk(b'IEND', b'')
                return png

            output_path.write_bytes(create_minimal_png(1080, 1440))

    def clear_cache(self) -> int:
        """清除图片缓存，返回清除的文件数量"""
        count = 0
        if CACHE_DIR.exists():
            for f in CACHE_DIR.iterdir():
                if f.is_file() and f.suffix == '.png':
                    f.unlink()
                    count += 1
        return count


if __name__ == "__main__":
    # 测试图片生成
    from content_generator import generate_script

    print("测试图片生成...")
    generator = AIImageGenerator(max_retries=3, parallel=True)

    # 测试单个场景
    test_scene = Scene(
        id="test_01",
        type="hook",
        text="测试文本",
        duration=10,
        visual_action="circle",
        image_prompt="一个简笔人物好奇地看着前方，头顶有大大的问号"
    )

    output_path = Path("test_output.png")
    if generator.generate(test_scene.image_prompt, output_path):
        print(f"✓ 测试图片已生成: {output_path}")
    else:
        print("✗ 测试失败")
