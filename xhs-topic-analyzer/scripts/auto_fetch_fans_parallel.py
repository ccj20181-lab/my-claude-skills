# -*- coding: utf-8 -*-
"""
并行获取粉丝数据脚本
使用 Claude Code 的 Task 工具启动多个 subagent 并行获取粉丝数据

使用方式：
python scripts/auto_fetch_fans_parallel.py all_users.json fans.json 3

输入文件格式（all_users.json）：
{
  "users": [
    {"userId": "xxx", "xsec_token": "xxx", "nickname": "昵称"},
    ...
  ],
  "total": 30
}

优势：
- 并行处理多个用户
- 每个 subagent 独立上下文，不会累积到主上下文
- 只返回精简结果（{userId: fansCount}）
"""
import json
import sys
import os
from pathlib import Path

# 解决 Windows 控制台编码问题
if os.name == 'nt':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def load_users(input_file):
    """加载精选用户列表"""
    if not os.path.exists(input_file):
        print(f"✗ 错误: 文件不存在 - {input_file}")
        sys.exit(1)

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    users = data.get("users", [])
    if not users:
        print("✗ 错误: 用户列表为空")
        sys.exit(1)

    print(f"✓ 加载用户数: {len(users)}")
    return users


def split_users_into_batches(users, batch_size):
    """将用户列表分割成多个批次"""
    batches = []
    for i in range(0, len(users), batch_size):
        batch = users[i:i + batch_size]
        # 提取 subagent 需要的字段
        batch_data = []
        for user in batch:
            batch_data.append({
                "userId": user.get("userId") or user.get("user_id"),
                "xsec_token": user.get("xsec_token"),
                "nickname": user.get("nickname", "N/A")
            })
        batches.append(batch_data)
    return batches


def generate_subagent_prompt(users):
    """生成 subagent 的提示词"""
    prompt = """# 粉丝数据获取任务

请为以下小红书用户获取粉丝数据：

## 用户列表
```json
""" + json.dumps(users, ensure_ascii=False, indent=2) + """
```

## 执行要求

1. 对每个用户调用 `mcp__xiaohongshu-mcp__user_profile`。
2. **极简模式**：只提取粉丝数（fans count）。
3. **严禁**输出用户笔记列表（feed list），这会导致 Token 爆炸！
4. 不要尝试保存文件。

## 最终输出

请只返回一个合法的 JSON 字符串（不要用 markdown 包裹，不要有其他解释文字）：
{"userId1": 12345, "userId2": 67890}
"""
    return prompt


def save_batch_prompts(batches, output_dir="batch_prompts"):
    """保存每个批次的提示词到文件"""
    os.makedirs(output_dir, exist_ok=True)

    batch_files = []
    for i, batch in enumerate(batches, 1):
        prompt = generate_subagent_prompt(batch)
        filename = f"batch_{i}.txt"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(prompt)
        batch_files.append(filepath)
        print(f"  ✓ 批次 {i}: {len(batch)} 个用户 -> {filename}")

    return batch_files


