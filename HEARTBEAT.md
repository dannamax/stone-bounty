# HEARTBEAT.md - 自动任务检查

> 此文件定义了心跳时自动执行的任务
> ⚠️ 每次会话启动时都会读取此文件并执行

---

## 🤖 自动化 Bounty 任务调度器

### 核心功能

系统会自动执行以下操作：

1. **读取任务清单** - 自动解析 `bounty.todolist`
2. **串行处理任务** - 按优先级逐个处理
3. **自动更新状态** - 更新任务状态和 memory 记录
4. **持续循环** - 处理完成后自动处理下一个

---

## 📋 心跳执行流程

### Step 1: 检查并运行任务调度器

```bash
cd /home/admin/.openclaw/workspace && python3 bounty_scheduler.py
```

### Step 2: 更新任务列表

```bash
cd /home/admin/.openclaw/workspace && python3 bounty_processor.py
```

### Step 3: 检查 PR 状态

```bash
# 检查所有已提交 PR 的状态
curl -s "https://api.github.com/repos/Scottcjn/Rustchain/pulls/823" | jq -r '.state, .merged'
curl -s "https://api.github.com/repos/Scottcjn/bottube/pulls/355" | jq -r '.state, .merged'
curl -s "https://api.github.com/repos/Scottcjn/bottube/pulls/356" | jq -r '.state, .merged'
```

---

## 📊 当前任务优先级

| 优先级 | 任务类型 | 示例 Issue |
|--------|---------|-----------|
| ⭐⭐⭐⭐⭐ | Dockerfile, GitHub Actions | #1599, #1591 |
| ⭐⭐⭐⭐ | CLI工具, OpenAPI, 测试 | #1606, #1604, #1614 |
| ⭐⭐⭐ | 代码注释, 类型提示 | #1608, #1588 |

---

## 🔄 自动化处理规则

### 会自动处理的任务类型

- ✅ Dockerfile 创建
- ✅ GitHub Actions workflow
- ✅ CONTRIBUTING.md
- ✅ 文档修复
- ✅ OpenAPI/Swagger 规范

### 会跳过的任务类型

- ❌ 需要截图证明
- ❌ 需要登录第三方网站
- ❌ 需要社交媒体操作
- ❌ 需要用户手动操作

---

## 📝 自动化能力记录

### 已实现的自动化

1. **任务扫描** - 自动扫描 GitHub bounty 任务
2. **任务筛选** - 按自动化程度筛选
3. **任务处理** - 串行自动处理
4. **PR 创建** - 自动提交 PR
5. **状态更新** - 更新 todolist 和 memory

### 关键文件

| 文件 | 功能 |
|------|------|
| `bounty_scheduler.py` | 任务调度器（串行处理） |
| `bounty_processor.py` | 任务扫描器（更新列表） |
| `bounty.todolist` | 任务清单 |
| `.bounty_processed.json` | 已处理记录 |

---

## ⏰ 定时任务

- **Cron**: 每小时自动检查更新
- **Heartbeat**: 每次会话自动执行调度器
- **手动触发**: `python3 bounty_scheduler.py`

---

## 🎯 下次心跳执行

**执行内容**:
1. 运行 bounty_scheduler.py
2. 运行 bounty_processor.py  
3. 更新 memory 记录

**预期结果**: 自动处理下一个高优先级任务