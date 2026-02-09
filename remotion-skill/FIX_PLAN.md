# Remotion-Skill 修复计划

> 分析时间: 2026-02-09
> 分析人: 幽浮喵 (规划师)

---

## 问题概览

| # | 问题 | 严重程度 | 根本原因 |
|---|------|----------|----------|
| 1 | 音频无法播放 | 高 | 音频路径配置错误，未复制到 public 目录 |
| 2 | 素材图片未引用 | 高 | data.json 中 path 全为 null，素材目录结构不匹配 |
| 3 | 火柴人样式丑陋 | 中 | SVG 设计过于简陋，缺乏视觉吸引力 |
| 4 | 背景色不固定 | 低 | SCENE_STYLES 定义了不同场景的不同背景色 |

---

## 问题 1: 音频无法播放

### 根本原因分析

1. **音频路径问题**: 在 `Scene.tsx:132` 中使用 `staticFile(audioPath)`:
   ```tsx
   {audioPath && <Audio src={staticFile(audioPath)} />}
   ```

2. **staticFile 的工作原理**: Remotion 的 `staticFile()` 函数从 `public/` 目录读取文件

3. **当前数据**: `data.json` 中音频路径为 `"path": "audio/scene_01.mp3"`，但音频文件实际生成在 `output/audio/` 目录

4. **问题所在**:
   - 音频文件没有被复制到 `remotion/public/audio/` 目录
   - `main.py:188` 只生成了 `remotion/src/data.json`，没有处理音频文件的复制

### 修复方案

**文件**: `$HOME/.codex/skills/remotion-skill/scripts/main.py`

**修改内容**:

```python
# 在 prepare_remotion_data 函数中添加音频文件复制逻辑

import shutil

def prepare_remotion_data(
    script: VideoScript,
    audio_data: Optional[dict],
    assets: list,
    output_dir: Path
) -> Path:
    """Prepare data file for Remotion"""
    print("\n📦 准备 Remotion 数据...")

    # === 新增: 复制音频文件到 public 目录 ===
    public_audio_dir = REMOTION_DIR / "public" / "audio"
    public_audio_dir.mkdir(parents=True, exist_ok=True)

    if audio_data:
        source_audio_dir = output_dir / "audio"
        for scene_id, audio_info in audio_data.get("files", {}).items():
            source_path = output_dir / audio_info["path"]
            if source_path.exists():
                dest_path = public_audio_dir / f"{scene_id}.mp3"
                shutil.copy2(source_path, dest_path)
                print(f"  ✓ 复制音频: {scene_id}.mp3")
    # === 结束新增 ===

    # ... 其余代码保持不变
```

**额外修改**: 确保 `data.json` 中的音频路径正确:

```python
# 在 scene_data 中修改音频路径格式
if audio_data and scene.id in audio_data.get("files", {}):
    scene_data["audio"] = {
        "path": f"audio/{scene.id}.mp3",  # 相对于 public 目录
        "duration_ms": audio_data["files"][scene.id].get("duration_ms", 0),
        "word_timestamps": audio_data["files"][scene.id].get("word_timestamps")
    }
```

---

## 问题 2: 素材图片未引用

### 根本原因分析

1. **data.json 现状**: 所有 `character.path` 和 `icon.path` 都是 `null`:
   ```json
   "character": {
     "type": "surprised",
     "path": null
   },
   "icon": {
     "name": "stock_up",
     "path": null
   }
   ```

2. **素材目录结构问题**:
   - `config.py` 定义: `CHARACTERS_DIR = ASSETS_DIR / "characters"` 期望文件如 `thinking.png`
   - **实际情况**: `assets/characters/` 目录为空！
   - `assets/icons/` 存在大量白板手绘风格图标，但文件名格式为中文如 `IPO上市_白板手绘.png`

3. **asset_matcher.py 问题**:
   - `get_character_path()` 返回不存在的路径
   - `match_scene_assets()` 在第 67-68 行检查路径存在性，若不存在则返回 `None`

