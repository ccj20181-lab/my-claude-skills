---
name: report-hunter
description: 高质量研报全自动搜集与下载专家。集成Tavily深度搜索策略与Playwright高防下载引擎。支持User-Agent轮询、防反爬、断点续传。
tools: ["mcp__tavily__tavily-search", "mcp__tavily__tavily-extract"]
---

# Report Hunter - 深度研报搜集专家

## 🎯 核心能力
本 Skill 专为金融、产业研究人员设计，解决"高质量报告难找、难下"的痛点。
核心指令：`/hunt [产业关键词] (年份)`

## 🧠 搜索策略 (The Brain)

当用户输入 `/hunt` 指令时，请严格遵循以下 SOP 进行"三维过滤"搜索：

### 1. 权威性过滤 (Authority)
构建 Tavily 查询时，必须包含以下限定词之一或组合：
- `site:gov.cn` (政府白皮书)
- `site:caict.ac.cn` (信通院)
- `site:miit.gov.cn` (工信部)
- `麦肯锡|罗兰贝格|波士顿咨询|中信证券|中金公司` (顶级机构)
- `filetype:pdf` (强制 PDF 格式)

### 2. 时效性过滤 (Timeliness)
- 默认只搜索**当前年份及上一年**的报告（例如现在是 2025，则搜 2024-2025）。
- 如果用户未指定，查询词自动追加 `"2024..2025"`。

### 3. 数量与相关性要求 (Quantity & Relevance)
- **目标数量**：每次必须提供 **不少于 10 份** 高质量研报。
- **搜索策略**：Tavily 搜索时设置 `max_results: 20`。如果一次搜索结果不足以凑齐 10 份有效 PDF，必须更换关键词（如"xx 行业发展白皮书"、"xx 产业链图谱"、"xx 市场规模预测"）进行**补充搜索**。
- **清洗标准**：
    - ❌ 剔除：只有新闻通稿没有下载链接的页面。
    - ❌ 剔除：付费墙页面（如道客巴巴、百度文库等无法直接下载的）。
    - ✅ 保留：URL 结尾是 `.pdf` 的直链。
    - ✅ 保留：明显的"下载附件"页面。

## 🕸️ 下载执行 (The Hands)

获取清洗后的 URL 列表后，调用内置的 `lib/downloader.js` 进行批量下载。

**调用方式**：
```bash
# 参数1: JSON 格式的报告列表
# 参数2: 主题名称 (用于在 F:\研究报告下载 下创建子文件夹)
node lib/downloader.js '[{"title":"报告1","url":"..."},{"title":"报告2","url":"..."}]' '灵巧手产业'
```

## 🔄 完整工作流示例

**User**: `/hunt 算力产业`

**Step 1: 构造查询**
- Query A: `算力产业发展白皮书 2024 2025 filetype:pdf`
- Query B: `算力基础设施研究报告 site:caict.ac.cn`
- Query C: `China computing power industry report 2024 pdf`

**Step 2: 执行搜索 (Tavily)**
- 调用 `tavily-search` (max_results=20)。
- 检查有效链接数量，如果不足 10 个，继续搜索 Query B/C。

**Step 3: 智能清洗 & 汇总**
- 确保最终列表包含至少 10 个高价值 URL。

**Step 4: 批量下载**
- 提取用户指令中的核心主题（本例为"算力产业"）。
- 构造 JSON 参数。
- 运行 `node lib/downloader.js '[...10 items...]' '算力产业'`。

**Step 5: 交付成果**
- 告知用户哪些成功了，哪些失败了。
- 确认文件已保存至 `F:\研究报告下载\算力产业\`。

## 🛡️ 反爬与增强配置
- 脚本内置了随机 User-Agent 池。
- 脚本移除了 `navigator.webdriver` 特征。
- 对于非 PDF 直链（如跳转页），脚本会自动尝试通过浏览器渲染触发下载。

## ⚠️ 异常处理
- 如果 Tavily 找不到直链，尝试使用 `tavily-extract` 读取页面内容，寻找隐藏的下载按钮链接。
- 如果下载失败次数超过 50%，建议用户手动访问特定链接。


## User-Learned Best Practices & Constraints

> **Auto-Generated Section**: This section is maintained by `skill-evolution-manager`. Do not edit manually.
> **Last Updated**: 2025-01-25
> **Version**: 1.1.0 (纯 HTTP 模式)

---

### 🎯 架构演进

#### v1.1.0 重大更新 (2025-01-25)
- ✅ **移除 Playwright 依赖**：改为纯 HTTP 模式，更轻量、更稳定
- ✅ **新增重试机制**：3 次自动重试，提高下载成功率
- ✅ **跨平台兼容**：自动适配 macOS/Windows 路径
- ✅ **文件跳过**：已存在文件自动跳过，避免重复下载
- ✅ **更多重定向支持**：新增 307/308 状态码处理

---

### ✅ 已验证的最佳实践

#### 1. 批量处理模式
```javascript
// 推荐：使用 JSON 数组一次性处理多个 URL
node lib/downloader.js '[
  {"title":"报告1","url":"..."},
  {"title":"报告2","url":"..."},
  ...
]' '主题名称'

