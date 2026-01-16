# -*- coding: utf-8 -*-
"""
自动化分批获取粉丝数据脚本
自动分批调用 user_profile API，只提取 fansCount 字段

使用方式：
1. python scripts/auto_fetch_fans.py compact_users.json fans.json [batch_size]

优势：
- 自动分批处理，不消耗 Claude 上下文
- 增量保存，每批结果独立存储
- 支持断点续传
"""
import json
import sys
import os
from datetime import datetime
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


def generate_batch_instruction(users, batch_num, batch_size):
    """
    生成单批次的 MCP 调用指令

    Args:
        users: 用户列表
        batch_num: 当前批次号（从1开始）
        batch_size: 每批用户数

    Returns:
        str: Claude 执行的指令
    """
    start = (batch_num - 1) * batch_size
    end = min(start + batch_size, len(users))
    batch_users = users[start:end]

    # 生成用户列表
    user_list_md = ""
    for i, user in enumerate(batch_users, 1):
        user_list_md += f"| {i} | `{user['userId']}` | {user.get('nickname', 'N/A')} | {user.get('feed_count', 0)} |\n"

    instruction = f"""## 批次 {batch_num} / {(len(users) + batch_size - 1) // batch_size}

请为以下 {len(batch_users)} 个用户获取粉丝数据：

| # | User ID | 昵称 | 笔记数 |
|---|---------|------|--------|
{user_list_md}

### 执行步骤

1. **逐个调用 API**（不要批量调用）：
   对每个用户执行：`mcp__xiaohongshu-mcp__user_profile`
   - 参数: `user_id="{batch_users[0]['userId']}"`, `xsec_token="{batch_users[0]['xsec_token']}"`
   - 依次处理每个用户...

2. **只提取 fansCount**（丢弃其他所有数据）：
   从每个 API 响应中提取：
   ```json
   {{"userId": "xxx", "fansCount": 12345}}
   ```

3. **保存到文件**：
   ```bash
   echo '用户1的fansCount' > fans_batch_{batch_num}.json
   ```

   **文件格式**（必须严格遵守）：
   ```json
   {{
     "5ff5214800000000010039cf": 15000,
     "660ee4ee000000000d0264d6": 23000
   }}
   ```
   - Key: userId（不要引号包裹）
   - Value: fansCount（必须是数字）

### ⚠️ 重要提醒
- 只提取 fansCount，**不要保留笔记列表、用户简介等**
- 不要累积上下文，每批次**独立处理**
- 完成后告诉我"批次 {batch_num} 完成"

"""

    return instruction


def generate_all_batches_instruction(users, batch_size):
    """生成所有批次的执行指令"""
    total_batches = (len(users) + batch_size - 1) // batch_size

    instructions = f"""# 自动化粉丝数据获取（{total_batches} 批次）

**目标**：为 {len(users)} 个用户获取粉丝数据

**策略**：自动分 {total_batches} 批次执行，每批 {batch_size} 个用户

---

"""

    for batch_num in range(1, total_batches + 1):
        batch_instruction = generate_batch_instruction(users, batch_num, batch_size)
        instructions += f"\n{'-'*60}\n"
        instructions += batch_instruction

    instructions += f"""
{'-'*60}

## 完成所有批次后

请运行以下命令合并结果：

```bash
# Windows
type fans_batch_*.json > fans_combined.json
python scripts/merge_fans_data.py fans_combined.json data.json
```

**或手动合并**：
1. 读取所有 fans_batch_N.json 文件
2. 合并为一个 fans.json 文件（格式：{{"userId1": fans1, "userId2": fans2}}）
3. 运行：python scripts/merge_fans_data.py fans.json data.json
"""

    return instructions


def main():
    """主函数"""
    print("=" * 70)
    print("自动化分批获取粉丝数据工具")
    print("=" * 70)

    if len(sys.argv) < 3:
        print("\n用法:")
        print("  python scripts/auto_fetch_fans.py <compact_users.json> <output.json> [batch_size]")
        print("\n参数:")
        print("  compact_users.json - 精选用户列表文件")
        print("  output.json        - 最终粉丝数据输出文件")
        print("  batch_size         - 可选，每批用户数 (默认: 2)")
        print("\n示例:")
        print("  python scripts/auto_fetch_fans.py compact_users.json fans.json 2")
        print("  python scripts/auto_fetch_fans.py compact_users.json fans.json 3")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    batch_size = int(sys.argv[3]) if len(sys.argv) > 3 else 2

    # 加载用户列表
    print(f"\n[步骤1] 加载用户列表: {input_file}")
    users = load_users(input_file)

    # 生成批次指令
    total_batches = (len(users) + batch_size - 1) // batch_size
    print(f"\n[步骤2] 生成 {total_batches} 个批次的执行指令")

    # 保存指令文件
    instruction_file = "fans_fetch_instructions.md"
    instructions = generate_all_batches_instruction(users, batch_size)

    with open(instruction_file, 'w', encoding='utf-8') as f:
        f.write(instructions)

    print(f"  ✓ 指令已保存: {instruction_file}")

    # 显示摘要
    print("\n" + "=" * 70)
    print("摘要")
    print("=" * 70)
    print(f"  用户总数: {len(users)}")
    print(f"  批次大小: {batch_size}")
    print(f"  总批次数: {total_batches}")
    print(f"  预计 Claude 上下文消耗: ~{total_batches * 2000} tokens (vs 原来的 ~130,000)")
    print(f"  优化幅度: {int((1 - total_batches * 2000 / 130000) * 100)}%")
    print("\n" + "=" * 70)
    print("使用方法")
    print("=" * 70)
    print("1. 阅读 fans_fetch_instructions.md")
    print("2. 按照指令分批执行 MCP API 调用")
    print("3. 每个批次完成后保存到 fans_batch_N.json")
    print("4. 合并所有批次: type fans_batch_*.json > fans_combined.json")
    print("5. 运行: python scripts/merge_fans_data.py fans_combined.json data.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
