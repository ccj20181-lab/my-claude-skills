#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Templates Utility - 模板渲染工具

提供视频模板的渲染和代码生成功能
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional


# 视频模板配置
VIDEO_TEMPLATES = {
    "knowledge": {
        "name": "金融小知识科普",
        "description": "概念科普类内容，如'什么是IPO'、'什么是期货'",
        "structure": [
            {"type": "title", "name": "开场标题", "duration_range": (3, 5)},
            {"type": "content", "name": "概念解释", "duration_range": (10, 15)},
            {"type": "content", "name": "举例说明", "duration_range": (10, 15)},
            {"type": "summary", "name": "关键要点", "duration_range": (8, 12)},
            {"type": "ending", "name": "结尾引导", "duration_range": (2, 3)}
        ],
        "total_duration": (30, 50)
    },
    "hotspot": {
        "name": "财经热点解读",
        "description": "时效性财经新闻解读，如'英伟达市值破万亿'",
        "structure": [
            {"type": "title", "name": "热点引入", "duration_range": (3, 5)},
            {"type": "content", "name": "事件解读", "duration_range": (15, 20)},
            {"type": "content", "name": "影响分析", "duration_range": (15, 20)},
            {"type": "content", "name": "投资启示", "duration_range": (10, 15)},
            {"type": "ending", "name": "结尾", "duration_range": (2, 3)}
        ],
        "total_duration": (45, 65)
    },
    "breakdown": {
        "name": "概念拆解",
        "description": "三段式分析，如'房贷新政：是什么、为什么、怎么看'",
        "structure": [
            {"type": "title", "name": "开场", "duration_range": (3, 5)},
            {"type": "content", "name": "是什么", "duration_range": (15, 20)},
            {"type": "content", "name": "为什么", "duration_range": (15, 20)},
            {"type": "content", "name": "怎么办", "duration_range": (15, 20)},
            {"type": "ending", "name": "结尾", "duration_range": (2, 3)}
        ],
        "total_duration": (50, 70)
    }
}


def get_template(template_type: str) -> Optional[Dict]:
    """获取模板配置"""
    return VIDEO_TEMPLATES.get(template_type)


def list_templates() -> List[Dict]:
    """列出所有可用模板"""
    return [
        {
            "type": template_type,
            "name": config["name"],
            "description": config["description"],
            "scene_count": len(config["structure"]),
            "duration": f"{config['total_duration'][0]}-{config['total_duration'][1]}秒"
        }
        for template_type, config in VIDEO_TEMPLATES.items()
    ]


def generate_scene_config(
    template_type: str,
    title: str,
    fps: int = 30
) -> Dict[str, Any]:
    """
    根据模板生成场景配置

    Args:
        template_type: 模板类型
        title: 视频标题
        fps: 帧率

    Returns:
        场景配置字典
    """
    template = get_template(template_type)
    if not template:
        raise ValueError(f"未知模板类型: {template_type}")

    scenes = []
    current_frame = 0

    for i, scene_def in enumerate(template["structure"]):
        # 使用中间值作为默认时长
        min_dur, max_dur = scene_def["duration_range"]
        duration_seconds = (min_dur + max_dur) // 2
        duration_frames = duration_seconds * fps

        scene = {
            "id": f"scene_{i+1:02d}",
            "type": scene_def["type"],
            "name": scene_def["name"],
            "start_frame": current_frame,
            "duration_frames": duration_frames,
            "duration_seconds": duration_seconds,
            "content": {},
            "background": {
                "prompt": "",  # 待用户填充
                "style": "modern"
            }
        }
        scenes.append(scene)
        current_frame += duration_frames

    total_seconds = current_frame // fps

    return {
        "title": title,
        "type": template_type,
        "template_name": template["name"],
        "duration_seconds": total_seconds,
        "resolution": {"width": 1080, "height": 1440},
        "fps": fps,
        "scenes": scenes
    }


def render_remotion_scenes(manifest: Dict) -> str:
    """
    根据资源清单生成 Remotion 场景代码

    Args:
        manifest: 资源清单字典

    Returns:
        TypeScript 代码字符串
    """
    scenes = manifest.get("scenes", [])

    scene_objects = []
    for scene in scenes:
        scene_obj = f'''  {{
    id: "{scene.get('id', 'unknown')}",
    image: "{scene.get('image', '')}",
    startFrame: {scene.get('startFrame', 0)},
    durationFrames: {scene.get('durationFrames', 150)},
    text: "{scene.get('content', {}).get('text', '')}"
  }}'''
        scene_objects.append(scene_obj)

    scenes_code = ",\n".join(scene_objects)

    return f'''// 自动生成的场景配置
// 生成时间: {manifest.get('generated_at', 'unknown')}
// 视频标题: {manifest.get('title', 'unknown')}

interface Scene {{
  id: string;
  image: string;
  startFrame: number;
  durationFrames: number;
  text?: string;
}}

export const scenes: Scene[] = [
{scenes_code}
];

export const videoConfig = {{
  title: "{manifest.get('title', '')}",
  type: "{manifest.get('type', 'knowledge')}",
  fps: {manifest.get('fps', 30)},
  width: {manifest.get('resolution', {}).get('width', 1080)},
  height: {manifest.get('resolution', {}).get('height', 1440)},
  durationSeconds: {manifest.get('duration_seconds', 30)}
}};
'''


def save_scenes_config(config: Dict, output_path: Path) -> str:
    """保存场景配置到 JSON 文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    return str(output_path)


def load_manifest(manifest_path: Path) -> Dict:
    """加载资源清单"""
    with open(manifest_path, 'r', encoding='utf-8') as f:
        return json.load(f)