4. **StickFigure.tsx 逻辑**: 第 80-93 行，只有当 `imagePath` 存在时才使用图片，否则渲染 SVG

### 修复方案

#### 方案 A: 修复素材路径映射 (推荐)

**文件**: `$HOME/.codex/skills/remotion-skill/scripts/config.py`

```python
# 更新 ICONS 映射，使用实际存在的文件名
ICONS = {
    # 基于实际的 assets/icons 目录内容
    "stock_up": "股票投资_白板手绘.png",
    "chart": "K线图_白板手绘.png",
    "company": "办公楼_白板手绘.png",
    "money": "金币堆_白板手绘.png",
    "growth": "火箭上升_白板手绘.png",
    "yuan": "人民币符号_白板手绘.png",
    "certificate": "合同文件_白板手绘.png",
    "contract": "合同文件_白板手绘.png",
    "report": "财务报表_白板手绘.png",
    "risk": "风险管理_白板手绘.png",
    "trend": "股票投资_白板手绘.png",
    # ... 其他映射
}
```

#### 方案 B: 复制素材到 public 目录

**文件**: `$HOME/.codex/skills/remotion-skill/scripts/main.py`

在 `prepare_remotion_data` 函数中添加:

```python
# 复制素材到 public 目录
public_assets_dir = REMOTION_DIR / "public" / "assets"

# 复制角色素材
for asset in assets:
    if asset.character_path and asset.character_path.exists():
        dest_dir = public_assets_dir / "characters"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / asset.character_path.name
        shutil.copy2(asset.character_path, dest_path)

    if asset.icon_path and asset.icon_path.exists():
        dest_dir = public_assets_dir / "icons"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / asset.icon_path.name
        shutil.copy2(asset.icon_path, dest_path)
```

**同时修改 data.json 生成逻辑**:

```python
scene_data = {
    "id": scene.id,
    "type": scene.type,
    "text": scene.text,
    "duration": duration,
    "character": {
        "type": scene.character,
        "path": f"assets/characters/{asset.character_path.name}" if asset.character_path else None
    },
    "icon": {
        "name": asset.icon_name,
        "path": f"assets/icons/{asset.icon_path.name}" if asset.icon_path else None
    } if asset.icon_name else None
}
```

---

## 问题 3: 火柴人样式丑陋

### 根本原因分析

1. **当前实现**: `StickFigure.tsx` 中的 `StickFigureSVG` 组件使用极简的线条绘制
   - 单色 (`#2D3748`) 灰色线条
   - 固定 4px 笔画宽度
   - 表情过于简单（仅眼睛和嘴巴）

2. **设计问题**:
   - 没有填充色彩
   - 没有圆润的关节
   - 没有动态感
   - 头身比例不协调（头太小）

### 修复方案

**文件**: `$HOME/.codex/skills/remotion-skill/remotion/src/components/StickFigure.tsx`

完全重新设计 SVG 火柴人，采用更现代、可爱的风格:

```tsx
const StickFigureSVG: React.FC<{ type: string; size: number }> = ({
  type,
  size,
}) => {
  // 使用更友好的配色
  const primaryColor = "#2D3748";
  const secondaryColor = "#4A5568";
  const skinColor = "#FEE2B3";
  const cheekColor = "#FFCACA";
  const strokeWidth = 5;

  // 表情映射
  const expressions: Record<string, React.ReactNode> = {
    happy: (
      <>
        {/* 开心的眼睛 - 弯弯的 */}
        <path d="M 32 38 Q 38 32 44 38" stroke={primaryColor} strokeWidth={3} fill="none" strokeLinecap="round" />
        <path d="M 56 38 Q 62 32 68 38" stroke={primaryColor} strokeWidth={3} fill="none" strokeLinecap="round" />
        {/* 开心的嘴巴 */}
        <path d="M 38 52 Q 50 65 62 52" stroke={primaryColor} strokeWidth={3} fill="none" strokeLinecap="round" />
        {/* 腮红 */}
        <ellipse cx="30" cy="48" rx="6" ry="4" fill={cheekColor} opacity="0.6" />
        <ellipse cx="70" cy="48" rx="6" ry="4" fill={cheekColor} opacity="0.6" />
      </>
    ),
    thinking: (
      <>
        {/* 思考的眼睛 */}
        <circle cx="38" cy="38" r="4" fill={primaryColor} />
        <circle cx="62" cy="38" r="4" fill={primaryColor} />
        {/* 思考的嘴 - 歪歪的 */}
        <path d="M 42 55 Q 50 52 58 55" stroke={primaryColor} strokeWidth={3} fill="none" strokeLinecap="round" />
        {/* 思考泡泡 */}
        <circle cx="82" cy="15" r="4" fill={secondaryColor} opacity="0.5" />
        <circle cx="88" cy="8" r="6" fill={secondaryColor} opacity="0.5" />
        <circle cx="96" cy="0" r="8" fill={secondaryColor} opacity="0.5" />
      </>
    ),
    confused: (
      <>
        {/* 困惑的眼睛 */}
        <circle cx="38" cy="38" r="4" fill={primaryColor} />
        <circle cx="62" cy="38" r="4" fill={primaryColor} />
        {/* 一边眉毛抬起 */}
        <path d="M 30 30 Q 38 26 46 30" stroke={primaryColor} strokeWidth={2} fill="none" />
        <path d="M 54 32 Q 62 30 70 32" stroke={primaryColor} strokeWidth={2} fill="none" />
        {/* 困惑的嘴 */}
        <path d="M 40 55 Q 45 52 50 55 Q 55 58 60 55" stroke={primaryColor} strokeWidth={3} fill="none" strokeLinecap="round" />
        {/* 问号 */}
        <text x="78" y="25" fontSize="20" fontWeight="bold" fill={primaryColor}>?</text>
      </>
    ),
    surprised: (
      <>
        {/* 惊讶的大眼睛 */}
        <circle cx="38" cy="38" r="6" fill="white" stroke={primaryColor} strokeWidth={2} />
        <circle cx="38" cy="38" r="3" fill={primaryColor} />
        <circle cx="62" cy="38" r="6" fill="white" stroke={primaryColor} strokeWidth={2} />
        <circle cx="62" cy="38" r="3" fill={primaryColor} />
        {/* O形嘴巴 */}
        <ellipse cx="50" cy="55" rx="8" ry="10" fill="white" stroke={primaryColor} strokeWidth={3} />
      </>
    ),
    pointing: (
      <>
        {/* 自信的眼睛 */}
        <circle cx="38" cy="38" r="4" fill={primaryColor} />
        <circle cx="62" cy="38" r="4" fill={primaryColor} />
        {/* 微笑 */}
        <path d="M 42 52 Q 50 58 58 52" stroke={primaryColor} strokeWidth={3} fill="none" strokeLinecap="round" />
      </>
    ),
    waving: (
      <>
        {/* 友好的眼睛 */}
        <path d="M 32 38 Q 38 32 44 38" stroke={primaryColor} strokeWidth={3} fill="none" strokeLinecap="round" />
        <path d="M 56 38 Q 62 32 68 38" stroke={primaryColor} strokeWidth={3} fill="none" strokeLinecap="round" />
        {/* 开心大嘴 */}
        <path d="M 35 50 Q 50 68 65 50" stroke={primaryColor} strokeWidth={3} fill="none" strokeLinecap="round" />
        {/* 腮红 */}
        <ellipse cx="28" cy="48" rx="6" ry="4" fill={cheekColor} opacity="0.6" />
        <ellipse cx="72" cy="48" rx="6" ry="4" fill={cheekColor} opacity="0.6" />
      </>
    ),
    neutral: (
      <>
        <circle cx="38" cy="38" r="4" fill={primaryColor} />
        <circle cx="62" cy="38" r="4" fill={primaryColor} />
        <line x1="42" y1="55" x2="58" y2="55" stroke={primaryColor} strokeWidth={3} strokeLinecap="round" />
      </>
    ),
  };

  const expression = expressions[type] || expressions.neutral;

  // 手臂姿势
  const getArms = () => {
    switch (type) {
      case "pointing":
        return (
          <>
            {/* 指向的手臂 */}
            <path d="M 50 90 Q 30 85 15 75" stroke={primaryColor} strokeWidth={strokeWidth} fill="none" strokeLinecap="round" />
            <path d="M 50 90 Q 75 75 95 60" stroke={primaryColor} strokeWidth={strokeWidth} fill="none" strokeLinecap="round" />
            {/* 指向的手指 */}
            <circle cx="95" cy="60" r="4" fill={skinColor} stroke={primaryColor} strokeWidth={2} />
          </>
        );
      case "waving":
        return (
          <>
            <path d="M 50 90 Q 30 85 15 95" stroke={primaryColor} strokeWidth={strokeWidth} fill="none" strokeLinecap="round" />
            <path d="M 50 90 Q 70 70 85 50" stroke={primaryColor} strokeWidth={strokeWidth} fill="none" strokeLinecap="round" />
            {/* 挥动的手 */}
            <ellipse cx="88" cy="48" rx="8" ry="10" fill={skinColor} stroke={primaryColor} strokeWidth={2} />
          </>
        );
      default:
        return (
          <>
            <path d="M 50 90 Q 30 95 20 105" stroke={primaryColor} strokeWidth={strokeWidth} fill="none" strokeLinecap="round" />
            <path d="M 50 90 Q 70 95 80 105" stroke={primaryColor} strokeWidth={strokeWidth} fill="none" strokeLinecap="round" />
          </>
        );
    }
  };

  return (
    <svg viewBox="0 0 100 160" width={size} height={size * 1.6}>
      {/* 头部 - 更大更圆润 */}
      <circle cx="50" cy="40" r="30" fill={skinColor} stroke={primaryColor} strokeWidth={strokeWidth} />

      {/* 表情 */}
      {expression}

      {/* 身体 - 圆润的线条 */}
      <path
        d="M 50 70 Q 50 100 50 120"
        stroke={primaryColor}
        strokeWidth={strokeWidth}
        fill="none"
        strokeLinecap="round"
      />

      {/* 手臂 */}
      {getArms()}

      {/* 腿部 - 更自然的姿势 */}
      <path d="M 50 120 Q 40 140 35 155" stroke={primaryColor} strokeWidth={strokeWidth} fill="none" strokeLinecap="round" />
      <path d="M 50 120 Q 60 140 65 155" stroke={primaryColor} strokeWidth={strokeWidth} fill="none" strokeLinecap="round" />
    </svg>
  );
};
```

