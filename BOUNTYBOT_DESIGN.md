# BountyBot 系统设计文档

> 自动化 RustChain Bounty 任务处理系统 v8
> 最后更新: 2026-03-11

---

## 📖 概述

BountyBot 是一个完全自动化的 GitHub bounty 任务处理系统，能够：
- 自动扫描 GitHub bounty 任务
- 智能分析任务类型
- 自动生成代码/文档
- 自动创建 Pull Request
- 持续监控和处理

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        BountyBot v8                              │
│                    完全自动化任务处理系统                           │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
   ┌─────────┐           ┌──────────┐           ┌──────────┐
   │ 任务扫描 │           │ 任务分析  │           │ 任务处理  │
   │(GitHub) │           │(Analyzer)│           │(Handler) │
   └─────────┘           └──────────┘           └──────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   GitHub API            TaskAnalyzer           11个处理器
   获取bounty             正则匹配              创建PR
```

---

## 🔄 完整处理流程

### Phase 1: 系统初始化

```python
def __init__(self):
    # 1. 读取配置
    GITHUB_TOKEN = read_token_from_file("/home/admin/.token")
    WALLET_ADDRESS = "RTC27a4b8256b4d3c63737b27e96b181223cc8774ae"
    CHECK_INTERVAL = 300  # 5分钟
    
    # 2. 获取单例锁
    if not acquire_lock(".bountybot.lock"):
        exit("另一个实例正在运行")
    
    # 3. 加载历史记录
    processed, skipped = load_processed(".bounty_processed.json")
    
    # 4. 初始化组件
    self.api = GitHubAPI(GITHUB_TOKEN)
    self.handler = TaskHandler(self.api)
```

### Phase 2: 任务扫描

```python
def fetch_bounties():
    """每5分钟扫描一次 GitHub bounty 任务"""
    url = "https://api.github.com/repos/Scottcjn/rustchain-bounties/issues"
    params = {
        "state": "open",
        "labels": "bounty",
        "per_page": 50
    }
    
    response = requests.get(url, headers=api_headers, params=params)
    issues = response.json()  # 返回最多50个开放任务
    
    # 过滤已处理的任务
    pending = []
    for issue in issues:
        if issue['number'] not in processed and issue['number'] not in skipped:
            pending.append(issue)
    
    return pending
```

### Phase 3: 任务分析

```python
class TaskAnalyzer:
    """智能任务分析器"""
    
    # 跳过模式 - 这些任务不会被处理
    SKIP_PATTERNS = [
        # CI/CD Workflow - 放弃处理
        r'github\s*action',
        r'workflow',
        r'ci/cd',
        r'dependabot',
        r'renovate',
        
        # 需要用户配合 - 无法自动处理
        r'screenshot',
        r'telegram\s*bot',
        r'discord\s*bot',
        r'social\s*media',
        r'mobile\s*app',
        r'postman\s*collection',
        r'browser\s*extension',
    ]
    
    # 任务处理器映射
    TASK_CONFIG = {
        # 优先级 5 - 已有成功案例
        'dockerfile': {
            'priority': 5,
            'handler': 'create_dockerfile'
        },
        'contributing': {
            'priority': 5,
            'handler': 'create_contributing'
        },
        
        # 优先级 4 - 文档和工具
        'openapi': {
            'priority': 4,
            'handler': 'create_openapi_spec'
        },
        'swagger': {
            'priority': 4,
            'handler': 'create_openapi_spec'
        },
        'homebrew': {
            'priority': 4,
            'handler': 'create_homebrew_formula'
        },
        'comparison': {
            'priority': 4,
            'handler': 'write_comparison_article'
        },
        'cli tool': {
            'priority': 4,
            'handler': 'create_cli_tool'
        },
        
        # 优先级 3 - 测试和代码质量
        'load test': {
            'priority': 3,
            'handler': 'create_load_test'
        },
        'unit test': {
            'priority': 3,
            'handler': 'create_unit_test'
        },
        'type hint': {
            'priority': 3,
            'handler': 'add_type_hints'
        },
        'code comment': {
            'priority': 3,
            'handler': 'add_code_comments'
        },
        'typo': {
            'priority': 3,
            'handler': 'fix_typo'
        },
        'grammar': {
            'priority': 3,
            'handler': 'fix_typo'
        },
    }
    
    @classmethod
    def analyze(cls, issue):
        """分析任务"""
        title = issue.get('title', '').lower()
        body = (issue.get('body') or '').lower()
        combined = title + ' ' + body
        
        # Step 1: 检查跳过模式
        for pattern in cls.SKIP_PATTERNS:
            if re.search(pattern, combined):
                return {
                    'should_skip': True,
                    'reason': f'匹配跳过模式: {pattern}'
                }
        
        # Step 2: 匹配任务处理器
        for keyword, config in cls.TASK_CONFIG.items():
            if keyword in combined:
                return {
                    'should_skip': False,
                    'priority': config['priority'],
                    'handler': config['handler'],
                    'type': keyword
                }
        
        # Step 3: 未知类型
        return {
            'should_skip': False,
            'priority': 1,
            'handler': None,
            'type': 'unknown'
        }
