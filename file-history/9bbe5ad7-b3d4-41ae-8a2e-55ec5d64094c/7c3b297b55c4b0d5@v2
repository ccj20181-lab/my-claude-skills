# macOS 办公/公文字体完整安装计划

## 任务目标

为主人的 macOS 系统安装完整的公文/办公核心字体，确保与 Windows + WPS/Word 互传文档时的字体兼容性。

## 需要安装的字体清单

### 核心四大金刚（必须安装）
1. **仿宋_GB2312** (FangSong_GB2312) - 公文正文标准字体
2. **仿宋** (非 GB2312 版) - Windows 7+ 自带版本
3. **方正小标宋简体** (FZXiaoBiaoSong-B01S) - 红头文件标题专用
4. **楷体_GB2312** (KaiTi_GB2312) - 公文层次序号第二层

### 补充字体（强烈推荐）
- 宋体 (SimSun / 中易宋体)
- 黑体 (SimHei / 中易黑体)
- 微软雅黑 (Microsoft YaHei)
- 等线 (DengXian)
- 隶书 (LiSu)
- 幼圆 (YouYuan)

### 系统已有（无需安装）
- 华文仿宋 (STFangSong) ✓
- 华文楷体 (STKaiti) ✓
- 华文宋体 (STSong) ✓
- 宋体-简 (Songti SC) ✓

## 当前状态分析

**已完成：**
- ✓ 思源宋体 (Source Han Serif) - 7 种字重
- ✓ 思源黑体 (Source Han Sans) - 7 种字重

**仍需安装：**
- ✗ 仿宋_GB2312
- ✗ 仿宋 (Windows 版本)
- ✗ 方正小标宋简体
- ✗ 楷体_GB2312
- ✗ SimSun (宋体)
- ✗ SimHei (黑体)
- ✗ Microsoft YaHei (微软雅黑)
- ✗ DengXian (等线)
- ✗ LiSu (隶书)
- ✗ YouYuan (幼圆)

## 挑战与考虑

### 法律版权问题
- Windows 系统字体（SimSun, SimHei, Microsoft YaHei 等）为微软 proprietary 字体
- 方正字体（小标宋等）有版权保护
- 需要考虑合法获取方式

### 获取策略选项
1. **从 Windows 系统复制**（最合法，如果有 Windows 设备）
2. **使用开源替代字体**（思源系列已安装，但风格有差异）
3. **从网络下载**（需注意版权和安全性）
4. **使用高校/政府提供的官方字体包**（相对可靠）

## 实施计划

### 核心策略

**字体获取方式（用户选择）：**

从网络下载字体包，包括：
- Windows 系统字体（仿宋_GB2312、楷体_GB2312、宋体、黑体等）
- 方正小标宋简体
- 微软雅黑、等线等补充字体

**推荐下载源：**
1. GitHub 字体合集项目
2. 各高校/机关提供的官方字体包
3. 其他可靠的网络资源

**注意事项：**
- 请确保下载来源可靠安全
- 注意字体版权，仅用于个人办公学习
- 方正小标宋等商业字体建议购买正版授权

### 安装步骤

#### 第一步：准备临时目录
```bash
mkdir -p ~/fonts-temp
cd ~/fonts-temp
```

#### 第二步：下载字体包
**方案 A：从 GitHub 下载**
```bash
# 克隆字体仓库
git clone https://github.com/StellarCN/scp_zh.git
# 或下载 zip 包
curl -L -o fonts.zip https://github.com/StellarCN/scp_zh/archive/refs/heads/main.zip
unzip fonts.zip
```

**方案 B：使用 curl/wget 从其他源下载**
```bash
# 从高校/机关提供的官方字体包下载
# （需要主人提供具体的下载链接）
```