### 设计改进点

1. **添加肤色填充** - 使用温暖的米色 `#FEE2B3`
2. **添加腮红效果** - 使用粉色椭圆增加可爱感
3. **圆润的线条** - 使用 `strokeLinecap="round"` 和贝塞尔曲线
4. **更大的头部** - 头身比从 1:3 调整为 1:2，更卡通
5. **丰富的表情** - 每种表情有独特的眼睛、嘴巴和附加元素
6. **动态手势** - pointing 和 waving 有明显的手部细节

---

## 问题 4: 背景色不固定

### 根本原因分析

1. **当前实现**: `Scene.tsx:100-102` 使用场景类型对应的背景色:
   ```tsx
   <AbsoluteFill
     style={{
       backgroundColor: sceneStyle.backgroundColor,
     }}
   >
   ```

2. **SCENE_STYLES 定义** (`types/scene.ts:66-116`):
   - `hook`: `#FFFDF7` (暖白色)
   - `title`: `#FFFFFF` (纯白)
   - `question`: `#FFF5F5` (淡红)
   - `explain`: `#FFFFFF` (纯白)
   - `analogy`: `#F0FFF4` (淡绿)
   - ... 等等，每种场景不同颜色

3. **设计意图冲突**:
   - 原设计想通过颜色区分场景类型
   - 但用户需求是纯白背景