```

### Phase 4: 任务排序

```python
# 分析所有待处理任务
tasks = []
for issue in pending_issues:
    analysis = TaskAnalyzer.analyze(issue)
    if not analysis['should_skip']:
        tasks.append((issue, analysis))

# 按优先级排序（高优先级先处理）
tasks.sort(key=lambda x: x[1].get('priority', 0), reverse=True)
```

### Phase 5: 任务处理

```python
def process_task(issue, analysis):
    """处理单个任务"""
    handler_name = analysis.get('handler')
    
    if handler_name and hasattr(TaskHandler, handler_name):
        handler = getattr(TaskHandler, handler_name)
        return handler(issue)
    
    return None  # 没有找到处理器
```

### Phase 6: PR 创建流程

```python
def _create_pr_for_task(upstream_repo, fork_repo, branch_name, file_path, content, pr_title, pr_body, issue_num):
    """创建 PR 的完整流程"""
    
    # 1. 获取上游仓库最新状态
    upstream_ref = api.get_ref(upstream_repo, "heads/main")
    upstream_sha = upstream_ref["object"]["sha"]
    
    # 2. 尝试同步 Fork
    try:
        api.sync_fork(upstream_repo, fork_repo, upstream_sha)
        base_sha = upstream_sha
    except:
        # 同步失败，使用 Fork 当前状态
        fork_ref = api.get_ref(fork_repo, "heads/main")
        base_sha = fork_ref["object"]["sha"]
    
    # 3. 创建新分支
    api.create_branch(fork_repo, branch_name, base_sha)
    
    # 4. 创建文件
    api.create_or_update_file(
        fork_repo,
        file_path,
        content,
        branch_name,
        f"{pr_title}\n\nCloses #{issue_num}"
    )
    
    # 5. 创建 PR
    pr_url = api.create_pr(
        upstream_repo,
        fork_repo,
        branch_name,
        pr_title,
        pr_body
    )
    
    return pr_url
```

### Phase 7: 间隔管理

```python
# 主循环
while running:
    try:
        # 更新心跳
        update_heartbeat()
        
        # 扫描任务
        issues = fetch_bounties()
        
        # 分析和处理
        for issue in issues:
            analysis = TaskAnalyzer.analyze(issue)
            if not analysis['should_skip']:
                result = process_task(issue, analysis)
                if result:
                    processed.add(issue['number'])
                    save_processed()
                    break  # 每次只处理一个任务
        
        # 等待下一个周期
        log(f"等待 {CHECK_INTERVAL}s...")
        for _ in range(CHECK_INTERVAL):
            if not running:
                break
            time.sleep(1)
    
    except Exception as e:
        log(f"[ERROR] {e}")
        time.sleep(60)  # 错误后等待1分钟
```

---

## 🔧 任务处理器列表

### 高优先级处理器 (优先级 5)

| 处理器 | 任务类型 | 创建的文件 | 成功案例 |
|--------|---------|-----------|---------|
| `create_dockerfile` | Dockerfile | Dockerfile.miner | ✅ PR #823 |
| `create_contributing` | CONTRIBUTING | CONTRIBUTING.md | ✅ PR #355 |

### 中高优先级处理器 (优先级 4)

| 处理器 | 任务类型 | 创建的文件 | 成功案例 |
|--------|---------|-----------|---------|
| `create_openapi_spec` | OpenAPI规范 | docs/openapi.yaml | ⏳ 待审核 |
| `create_homebrew_formula` | Homebrew | homebrew/rustchain.rb | ❌ PR #1674 closed |
| `write_comparison_article` | 比较文章 | docs/comparison-*.md | ⏳ PR #866 |
| `create_cli_tool` | CLI工具 | tools/rustchain_monitor.py | ⏳ PR #864 |

### 中等优先级处理器 (优先级 3)

| 处理器 | 任务类型 | 创建的文件 |
|--------|---------|-----------|
| `create_load_test` | 负载测试 | tests/load_test.py |
| `create_unit_test` | 单元测试 | tests/test_api.py |
| `add_type_hints` | 类型提示 | src/types/api_types.py |
| `add_code_comments` | 代码注释 | src/rustchain_annotated.py |
| `fix_typo` | 拼写修复 | docs/typo_fixes.md |

---

## 📊 状态监控文件

| 文件 | 功能 | 内容示例 |
|------|------|----------|
| `.bountybot.lock` | 单例锁 | `160661` (PID) |
| `.bountybot.heartbeat` | 心跳 | `{"timestamp": 1773225247, "current_task": 1610}` |
| `.bounty_processed.json` | 处理记录 | `{"processed": [1606, 1610], "skipped": [1591, 1592]}` |
| `/tmp/bountybot.log` | 运行日志 | 所有操作的详细日志 |

---

## ⏰ 定时任务配置

### Cron 配置

```bash
# 每小时更新任务列表
0 * * * * cd /home/admin/.openclaw/workspace && python3 bounty_processor.py

