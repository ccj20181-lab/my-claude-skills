# Notes: Remotion 视频效果优化审计

## 现状问题（用户反馈）
- 文案出现“上下两个框重复”。
- 文案样式不够美观，期望以字幕形式出现。
- 素材引用太少且太小。
- 火柴人体系不需要，改成简单人物形象。
- 动画效果太简单。

## 代码侧初步定位
- `remotion/src/components/Scene.tsx`
  - 同时渲染了 `TextBubble/TitleText` 与 `Captions`（且 `Captions` 使用同一份 `data.text`），会造成同屏重复。
  - 之前 icon 未渲染；已补渲染，但尺寸/数量仍不足。
  - 仍然渲染 `StickFigure`（火柴人 SVG/图片）。
- `remotion/src/components/Captions.tsx`
  - 主要为 word-level 高亮设计；当 `word_timestamps` 为空时只能整段显示，缺少节奏/排版控制。
- `scripts/main.py -> prepare_remotion_data()`
  - 目前每场景只注入 1 个 icon（主 icon），没有“辅助素材”概念。
  - `assets/characters/` 为空导致“缺少角色素材”告警，但渲染端其实并不依赖（可移除/弱化）。

## 优化方向（设计草案）
- 字幕系统：
  - 新增 `Subtitle.tsx`：支持无 timestamps 的“逐字 reveal”（按时长比例）+ 两行内排版 + 半透明底板。
  - Title 场景：显示 meta.title（大标题）+ scene.text（副标题），其他场景只显示字幕块。
- 素材系统：
  - 每场景：hero icon（更大）+ icon cloud（2-4 个，低透明漂浮）。
  - icon cloud 的 icon 列表由 Python 侧注入（避免运行时目录遍历）。
- 人物形象：
  - 新增 `HostAvatar.tsx`（纯 SVG），根据 `data.character.type` 切换表情。
  - Scene 中固定位置 + 轻微呼吸/点头。
- 动画：
  - icon 入场（spring + 轻微旋转），字幕入场（上滑 + 透明）。
  - 关键场景（hook/question/summary/cta）加 HandDraw 强调（underline/circle/arrow）。
  - 转场策略：不同 sceneType 选不同 TransitionType；避免全 fade。

## 验证清单
- 不重复文案（同屏只出现一处文案呈现）。
- 素材数量/大小符合预期。
- avatar 替代 stick figure 成功（视频中无 StickFigure）。
- 渲染 mp4 有音轨且非静音。

