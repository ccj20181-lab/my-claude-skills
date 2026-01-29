---
name: wechat-publish
description: 将 Markdown 文章发布到微信公众号草稿箱，支持多种精美主题风格和 AI 自动生成封面图。当用户需要：(1) 发布文章到公众号，(2) 发布到微信，(3) 同步到公众号草稿箱，(4) 发小绿书 时触发。
version: 1.1.0
tools:
  - Bash
  - Read
  - Write
  - AskUserQuestion
env:
  IMGBB_API_KEY: 9d823e5d2dc9c968daf476e4abfab336
  WECHAT_API_KEY: xhs_4ded7e5d7cef78a0cd27660b5be13db0
  WECHAT_API_BASE: https://wx.limyai.com/api/openapi
  NANOBANANA_API_KEY: sk-30hw0QuR0UD2t6ub808670A2Da6641159aDbAe54519f6743
  NANOBANANA_API_URL: https://api.apiyi.com/v1beta/models/gemini-3-pro-image-preview:generateContent
  GEMINI_API_KEY: ""
  GEMINI_API_BASE: "https://yunwu.ai"
---

# Wechat Publish Skill

这是一个全自动化的微信公众号发布工具。

## 功能列表
1.  **Markdown 转 HTML**: 专为微信编辑器优化，解决空行、列表样式等问题。
2.  **主题渲染**: 提供 4 种精美主题（专业、优雅、活力、极客）。
3.  **图床集成**: 自动扫描本地图片并上传至 ImgBB。
4.  **AI 封面**: 使用 Gemini API 自动生成 2.35:1 的高质量封面图。
5.  **AI 插图 (新!)**: 在文章中通过特殊语法自动生成配图。
6.  **一键发布**: 对接第三方 API 直接发布到公众号草稿箱。

## AI 插图语法
在 Markdown 文件中，你可以使用以下语法让 AI 自动生成插图：

```markdown
![一只可爱的猫娘工程师在写代码](ai:generate)
```

或者指定图片比例：
```markdown
![赛博朋克风格的城市夜景](ai:16:9)
![复古风格的咖啡馆](ai:1:1)
```

工具会自动识别这些标记，调用 Gemini 3 Pro 生成图片，保存到本地并自动上传到图床。

## 运行方式
```bash
node index.js "/path/to/your/article.md"
```

如果未提供文件路径，将会提示用户输入。

---

## ✅ 高清图片固化策略（已内置）
为避免公众号草稿中出现 **1:1 低清缩略图**，本 Skill 默认启用以下策略：

1. **默认图床改为 Catbox**（`IMAGE_HOST=catbox`）  
   Catbox 直链无防盗链限制，避免 ImgBB 的 180×180 缩略图问题。

2. **默认开启图片代理**（`IMAGE_PROXY=https://images.weserv.nl/?w=2400&url=`）  
   通过代理服务器抓取原图，公众号后台无需 Referer 也能拿到高清图。

3. **默认缩放到 2400px + 质量 92**  
   在清晰度与体积之间取得平衡，确保微信不再强制压缩。

### 可配置环境变量
```bash
IMAGE_HOST=catbox            # catbox | imgbb
IMAGE_PROXY=https://images.weserv.nl/?w=2400&url=
IMAGE_PROXY_HOSTS=files.catbox.moe,i.ibb.co

WECHAT_IMAGE_MAX_WIDTH=2400
WECHAT_IMAGE_MAX_BYTES=6000000
WECHAT_IMAGE_QUALITY=92

SKIP_IMAGE_RESIZE=false      # 需要完全保留原图时设置 true
IMGBB_HOTLINK=display        # 使用 ImgBB 时的热链偏好
```

### 如果仍然不清晰（兜底）
- 说明平台对外链图仍有压缩，需切换为 **“微信素材上传接口”**  
  我可以继续接入该接口（需你提供 access_token 或上传 API）。