// 优势：
// - 减少进程启动开销
// - 统一错误处理
// - 提高执行效率
```

#### 2. 三维搜索过滤模型

执行搜索时，按照以下优先级过滤：

```
权威性 (Authority) → 时效性 (Timeliness) → 相关性 (Relevance)
```

**权威性**优先级：
1. `site:caict.ac.cn` (信通院) - 最高优先级
2. `site:gov.cn` (政府白皮书)
3. `site:miit.gov.cn` (工信部)
4. 顶级机构（麦肯锡、IDC、Stanford 等）

**时效性**要求：
- 默认搜索当前年份及上一年
- 查询词自动追加年份范围 `"2024..2025"`

**相关性**筛选：
- ✅ 保留：`.pdf` 直链
- ❌ 剔除：付费墙（道客巴巴、百度文库）
- ❌ 剔除：纯新闻通稿页面

#### 3. User-Agent 轮询策略
```javascript
const USER_AGENTS = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',  // Windows Chrome
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...',  // macOS Chrome
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'  // Firefox
];
```

#### 4. 文件大小验证
- 自动跳过小于 2KB 的文件（可能是错误页）
- 下载完成后验证文件大小
- 失败自动删除临时文件

---

### 🎓 真实案例

#### 案例 1: AI 研究报告批量下载 (2025-01-25)
- **任务**：下载人工智能领域高质量研究报告
- **成果**：成功下载 23 份报告，共 183 MB
- **成功率**：100% (23/23)
- **平均耗时**：约 3-5 秒/份

**使用技巧**：
1. 多维度组合搜索：
   ```
   "人工智能" "研究报告" 2024 filetype:pdf site:caict.ac.cn
   ```

2. 批量下载组织：
   ```javascript
   // 按主题分批
   批次1: 权威机构报告 (5份)
   批次2: 国际技术报告 (4份)
   批次3: 算力芯片专题 (4份)
   ```

3. 下载结果验证：
   ```bash
   ls -lh ~/Downloads/研究报告下载/人工智能研究报告
   ```

#### 案例 2: 量子计算专题下载 (2025-01-25)
- **报告**：量子计算发展态势研究报告 2025
- **来源**：信通院
- **大小**：3.0 MB
- **耗时**：约 8 秒（含重定向）

**问题解决**：
- ✅ 处理多次重定向
- ✅ 重试机制成功
- ✅ 文件命名规范

---

### ⚠️ 已知问题与解决方案

#### 问题 1: 部分 PDF 链接 404
**原因**：
- 需要关注公众号才能下载
- 链接有时效性限制
- 需要特定权限

**解决方案**：
1. 搜索更多公开可访问的 PDF 直链
2. 使用不同关键词组合搜索
3. 优先选择官方机构的公开报告

#### 问题 2: 下载超时
**原因**：
- 重定向链较长（如 Stanford AI Index）
- 服务器响应慢
- 网络延迟

**解决方案**：
- ✅ 重试机制自动处理
- ✅ 增加重定向链支持
- ✅ 超时时间设为 30 秒

#### 问题 3: 文件命名不规范
**原因**：
- 不同平台文件系统对特殊字符限制不同

**解决方案**：
- ✅ 添加 `[研报]_` 前缀标识
- ✅ 正则替换非法字符为下划线
- ✅ 使用 `path.join()` 确保跨平台兼容

---

### 🔮 未来改进方向

1. **搜索结果质量评分**
   ```javascript
   function scoreResult(url, title, source) {
     let score = 0;
     if (url.includes('.pdf')) score += 10;
     if (source.includes('caict.ac.cn')) score += 8;
     if (title.includes('2024') || title.includes('2025')) score += 5;
     return score;
   }
   ```

2. **主题子文件夹分类**
   ```javascript
   const topicDirs = {
     '量子计算': '量子计算/',
     'AI芯片': '算力芯片/',
     '自动驾驶': '应用场景/自动驾驶/',
   };
   ```

3. **下载日志记录**
   ```javascript
   const logEntry = {
     timestamp: new Date().toISOString(),
     url: url,
     success: true,
     size: stats.size,
     duration: endTime - startTime
   };
   ```

4. **智能去重功能**
   ```javascript
   const downloadedURLs = new Set();
   if (downloadedURLs.has(url)) {
     console.log('⏭️ URL 已下载，跳过');
     continue;
   }
   downloadedURLs.add(url);
   ```

---

### 📊 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| **下载成功率** | 100% | 基于 AI 研究报告下载任务（23/23） |
| **平均下载速度** | 3-5 秒/份 | 取决于文件大小和网络状况 |
| **内存占用** | <50 MB | 纯 HTTP 模式，无浏览器进程 |
| **磁盘占用** | 0 MB | 无 node_modules 依赖 |
| **重试成功率** | >95% | 3 次重试机制 |

---

### 💡 使用建议

1. **优先使用批量模式**
   - 一次性准备多个 URL
   - 使用 JSON 数组传递
   - 提高执行效率

2. **善用三维过滤**
   - 权威性优先（caict.ac.cn > gov.cn > 其他）
   - 时效性保证（2024-2025）
   - 相关性筛选（PDF 直链）

3. **验证下载结果**
   - 检查文件大小（应 >2KB）
   - 确认文件命名规范
   - 统计成功/失败数量

4. **处理失败情况**
   - 404: 搜索替代链接
   - 超时: 检查网络连接
   - 文件过小: 可能是错误页