### 修复方案

**方案 A: 直接修改 (推荐)**

**文件**: `$HOME/.codex/skills/remotion-skill/remotion/src/components/Scene.tsx`

```tsx
// 第 97-103 行修改为:
return (
  <Transition type="fade" duration={10}>
    <AbsoluteFill
      style={{
        backgroundColor: "#FFFFFF",  // 固定纯白背景
      }}
    >
```

**方案 B: 修改主题配置**

**文件**: `$HOME/.codex/skills/remotion-skill/remotion/src/types/scene.ts`

将所有 `backgroundColor` 统一为 `#FFFFFF`:

```typescript
export const SCENE_STYLES: Record<SceneType, {
  backgroundColor: string;
  accentColor: string;
  textSize: number;
}> = {
  hook: {
    backgroundColor: "#FFFFFF",  // 改为纯白
    accentColor: "#FF6B35",
    textSize: 48,
  },
  title: {
    backgroundColor: "#FFFFFF",
    accentColor: "#2D3748",
    textSize: 64,
  },
  // ... 所有其他场景类型的 backgroundColor 都改为 "#FFFFFF"
};
```

**方案 C: 添加主题配置开关**

**文件**: `$HOME/.codex/skills/remotion-skill/remotion/src/theme/whiteboard.ts`

```typescript
export const whiteboardTheme = {
  colors: {
    background: "#FFFFFF",  // 确保是纯白
    useUniformBackground: true,  // 新增: 是否使用统一背景
    // ...
  },
  // ...
};
```

然后在 `Scene.tsx` 中:

```tsx
const backgroundColor = whiteboardTheme.colors.useUniformBackground
  ? whiteboardTheme.colors.background
  : sceneStyle.backgroundColor;
```

---

## 修复优先级与实施顺序

### 第一阶段: 核心功能修复

1. **音频问题** (问题 1) - 高优先级
   - 修改 `main.py` 添加音频复制逻辑
   - 确保路径正确性

2. **素材引用问题** (问题 2) - 高优先级
   - 更新 `config.py` 中的 ICONS 映射
   - 修改 `main.py` 添加素材复制逻辑
   - 确保 data.json 中路径正确

### 第二阶段: 视觉优化

3. **背景色固定** (问题 4) - 中优先级
   - 修改 `Scene.tsx` 使用固定白色背景

4. **火柴人重设计** (问题 3) - 中优先级
   - 重写 `StickFigure.tsx` 中的 SVG 组件

---

## 测试验证清单

修复完成后，执行以下验证:

- [ ] 运行 `python3 scripts/main.py --topic "IPO" --skip-tts` 生成数据
- [ ] 检查 `remotion/public/audio/` 目录是否有音频文件
- [ ] 检查 `remotion/public/assets/` 目录是否有素材文件
- [ ] 检查 `remotion/src/data.json` 中的路径是否正确
- [ ] 运行 `cd remotion && npx remotion preview` 预览效果
- [ ] 验证音频是否正常播放
- [ ] 验证素材图片是否正确显示
- [ ] 验证背景是否为纯白色
- [ ] 验证火柴人样式是否美观

---

## 文件修改清单

| 文件路径 | 修改类型 | 说明 |
|---------|---------|------|
| `scripts/main.py` | 修改 | 添加音频和素材复制逻辑 |
| `scripts/config.py` | 修改 | 更新 ICONS 映射到实际文件名 |
| `remotion/src/components/Scene.tsx` | 修改 | 固定背景为纯白色 |
| `remotion/src/components/StickFigure.tsx` | 重写 | 重新设计 SVG 火柴人 |
| `remotion/src/types/scene.ts` | 可选修改 | 统一 SCENE_STYLES 背景色 |

---

*修复计划完成 - 幽浮喵 ฅ'ω'ฅ*
