#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Project - 创建 3:4 竖屏 Remotion 项目

专为秒懂金融视频设计，默认配置：
- 分辨率：1080×1440（3:4竖屏）
- 帧率：30fps
- 自动创建 public/scenes 目录
"""
import sys
import io
import os
import argparse
import subprocess
import json
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 默认配置
DEFAULT_PATH = str(Path.home() / "miaodong-videos")
DEFAULT_WIDTH = 1080
DEFAULT_HEIGHT = 1440
DEFAULT_FPS = 30

# 模板类型
TEMPLATES = {
    "knowledge": "金融小知识科普",
    "hotspot": "财经热点解读",
    "breakdown": "概念拆解"
}


def create_remotion_project(name: str, path: str) -> Path:
    """
    使用 npx create-video 创建 Remotion 项目

    Args:
        name: 项目名称
        path: 项目父目录

    Returns:
        项目路径
    """
    project_path = Path(path) / name

    if project_path.exists():
        print(f"⚠️ 项目已存在: {project_path}")
        return project_path

    # 创建父目录
    Path(path).mkdir(parents=True, exist_ok=True)

    print(f"📦 正在创建 Remotion 项目: {name}")
    print(f"   路径: {project_path}")

    try:
        # 使用 npx create-video 创建项目
        # 使用 --template blank 创建空白项目，然后手动配置
        result = subprocess.run(
            ["npx", "create-video@latest", name, "--template", "blank"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            print(f"❌ 创建失败: {result.stderr}")
            # 如果 create-video 失败，手动创建基础结构
            print("📝 尝试手动创建项目结构...")
            create_manual_project(project_path)
        else:
            print(f"✅ Remotion 项目创建成功")

    except subprocess.TimeoutExpired:
        print(f"❌ 创建超时，尝试手动创建...")
        create_manual_project(project_path)
    except FileNotFoundError:
        print(f"⚠️ 未找到 npx，尝试手动创建项目结构...")
        create_manual_project(project_path)

    return project_path


def create_manual_project(project_path: Path) -> None:
    """手动创建项目基础结构"""
    project_path.mkdir(parents=True, exist_ok=True)

    # 创建 package.json
    package_json = {
        "name": project_path.name,
        "version": "1.0.0",
        "type": "module",
        "scripts": {
            "start": "remotion studio",
            "build": "remotion render src/index.ts MyVideo out/video.mp4",
            "preview": "remotion preview"
        },
        "dependencies": {
            "@remotion/cli": "^4.0.0",
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "remotion": "^4.0.0"
        },
        "devDependencies": {
            "@types/react": "^18.2.0",
            "typescript": "^5.0.0"
        }
    }
    (project_path / "package.json").write_text(
        json.dumps(package_json, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # 创建 tsconfig.json
    tsconfig = {
        "compilerOptions": {
            "target": "ES2022",
            "module": "ESNext",
            "moduleResolution": "bundler",
            "jsx": "react-jsx",
            "strict": true,
            "esModuleInterop": true,
            "skipLibCheck": true,
            "outDir": "dist"
        },
        "include": ["src/**/*"]
    }
    (project_path / "tsconfig.json").write_text(
        json.dumps(tsconfig, indent=2),
        encoding="utf-8"
    )

    print(f"  ✅ 手动创建项目结构完成")


def configure_video_settings(project_path: Path, width: int, height: int, fps: int) -> None:
    """
    配置视频参数为 3:4 竖屏

    Args:
        project_path: 项目路径
        width: 视频宽度
        height: 视频高度
        fps: 帧率
    """
    print(f"⚙️ 配置视频参数: {width}×{height} @ {fps}fps")

    # 创建 remotion.config.ts
    config_content = f'''import {{ Config }} from "@remotion/cli/config";

Config.setVideoImageFormat("png");

// 3:4 竖屏配置（秒懂金融视频）
export const videoConfig = {{
  width: {width},
  height: {height},
  fps: {fps},
  durationInFrames: 30 * {fps}, // 默认30秒
}};
'''
    config_path = project_path / "remotion.config.ts"
    config_path.write_text(config_content, encoding="utf-8")
    print(f"  ✅ 已创建 remotion.config.ts")


def create_src_structure(project_path: Path, template: str) -> None:
    """
    创建 src 目录结构

    Args:
        project_path: 项目路径
        template: 模板类型
    """
    src_path = project_path / "src"
    src_path.mkdir(parents=True, exist_ok=True)

    # 创建 Root.tsx - 主组件
    root_content = f'''import {{ Composition }} from "remotion";
import {{ MyVideo }} from "./MyVideo";

// 视频配置
const VIDEO_WIDTH = {DEFAULT_WIDTH};
const VIDEO_HEIGHT = {DEFAULT_HEIGHT};
const VIDEO_FPS = {DEFAULT_FPS};
const DURATION_SECONDS = 30;

export const RemotionRoot: React.FC = () => {{
  return (
    <>
      <Composition
        id="MyVideo"
        component={{MyVideo}}
        durationInFrames={{DURATION_SECONDS * VIDEO_FPS}}
        fps={{VIDEO_FPS}}
        width={{VIDEO_WIDTH}}
        height={{VIDEO_HEIGHT}}
      />
    </>
  );
}};
'''
    (src_path / "Root.tsx").write_text(root_content, encoding="utf-8")

    # 创建 MyVideo.tsx - 视频组件
    video_content = '''import { AbsoluteFill, Img, useCurrentFrame, useVideoConfig, staticFile } from "remotion";

// 场景类型定义
interface Scene {
  id: string;
  image: string;
  startFrame: number;
  durationFrames: number;
  text?: string;
}

// 场景配置（由 generate_scenes.py 生成的 manifest 填充）
const scenes: Scene[] = [
  {
    id: "placeholder",
    image: "scenes/placeholder.png",
    startFrame: 0,
    durationFrames: 150,
    text: "秒懂金融"
  }
];

export const MyVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  // 查找当前场景
  const currentScene = scenes.find(
    (scene) =>
      frame >= scene.startFrame &&
      frame < scene.startFrame + scene.durationFrames
  ) || scenes[0];

  // 计算场景内进度
  const sceneProgress =
    (frame - currentScene.startFrame) / currentScene.durationFrames;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#1a1a2e",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      {/* 背景图片 */}
      <Img
        src={staticFile(currentScene.image)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
        }}
      />

      {/* 文字覆盖层（可选） */}
      {currentScene.text && (
        <div
          style={{
            position: "absolute",
            bottom: 100,
            left: 0,
            right: 0,
            textAlign: "center",
            color: "white",
            fontSize: 48,
            fontWeight: "bold",
            textShadow: "2px 2px 4px rgba(0,0,0,0.5)",
            opacity: Math.min(1, sceneProgress * 3),
          }}
        >
          {currentScene.text}
        </div>
      )}
    </AbsoluteFill>
  );
};
'''
    (src_path / "MyVideo.tsx").write_text(video_content, encoding="utf-8")

    # 创建 index.ts - 入口文件
    index_content = '''import { registerRoot } from "remotion";
import { RemotionRoot } from "./Root";

registerRoot(RemotionRoot);
'''
    (src_path / "index.ts").write_text(index_content, encoding="utf-8")

    print(f"  ✅ 已创建 src 目录结构（模板: {TEMPLATES.get(template, template)}）")


def create_public_structure(project_path: Path) -> None:
    """创建 public 目录结构"""
    scenes_path = project_path / "public" / "scenes"
    scenes_path.mkdir(parents=True, exist_ok=True)

    # 创建占位图提示
    readme = """# 场景图片目录