# 启动 BountyBot（如果未运行）
*/5 * * * * pgrep -f bountybot.py || (cd /home/admin/.openclaw/workspace && nohup python3 bountybot.py >> /tmp/bountybot.log 2>&1 &)
```

### 手动触发

```bash
# 启动
python3 bountybot.py

# 检查状态
cat /home/admin/.openclaw/workspace/.bountybot.heartbeat

# 查看日志
tail -f /tmp/bountybot.log

# 停止
pkill -f bountybot.py
```

---

## 🎯 跳过规则详解

### 自动跳过的任务类型

| 类别 | 关键词 | 原因 |
|------|--------|------|
| **CI/CD** | github action, workflow, dependabot | 用户要求不处理 |
| **需要截图** | screenshot, video | 无法自动生成 |
| **社交媒体** | twitter, telegram bot, discord bot | 需要用户操作 |
| **移动端** | mobile app, react native, flutter | 复杂度高 |
| **第三方平台** | postman, grafana | 需要外部配置 |

### 跳过检测逻辑

```python
def should_skip(issue):
    title = issue['title'].lower()
    body = issue.get('body', '').lower()
    combined = title + ' ' + body
    
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, combined):
            return True, f"匹配: {pattern}"
    
    return False, None
```

---

## 📈 性能指标

| 指标 | 数值 |
|------|------|
| 扫描间隔 | 5 分钟 |
| 每次扫描任务数 | 最多 50 个 |
| 处理器数量 | 11 个 |
| 平均处理时间 | 5-10 秒/任务 |
| 错误重试间隔 | 60 秒 |

---

## 🔐 安全配置

| 配置项 | 值 |
|--------|-----|
| GitHub Token | 从 `/home/admin/.token` 读取 |
| 钱包地址 | `RTC27a4b8256b4d3c63737b27e96b181223cc8774ae` |
| 单例锁 | `.bountybot.lock` |
| 日志位置 | `/tmp/bountybot.log` |

---

## 📝 使用示例

### 查看当前状态

```bash
# 查看运行状态
ps aux | grep bountybot

# 查看心跳
cat /home/admin/.openclaw/workspace/.bountybot.heartbeat

# 查看处理记录
cat /home/admin/.openclaw/workspace/.bounty_processed.json

# 查看待处理任务
cat /home/admin/.openclaw/workspace/bounty.todolist
```

### 手动操作

```bash
# 启动 BountyBot
cd /home/admin/.openclaw/workspace && python3 bountybot.py

# 停止 BountyBot
pkill -f bountybot.py

# 重新扫描任务
python3 bounty_processor.py
```

---

## ✅ 成功案例

| PR | 任务 | 奖励 | 状态 |
|----|------|------|------|
| [#823](https://github.com/Scottcjn/Rustchain/pull/823) | Dockerfile | 3 RTC | ✅ MERGED |
| [#355](https://github.com/Scottcjn/bottube/pull/355) | CONTRIBUTING | 1 RTC | ✅ MERGED |
| [#864](https://github.com/Scottcjn/Rustchain/pull/864) | CLI工具 | 5 RTC | ⏳ 审核 |
| [#866](https://github.com/Scottcjn/Rustchain/pull/866) | 比较文章 | 3 RTC | ⏳ 审核 |

**已确认收益: 4 RTC**
**待审核收益: 8 RTC**

---

## 🚀 未来改进

1. **增加更多处理器** - 支持更多任务类型
2. **智能重试** - 失败任务自动重试
3. **邮件通知** - PR 创建后发送邮件
4. **竞品监控** - 监控 createkr 等竞争对手
5. **分支清理** - 自动清理已合并的分支

---

*最后更新: 2026-03-11*
*版本: v8*