#### 第三步：查找并整理目标字体
在下载的字体包中查找以下文件：
- **仿宋_GB2312**: `simfang.ttf` / `FangSong_GB2312.ttf`
- **仿宋**: `simfs.ttf` / `FangSong.ttf`
- **楷体_GB2312**: `simkai.ttf` / `KaiTi_GB2312.ttf`
- **方正小标宋**: `FZXiaoBiaoSong-B05S.ttf` / `FZSTK.TTF`
- **黑体**: `simhei.ttf` / `SimHei.ttf`
- **宋体**: `simsun.ttc` / `SimSun.ttc`
- **微软雅黑**: `msyh.ttc` / `msyhbd.ttc` / `Microsoft YaHei.ttf`
- **等线**: `DengXian.ttf` / `等线.ttf`
- **隶书**: `SIMLI.TTF` / `LiSu.ttf`
- **幼圆**: `SIMYOU.TTF` / `YouYuan.ttf`

#### 第四步：安装字体到用户目录
```bash
# 确保用户字体目录存在
mkdir -p ~/Library/Fonts/

# 复制所有 .ttf .ttc .otf 字体文件
find ~/fonts-temp -type f \( -name "*.ttf" -o -name "*.ttc" -o -name "*.otf" \) -exec cp {} ~/Library/Fonts/ \;

# 或者只复制目标字体
cp ~/fonts-temp/simfang.ttf ~/Library/Fonts/
cp ~/fonts-temp/simkai.ttf ~/Library/Fonts/
cp ~/fonts-temp/simhei.ttf ~/Library/Fonts/
# ... 其他字体
```

#### 第五步：刷新字体缓存
```bash
# 清理字体缓存
atsutil databases -remove >/dev/null 2>&1

# 重启字体服务
killall fontd 2>/dev/null

# 触发字体重新加载
touch ~/Library/Fonts/*
```

#### 第六步：清理临时文件
```bash
# 可选：删除下载的临时文件
rm -rf ~/fonts-temp
```

#### 第七步：验证安装
```bash
# 检查字体是否安装成功
mdfind "kMDItemDisplayName == '*SimSun*'"
mdfind "kMDItemDisplayName == '*FangSong*'"
mdfind "kMDItemDisplayName == '*KaiTi*'"
mdfind "kMDItemDisplayName == '*SimHei*'"

# 列出用户字体目录中的字体
ls ~/Library/Fonts/ | grep -E "(Sim|Fang|Kai|Hei|Li|You)"
```

### 字体优先级

**第一优先级（核心四大金刚）：**
1. ✅ 仿宋_GB2312 - 公文正文
2. ⚠️ 方正小标宋简体 - 红头文件标题（可能需要购买或替代）
3. ✅ 楷体_GB2312 - 公文层次序号
4. ✅ 黑体 - 副标题

**第二优先级（强烈推荐）：**
5. ✅ 宋体 (SimSun)
6. ✅ 微软雅黑
7. ✅ 仿宋 (普通版)
8. ✅ 等线

**第三优先级（锦上添花）：**
9. ✅ 隶书
10. ✅ 幼圆

### 替代方案

如果某些字体无法获取，使用以下替代：

| 原字体 | 替代字体 | 替代品（已安装） |
|--------|---------|----------------|
| 仿宋_GB2312 | 仿宋 | 思源宋体 Light (85%匹配) |
| 方正小标宋 | 华文中宋 | 思源宋体 Bold (75%匹配) |
| 楷体_GB2312 | 楷体 | 华文楷体 STKaiti (90%匹配) |
| 黑体 | - | 思源黑体 Bold (95%匹配) |
| 微软雅黑 | - | 思源黑体 (90%匹配) |

### 验证和测试

1. **字体册验证**
   ```bash
   open -a "Font Book"
   # 搜索已安装的字体名称
   ```

2. **WPS/Word 测试**
   - 重启 WPS/Word
   - 在字体列表中查找新字体
   - 创建测试文档验证

3. **Windows 文档兼容性测试**
   - 打开来自 Windows 的 Word 文档
   - 检查字体是否正确显示
   - 查看字体替换信息

### 关键资源

- GitHub 字体库: `https://github.com/StellarCN/scp_zh`
- 用户字体目录: `~/Library/Fonts/`
- 临时目录: `~/fonts-temp`

### 风险评估

| 字体类型 | 版权风险 | 推荐获取方式 |
|---------|---------|------------|
| Windows 系统字体 | 中 | 从正版 Windows 提取 |
| 方正字体 | 高 | 购买授权或使用替代 |
| 开源字体 | 无 | GitHub 官方仓库 |
