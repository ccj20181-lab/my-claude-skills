# 并行粉丝数据获取指南

## 目标
为 10 个用户获取粉丝数据

## 方案
使用 Claude Code 的 Task 工具启动 **2 个 subagent** 并行处理

## 步骤

### 步骤 1: 准备批次数据
```bash
python scripts/auto_fetch_fans_parallel.py compact_users.json fans.json 2
```
此命令会：
1. 读取 compact_users.json
2. 分割成 2 个批次（每批 5 个用户）
3. 生成 2 个提示词文件

### 步骤 2: 启动 Subagents

打开 **2 个新的 Claude Code 窗口**（或使用多轮对话），每个窗口执行：

**窗口 1**（处理批次 1 - 5 个用户）：
```markdown
请执行以下任务。完成后直接返回 JSON 结果，不要有其他解释。

[TEMPLATE]
```json
[{'userId': '660ee4ee000000000d0264d6', 'xsec_token': 'ABU1BHhdnkQPZBoV2fmsVTRGckftdOuV_439T1x_zzFrw=', 'nickname': '渔山学财经'}, {'userId': '5ff5214800000000010039cf', 'xsec_token': 'ABU1BHhdnkQPZBoV2fmsVTRK35kv_Fn8fRLKdj_CTOkk0=', 'nickname': '招财小猫咪'}, {'userId': '6194ae1a000000002102497a', 'xsec_token': 'ABn2Z5Y4D7koMMohim4fxAl_y3xTK9hUS68d-gl2E4jB0=', 'nickname': '奶爸财经'}, {'userId': '68e4ce0a0000000037000157', 'xsec_token': 'AB2XrCgthEqasbeLiEoXb62yVwurOGlWR8vu06a6KMTXo=', 'nickname': '爱学习的叮当猫'}, {'userId': '6268dcb40000000021020748', 'xsec_token': 'ABn2Z5Y4D7koMMohim4fxAlzymy9IDMUNr_tqS1RbDg_o=', 'nickname': '程娘子浅谈攒钱'}]
```
[/TEMPLATE]
```

**窗口 2**（处理批次 2 - 5 个用户）：
```markdown
请执行以下任务。完成后直接返回 JSON 结果，不要有其他解释。

[TEMPLATE]
```json
[{'userId': '6046f6150000000001005169', 'xsec_token': 'ABU1BHhdnkQPZBoV2fmsVTRDFOyu5hs6GqHFQ2mVAr49M=', 'nickname': '橙子（搞钱版）'}, {'userId': '6684dc20000000001e00b362', 'xsec_token': 'ABn2Z5Y4D7koMMohim4fxAl8Bkg2xD18prwfGb9SDE0Dg=', 'nickname': '王死有钱'}, {'userId': '6805a7920000000007001ae6', 'xsec_token': 'AB2XrCgthEqasbeLiEoXb62-F53jLNQ2jRsbWpwzYB7D4=', 'nickname': '大A研究者'}, {'userId': '6730df39000000001c019639', 'xsec_token': 'ABi02UEDFPWIHOTR1EwbbTmlmDJM4Q50i9suv5crdBmnw=', 'nickname': '找对象'}, {'userId': '642d90c50000000010029c61', 'xsec_token': 'AB2XrCgthEqasbeLiEoXb626aVhj25KN6IvSuvSxE7SZs=', 'nickname': '阿水超清醒'}]
```
[/TEMPLATE]
```



### 步骤 3: 收集结果

将每个窗口返回的结果保存到单独的文件：
```bash
echo '{subagent1_result}' > fans_batch_1.json
echo '{subagent2_result}' > fans_batch_2.json

```

### 步骤 4: 合并结果
```bash
type fans_batch_*.json > fans.json
```

### 步骤 5: 继续 pipeline
```bash
python scripts/merge_fans_data.py fans.json data.json
python scripts/pipeline.py --file data.json --mode finance-pro
```

## 关键优势

| 指标 | 传统方式 | Subagent 方式 |
|------|----------|---------------|
| 上下文累积 | 累积到主上下文 | 每个 subagent 独立 |
| 爆炸风险 | 高 | 无 |
| 处理时间 | 串行 | 并行 |
| 结果格式 | 完整响应 | 精简 {userId: fans} |

## 预计效果

- 主上下文消耗: ~400 tokens（只保存结果）
- 每个 subagent 消耗: ~65000 tokens（独立）
- **总消耗大幅降低，且不会爆炸** ✨

