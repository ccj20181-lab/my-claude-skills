# TTS 配置说明

本文档说明 MiniMax TTS API 的配置和使用方法。

## API 概述

使用 MiniMax 的 T2A (Text-to-Audio) v2 API 进行语音合成。

### API 端点
```
POST https://api.minimax.chat/v1/t2a_v2?GroupId={group_id}
```

### 认证
```
Authorization: Bearer {api_key}
Content-Type: application/json
```

---

## 环境变量配置

```bash
# 必需
export MINIMAX_API_KEY="your_api_key_here"
export MINIMAX_GROUP_ID="your_group_id_here"
```

### 获取 API Key
1. 访问 [MiniMax 开放平台](https://www.minimaxi.com/)
2. 注册/登录账号
3. 进入控制台 → API 管理
4. 创建 API Key 和 Group ID

---

## 默认配置

```python
TTSConfig(
    model="speech-02-hd",        # 高清模型
    voice_id="female-tianmei",   # 甜美女声
    speed=1.0,                   # 正常语速
    pitch=0,                     # 正常音调
    volume=100,                  # 最大音量
    sample_rate=24000,           # 采样率
)
```

---

## 可用音色

### 推荐音色（财经科普）

| Voice ID | 名称 | 特点 | 推荐场景 |
|----------|------|------|----------|
| `female-tianmei` | 甜美女声 | 亲切自然 | **默认推荐** |
| `female-yujie` | 御姐女声 | 成熟稳重 | 专业内容 |
| `male-qn-jingying` | 精英青年 | 清晰专业 | 严肃话题 |
| `male-qn-qingse` | 青涩青年 | 活泼年轻 | 轻松话题 |

### 其他可用音色

**女声**
- `female-shaonv` - 少女
- `female-yujie` - 御姐
- `female-chengshu` - 成熟女性
- `female-tianmei` - 甜美

**男声**
- `male-qn-qingse` - 青涩青年
- `male-qn-jingying` - 精英青年
- `male-qn-badao` - 霸道青年
- `male-qn-daxuesheng` - 大学生

---

## 参数说明

### 语速 (speed)
```python
speed: float  # 范围 0.5 - 2.0, 默认 1.0
```
- 0.5: 慢速，适合复杂概念
- 1.0: 正常速度（推荐）
- 1.2: 稍快，适合简单内容
- 1.5+: 快速，不推荐

### 音调 (pitch)
```python
pitch: int  # 范围 -12 到 12, 默认 0
```
- 负值: 更低沉
- 0: 正常
- 正值: 更高亢

### 音量 (volume)
```python
volume: int  # 范围 0-100, 默认 100
```
建议保持 100，后期可在视频中调整。

### 采样率 (sample_rate)
```python
sample_rate: int  # 可选 16000, 24000, 32000
```
- 16000: 较小文件
- 24000: 平衡（推荐）
- 32000: 高质量

---

## 使用示例

### 基本使用

```python
from tts_minimax import MiniMaxTTS, TTSConfig
import asyncio

async def main():
    config = TTSConfig(voice_id="female-tianmei")
    tts = MiniMaxTTS(config)

    result = await tts.synthesize(
        text="大家好，今天我们来聊聊什么是IPO",
        output_path="./output.mp3"
    )

    print(f"音频时长: {result.duration_ms}ms")
    print(f"保存位置: {result.audio_path}")

asyncio.run(main())
```

### 批量生成

```python
async def generate_all_scenes(scenes):
    config = TTSConfig()
    tts = MiniMaxTTS(config)

    results = await tts.synthesize_scenes(
        scenes=scenes,
        output_dir="./audio"
    )

    return results
```

### 自定义音色

```python
config = TTSConfig(
    voice_id="male-qn-jingying",
    speed=0.95,
    pitch=0,
)
```

---

## 时间戳功能

API 返回的时间戳可用于字幕同步。

### 返回格式
```json
{
  "word_timestamps": [
    {"word": "大家", "start_ms": 0, "end_ms": 320},
    {"word": "好", "start_ms": 320, "end_ms": 480},
    {"word": "，", "start_ms": 480, "end_ms": 560},
    ...
  ]
}
```

### 用于字幕高亮
```tsx
// Remotion 中使用
const currentTimeMs = (frame / fps) * 1000;

wordTimestamps.map((word) => {
  const isActive = currentTimeMs >= word.start_ms
                && currentTimeMs < word.end_ms;
  return (
    <span style={{ color: isActive ? "blue" : "black" }}>
      {word.word}
    </span>
  );
});
```

---

## 缓存机制

脚本内置缓存机制，避免重复生成相同内容。

### 缓存逻辑
1. 根据文本内容 + 音色 + 语速生成 MD5 哈希
2. 检查是否存在对应音频文件
3. 如存在且有元数据，直接返回缓存
4. 否则调用 API 生成新音频

### 禁用缓存
```python
result = await tts.synthesize(
    text="...",
    output_path="...",
    use_cache=False  # 强制重新生成
)
```

---

## 错误处理

### 常见错误

| 错误码 | 原因 | 解决方案 |
|--------|------|----------|
| 401 | API Key 无效 | 检查 MINIMAX_API_KEY |
| 403 | Group ID 不匹配 | 检查 MINIMAX_GROUP_ID |
| 429 | 请求过于频繁 | 增加请求间隔 |
| 500 | 服务器错误 | 重试或联系支持 |

### 错误处理代码
```python
try:
    result = await tts.synthesize(text, output_path)
except ValueError as e:
    print(f"配置错误: {e}")
except RuntimeError as e:
    print(f"API 错误: {e}")
```

---

## 成本优化

### 计费方式
按字符数计费，中文每个字符计 1 个单位。

### 优化建议
1. **启用缓存**: 避免重复生成相同内容
2. **精简文案**: 去除不必要的语气词
3. **合理时长**: 控制视频时长在 2-3 分钟
4. **批量生成**: 一次性生成所有场景音频

### 估算成本
```
假设：
- 150 秒视频 ≈ 450-600 字
- 按 0.1 元/1000 字计算
- 每个视频约 0.05-0.06 元
```

---

## 常见问题

### Q: 生成的音频有杂音？
A: 检查文本中是否有特殊字符，尝试清理后重新生成。

### Q: 语速感觉太快/太慢？
A: 调整 `speed` 参数，财经内容建议 0.9-1.0。

### Q: 如何切换音色？
A: 在调用时指定 `voice_id`，或在 `config.py` 中修改默认值。

### Q: API 返回超时？
A: 长文本可能需要更长处理时间，增加请求超时设置。

---

## 测试命令

```bash
# 测试单句
python3 scripts/tts_minimax.py "这是一段测试语音" ./test.mp3

# 检查配置
python3 -c "from scripts.config import TTSConfig; c = TTSConfig(); print(c)"
```
