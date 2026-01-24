---
name: html-to-desktop
description: 快速将 HTML 代码保存为 .html 文件到桌面。当用户提供 HTML 代码并要求保存、导出、转换为文件、放到桌面时使用此 skill。触发词包括：保存 HTML、导出网页、HTML 转文件、放到桌面、保存到桌面、保存为 html。
---

# HTML to Desktop

将 HTML 代码高效保存为桌面 .html 文件。

## 工作流程

1. **获取代码** - 提取用户消息中的完整 HTML
2. **确定文件名** - 用户指定 > `<title>` 提取 > 语义生成 > 时间戳
3. **保存文件** - Write 工具写入桌面
4. **反馈结果** - 路径 + 打开提示

## 文件命名

**优先级：**
1. 用户明确指定的文件名
2. 从 `<title>` 标签提取（转拼音/保留英文）
3. 根据内容语义命名（dashboard、landing-page 等）
4. 默认：`page-YYYYMMDD-HHMMSS.html`

**规范：** 小写、连字符连接、移除特殊字符、确保 `.html` 后缀

## 保存路径

```
/Users/{username}/Desktop/{filename}.html
```

## 输出模板

```
✅ 文件已保存到桌面喵～

📄 文件名: {filename}
📍 路径: {full_path}
💡 双击文件即可在浏览器中打开
```

## 注意事项

- 文件已存在时添加数字后缀（page-2.html）
- 保持原始 HTML 格式不修改
- 支持任意大小 HTML 内容