此目录用于存放 AI 生成的场景图片。

使用 `generate_scenes.py` 脚本生成图片后，图片会自动保存到这里。

## 文件命名规范

- scene_01.png - 第1个场景
- scene_02.png - 第2个场景
- ...
- scenes-manifest.json - 资源清单

## 图片规格

- 分辨率: 1080×1440 (3:4 竖屏)
- 格式: PNG
"""
    (scenes_path / "README.md").write_text(readme, encoding="utf-8")

    print(f"  ✅ 已创建 public/scenes 目录")


def main():
    parser = argparse.ArgumentParser(
        description="创建 3:4 竖屏 Remotion 项目（秒懂金融视频）",
        epilog="示例:\\n"
               "  python3 scripts/create_project.py --name ipo-explainer\\n"
               "  python3 scripts/create_project.py --name ipo --path ~/videos --template hotspot",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--name", required=True, help="项目名称")
    parser.add_argument("--path", default=DEFAULT_PATH, help=f"项目路径 (默认: {DEFAULT_PATH})")
    parser.add_argument("--template", default="knowledge",
                        choices=list(TEMPLATES.keys()),
                        help="模板类型 (默认: knowledge)")

    args = parser.parse_args()

    print(f"\n🎬 秒懂金融视频项目创建器")
    print(f"{'=' * 40}")

    # 1. 创建 Remotion 项目
    project_path = create_remotion_project(args.name, args.path)

    # 2. 配置 3:4 竖屏参数
    configure_video_settings(project_path, DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_FPS)

    # 3. 创建 src 目录结构
    create_src_structure(project_path, args.template)

    # 4. 创建 public 目录结构
    create_public_structure(project_path)

    print(f"\n{'=' * 40}")
    print(f"✅ 项目创建完成: {project_path}")
    print(f"\n📋 下一步:")
    print(f"   1. cd {project_path}")
    print(f"   2. npm install")
    print(f"   3. 使用 generate_scenes.py 生成场景图片")
    print(f"   4. npx remotion studio  # 预览")
    print(f"   5. npx remotion render src/index.ts MyVideo out/video.mp4  # 渲染")

    return 0


if __name__ == "__main__":
    exit(main())