def generate_instructions(batches, users_file, output_file):
    """
    生成并行获取指令

    Args:
        batches: 分好的批次列表
        users_file: 用户列表文件
        output_file: 输出文件

    Returns:
        str: 执行指令
    """
    instructions = f"""# 并行粉丝数据获取指南

## 目标
为 {sum(len(b) for b in batches)} 个用户获取粉丝数据

## 方案
使用 Claude Code 的 Task 工具启动 **{len(batches)} 个 subagent** 并行处理

## 步骤

### 步骤 1: 准备批次数据
```bash
python scripts/auto_fetch_fans_parallel.py {users_file} {output_file} 2
```
此命令会：
1. 读取 {users_file}
2. 分割成 {len(batches)} 个批次（每批 {len(batches[0]) if batches else 0} 个用户）
3. 生成 {len(batches)} 个提示词文件

### 步骤 2: 启动 Subagents

打开 **{len(batches)} 个新的 Claude Code 窗口**（或使用多轮对话），每个窗口执行：

**窗口 1**（处理批次 1 - {len(batches[0]) if batches else 0} 个用户）：
```markdown
请执行以下任务。完成后直接返回 JSON 结果，不要有其他解释。

[TEMPLATE]
```json
{batches[0] if batches else []}
```
[/TEMPLATE]
```

**窗口 2**（处理批次 2 - {len(batches[1]) if len(batches) > 1 else 0} 个用户）：
```markdown
请执行以下任务。完成后直接返回 JSON 结果，不要有其他解释。

[TEMPLATE]
```json
{batches[1] if len(batches) > 1 else []}
```
[/TEMPLATE]
```

{f'''**窗口 3**（处理批次 3 - {len(batches[2]) if len(batches) > 2 else 0} 个用户）：
```markdown
请执行以下任务。完成后直接返回 JSON 结果，不要有其他解释。

[TEMPLATE]
```json
{batches[2] if len(batches) > 2 else []}
```
[/TEMPLATE]
''' if len(batches) > 2 else ''}

### 步骤 3: 收集结果

将每个窗口返回的结果保存到单独的文件：
```bash
echo '{{subagent1_result}}' > fans_batch_1.json
echo '{{subagent2_result}}' > fans_batch_2.json
{f'''echo '{{subagent3_result}}' > fans_batch_3.json''' if len(batches) > 2 else ''}
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
| 结果格式 | 完整响应 | 精简 {{userId: fans}} |

## 预计效果

- 主上下文消耗: ~{len(batches) * 200} tokens（只保存结果）
- 每个 subagent 消耗: ~{len(batches[0]) * 13000 if batches else 0} tokens（独立）
- **总消耗大幅降低，且不会爆炸** ✨

"""
    return instructions


def main():
    """主函数"""
    print("=" * 70)
    print("并行获取粉丝数据工具（使用 Subagent 机制）")
    print("=" * 70)

    if len(sys.argv) < 3:
        print("\n用法:")
        print("  python scripts/auto_fetch_fans_parallel.py <users.json> <output.json> [batch_size]")
        print("\n参数:")
        print("  users.json   - 精选用户列表文件 (compact_users.json)")
        print("  output.json  - 粉丝数据输出文件 (fans.json)")
        print("  batch_size   - 可选，每批用户数 (默认: 2)")
        print("\n示例:")
        print("  python scripts/auto_fetch_fans_parallel.py compact_users.json fans.json 2")
        print("  python scripts/auto_fetch_fans_parallel.py compact_users.json fans.json 3")
        sys.exit(1)

    users_file = sys.argv[1]
    output_file = sys.argv[2]
    batch_size = int(sys.argv[3]) if len(sys.argv) > 3 else 2

    # 加载用户列表
    print(f"\n[步骤1] 加载用户列表: {users_file}")
    users = load_users(users_file)

    # 分割成批次
    print(f"\n[步骤2] 分割成批次（每批 {batch_size} 个用户）")
    batches = split_users_into_batches(users, batch_size)
    print(f"  总批次数: {len(batches)}")

    # 生成并行获取指令
    print(f"\n[步骤3] 生成并行获取指令")
    instructions = generate_instructions(batches, users_file, output_file)

    # 保存指令
    instruction_file = "parallel_fetch_instructions.md"
    with open(instruction_file, 'w', encoding='utf-8') as f:
        f.write(instructions)
    print(f"  ✓ 指令已保存: {instruction_file}")

    # 保存批次提示词
    print(f"\n[步骤4] 保存批次提示词")
    batch_files = save_batch_prompts(batches)

    # 显示摘要
    print("\n" + "=" * 70)
    print("摘要")
    print("=" * 70)
    print(f"  用户总数: {len(users)}")
    print(f"  批次大小: {batch_size}")
    print(f"  总批次数: {len(batches)}")
    print(f"  建议: 打开 {len(batches)} 个窗口并行处理")
    print("\n" + "=" * 70)
    print("使用方法")
    print("=" * 70)
    print("1. 阅读 parallel_fetch_instructions.md")
    print(f"2. 打开 {len(batches)} 个 Claude Code 窗口")
    print(f"3. 每个窗口读取 batch_prompts/batch_N.txt 并执行")
    print("4. 收集结果，合并到 fans.json")
    print("5. 继续 pipeline")
    print("=" * 70)


if __name__ == "__main__":
    main()
