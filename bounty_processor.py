#!/usr/bin/env python3
"""
Bounty Task Auto-Processor v2
自动处理RustChain bounty任务的脚本

功能:
1. 每小时检查GitHub bounty任务
2. 智能筛选可自动处理的任务
3. 更新bounty.todolist
4. 自动处理任务并提交PR
5. 更新memory记录

v2 更新:
- 增加智能任务分析器 (TaskAnalyzer)
- 精确识别需要用户配合的任务
- 精确识别 CI/CD workflow 相关任务
- 提供详细的跳过原因
"""

import os
import re
import json
import time
import requests
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration - 从文件读取 Token
TOKEN_FILE = "/home/admin/.token"
if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, 'r') as f:
        GITHUB_TOKEN = f.read().strip()
else:
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
WALLET_ADDRESS = "RTC27a4b8256b4d3c63737b27e96b181223cc8774ae"
AGENT_NAME = "dannamax"
WORKSPACE = "/home/admin/.openclaw/workspace"
TODOLIST_FILE = f"{WORKSPACE}/bounty.todolist"
MEMORY_FILE = f"{WORKSPACE}/memory/2026-03-11.md"
MAIN_MEMORY_FILE = f"{WORKSPACE}/MEMORY.md"


class TaskAnalyzer:
    """
    智能任务分析器
    分析任务是否可以自动处理，以及跳过的原因
    """
    
    # ==================== 跳过规则定义 ====================
    
    # 规则1: CI/CD Workflow 相关 - 放弃处理
    WORKFLOW_PATTERNS = [
        (r'github\s*action', 'CI/CD: GitHub Actions'),
        (r'workflow', 'CI/CD: Workflow'),
        (r'ci/cd', 'CI/CD: CI/CD Pipeline'),
        (r'ci\s*cd', 'CI/CD: CI CD'),
        (r'ci\s*pipeline', 'CI/CD: CI Pipeline'),
        (r'dependabot', 'CI/CD: Dependabot'),
        (r'renovate', 'CI/CD: Renovate'),
    ]
    
    # 规则2: 需要用户配合操作的任务
    USER_INTERACTION_PATTERNS = [
        # 社交媒体相关
        (r'screenshot', '需要截图证明'),
        (r'video\s*(recording|call|chat)', '需要视频'),
        (r'upload\s*(to|video|image)', '需要上传'),
        (r'social\s*media', '需要社交媒体操作'),
        (r'tweet|twitter', '需要Twitter操作'),
        (r'linkedin', '需要LinkedIn操作'),
        (r'star\s*(all|repo)', '需要Star操作'),
        (r'upvote', '需要投票操作'),
        (r'emoji\s*reaction', '需要Emoji反应'),
        (r'like|share|follow', '需要社交互动'),
        
        # 第三方平台相关
        (r'clawhub', '需要登录ClawHub'),
        (r'bot[t]?ube', '需要登录BoTTube'),
        (r'postman\s*collection', '需要Postman操作'),
        (r'grafana', '需要Grafana操作'),
        
        # 移动端相关
        (r'mobile\s*app', '需要移动端开发'),
        (r'react\s*native', '需要React Native'),
        (r'flutter', '需要Flutter'),
        
        # Bot 相关
        (r'telegram\s*bot', '需要Telegram Bot'),
        (r'discord\s*bot', '需要Discord Bot'),
        (r'bot\s*for', '需要Bot开发'),
        
        # 其他需要用户操作
        (r'browser\s*extension', '需要浏览器扩展开发'),
        (r'sdk\s*wrapper', '需要SDK开发'),
        (r'blog\s*post|tutorial', '需要写博客/教程'),
        (r'translate', '需要翻译'),
        (r'awesome\s*list', '需要提交到Awesome List'),
    ]
    
    # 规则3: 可自动处理的任务类型
    AUTO_PROCESSABLE = {
        # 高自动化 (⭐⭐⭐⭐⭐)
        'dockerfile': {'priority': 5, 'handler': 'create_dockerfile'},
        'contributing': {'priority': 5, 'handler': 'create_contributing'},
        
        # 中高自动化 (⭐⭐⭐⭐)
        'openapi': {'priority': 4, 'handler': 'create_openapi'},
        'swagger': {'priority': 4, 'handler': 'create_openapi'},
        'homebrew': {'priority': 4, 'handler': 'create_homebrew'},
        'formula': {'priority': 4, 'handler': 'create_homebrew'},
        'load\s*test': {'priority': 4, 'handler': 'create_load_test'},
        'unit\s*test': {'priority': 4, 'handler': 'create_unit_test'},
        'cli\s*tool': {'priority': 4, 'handler': 'create_cli'},
        
        # 中等自动化 (⭐⭐⭐)
        'code\s*comment': {'priority': 3, 'handler': 'add_comments'},
        'type\s*hint': {'priority': 3, 'handler': 'add_type_hints'},
        'typo|grammar': {'priority': 3, 'handler': 'fix_typo'},
        'comparison': {'priority': 3, 'handler': 'write_comparison'},
    }
    
    @classmethod
    def analyze(cls, issue):
        """
        分析任务
        
        返回:
        {
            'should_skip': bool,      # 是否应该跳过
            'skip_reason': str,       # 跳过原因
            'skip_category': str,     # 跳过类别 (workflow/user_interaction/none)
            'auto_level': int,        # 自动化等级 (1-5)
            'handler': str,           # 处理器名称
            'task_type': str,         # 任务类型
        }
        """
        title = issue.get('title', '').lower()
        body = (issue.get('body') or '').lower()
        combined = title + ' ' + body
        
        result = {
            'should_skip': False,
            'skip_reason': None,
            'skip_category': 'none',
            'auto_level': 0,
            'handler': None,
            'task_type': 'unknown'
        }
        
        # Step 1: 检查 CI/CD Workflow 相关
        for pattern, reason in cls.WORKFLOW_PATTERNS:
            if re.search(pattern, combined):
                result['should_skip'] = True
                result['skip_reason'] = reason
                result['skip_category'] = 'workflow'
                return result
        
        # Step 2: 检查需要用户配合的任务
        for pattern, reason in cls.USER_INTERACTION_PATTERNS:
            if re.search(pattern, combined):
                result['should_skip'] = True
                result['skip_reason'] = reason
                result['skip_category'] = 'user_interaction'
                return result
        
        # Step 3: 检查可自动处理的任务类型
        for task_type, config in cls.AUTO_PROCESSABLE.items():
            if re.search(task_type, combined):
                result['auto_level'] = config['priority']
                result['handler'] = config['handler']
                result['task_type'] = task_type.replace('\\s*', ' ')
                return result
        
        # Step 4: 默认情况 - 未知任务类型
        result['auto_level'] = 1
        return result
    
    @classmethod
    def get_skip_summary(cls, issues):
        """获取跳过任务的统计摘要"""
        summary = {
            'workflow': [],
            'user_interaction': [],
            'total_skipped': 0
        }
        
        for issue in issues:
            analysis = cls.analyze(issue)
            if analysis['should_skip']:
                summary['total_skipped'] += 1
                if analysis['skip_category'] == 'workflow':
                    summary['workflow'].append({
                        'id': issue['number'],
                        'title': issue['title'][:50],
                        'reason': analysis['skip_reason']
                    })
                else:
                    summary['user_interaction'].append({
                        'id': issue['number'],
                        'title': issue['title'][:50],
                        'reason': analysis['skip_reason']
                    })
        
        return summary


class BountyProcessor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        })
        self.processed_issues = self.load_processed_issues()
    
    def load_processed_issues(self):
        """Load already processed issue numbers"""
        processed_file = f"{WORKSPACE}/.bounty_processed.json"
        if os.path.exists(processed_file):
            with open(processed_file, 'r') as f:
                data = json.load(f)
                return set(data.get('processed', []))
        return set()
    
    def save_processed_issues(self):
        """Save processed issue numbers"""
        processed_file = f"{WORKSPACE}/.bounty_processed.json"
        with open(processed_file, 'w') as f:
            json.dump(list(self.processed_issues), f)
    
    def fetch_open_bounties(self):
        """Fetch all open bounty issues"""
        url = "https://api.github.com/repos/Scottcjn/rustchain-bounties/issues"
        params = {"state": "open", "labels": "bounty", "per_page": 50}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to fetch issues: {e}")
            return []
    
    def categorize_bounty(self, issue, analysis):
        """Categorize bounty by type and difficulty"""
        title = issue.get('title', '')
        body = issue.get('body', '') or ''
        
        # Extract reward
        reward_match = re.search(r'\[.*?(\d+[-\d]*\s*RTC).*?\]', title, re.IGNORECASE)
        reward = reward_match.group(1) if reward_match else "未知"
        
        # Determine automation level
        auto_level = analysis.get('auto_level', 1)
        automation = "⭐" * min(auto_level, 5) if auto_level > 0 else "⭐⭐⭐"
        
        # Determine difficulty
        difficulty = "中等"
        if 'EASY' in title.upper():
            difficulty = "简单"
        elif any(kw in title.upper() for kw in ['BUILD', 'CREATE', 'IMPLEMENT', 'PORT']):
            difficulty = "困难"
        
        return {
            'id': issue['number'],
            'title': title[:60],
            'reward': reward,
            'automation': automation,
            'difficulty': difficulty,
            'url': issue['html_url'],
            'body': body,
            'task_type': analysis.get('task_type', 'unknown'),
            'skip_reason': analysis.get('skip_reason'),
            'skip_category': analysis.get('skip_category')
        }
    
    def update_todolist(self, pending, completed, abandoned, skip_summary):
        """Update bounty.todolist file"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M GMT+8")
        
        content = f"""# Bounty Task Todolist

> 自动更新时间: {now}
> 筛选条件: 可自动处理、无需用户配合、代码/文档类任务

---

## 📋 任务筛选规则

### 自动处理条件（必须全部满足）
- ✅ 代码/文档/配置类任务
- ✅ 可通过API/Git自动提交
- ✅ 不需要登录第三方网站
- ✅ 不需要截图/录屏证明
- ✅ 不需要社交媒体操作
- ✅ 不涉及 CI/CD Workflow

### 放弃条件（任一满足）
- ❌ CI/CD Workflow 相关任务
- ❌ 需要登录ClawHub/BoTTube等第三方网站
- ❌ 需要截图/录屏证明
- ❌ 需要社交媒体操作（点赞、转发、评论）
- ❌ 需要用户手动操作

---

## 🔄 待处理任务队列

| # | Issue | 任务 | 奖励 | 自动化 | 类型 | 状态 |
|---|-------|------|------|--------|------|------|
"""
        
        for i, task in enumerate(pending, 1):
            content += f"| {i} | #{task['id']} | {task['title']} | {task['reward']} | {task['automation']} | {task['task_type']} | ⏳ 待处理 |\n"
        
        content += """
---

## ✅ 已处理任务

| # | Issue | 任务 | 奖励 | PR链接 | 状态 | 处理时间 |
|---|-------|------|------|--------|------|----------|
"""
        
        for i, task in enumerate(completed, 1):
            pr_link = task.get('pr_link', '评论提交')
            status = task.get('status', '⏳ 审核中')
            processed_time = task.get('processed_time', '-')
            content += f"| {i} | #{task['id']} | {task['title']} | {task['reward']} | {pr_link} | {status} | {processed_time} |\n"
        
        # 分类显示已放弃任务
        content += """
---

## 🚫 已放弃任务

### 🔧 CI/CD Workflow 相关（不处理）

| # | Issue | 任务 | 奖励 | 原因 |
|---|-------|------|------|------|
"""
        
        for i, task in enumerate(skip_summary['workflow'], 1):
            content += f"| {i} | #{task['id']} | {task['title']} | - | {task['reason']} |\n"
        
        content += """
### 👤 需要用户配合操作

| # | Issue | 任务 | 奖励 | 原因 |
|---|-------|------|------|------|
"""
        
        for i, task in enumerate(skip_summary['user_interaction'], 1):
            content += f"| {i} | #{task['id']} | {task['title']} | - | {task['reason']} |\n"
        
        # 统计
        total_pending_reward = sum(self._extract_reward_num(t['reward']) for t in pending)
        total_completed_reward = sum(self._extract_reward_num(t['reward']) for t in completed)
        
        content += f"""
---

## 📊 统计

| 类别 | 数量 | 奖励 |
|------|------|------|
| 待处理 | {len(pending)} | {total_pending_reward} RTC |
| 已处理 | {len(completed)} | {total_completed_reward} RTC |
| CI/CD 放弃 | {len(skip_summary['workflow'])} | - |
| 需用户配合 | {len(skip_summary['user_interaction'])} | - |

---

## 📝 最近更新

```
[{now}] 智能任务分析完成
- CI/CD Workflow 任务: {len(skip_summary['workflow'])} 个
- 需要用户配合: {len(skip_summary['user_interaction'])} 个
- 可自动处理: {len(pending)} 个
```
"""
        
        with open(TODOLIST_FILE, 'w') as f:
            f.write(content)
        
        print(f"[OK] Updated {TODOLIST_FILE}")
    
    def _extract_reward_num(self, reward_str):
        """Extract numeric reward from string"""
        match = re.search(r'(\d+)', str(reward_str))
        return int(match.group(1)) if match else 0
    
    def update_memory(self, completed_tasks, skip_summary):
        """Update memory files with completed tasks"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M GMT+8")
        
        daily_content = f"""
---

## 自动处理记录 [{now}]

### 任务分析摘要

- **CI/CD Workflow 放弃**: {len(skip_summary['workflow'])} 个
- **需要用户配合**: {len(skip_summary['user_interaction'])} 个
- **可自动处理**: {len(completed_tasks)} 个

### 已完成任务

"""
        for task in completed_tasks:
            daily_content += f"- Issue #{task['id']}: {task['title']} ({task['reward']})\n"
        
        with open(MEMORY_FILE, 'a') as f:
            f.write(daily_content)
        
        print(f"[OK] Updated {MEMORY_FILE}")
    
    def run(self):
        """Main processing loop"""
        print(f"\n{'='*50}")
        print(f"Bounty Auto-Processor v2")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}\n")
        
        # Fetch issues
        print("[1/5] Fetching open bounty issues...")
        issues = self.fetch_open_bounties()
        print(f"      Found {len(issues)} open bounty issues")
        
        # Analyze and categorize
        print("[2/5] Analyzing tasks with TaskAnalyzer...")
        pending = []
        completed = self._load_completed_tasks()
        abandoned = []
        
        for issue in issues:
            issue_num = issue['number']
            
            # Skip already processed
            if issue_num in self.processed_issues:
                continue
            
            # 使用 TaskAnalyzer 分析任务
            analysis = TaskAnalyzer.analyze(issue)
            task = self.categorize_bounty(issue, analysis)
            
            if analysis['should_skip']:
                # 任务应该跳过
                abandoned.append({
                    **task,
                    'reason': analysis['skip_reason']
                })
                print(f"      ⏭️ #{issue_num}: {analysis['skip_reason']}")
            else:
                # 任务可以处理
                pending.append(task)
                print(f"      ✓ #{issue_num}: {task['title'][:40]} ({task['reward']}) [{task['task_type']}]")
        
        # 获取跳过统计
        skip_summary = TaskAnalyzer.get_skip_summary(issues)
        
        print(f"\n      可自动处理: {len(pending)}")
        print(f"      CI/CD 放弃: {len(skip_summary['workflow'])}")
        print(f"      需用户配合: {len(skip_summary['user_interaction'])}")
        
        # Update todolist
        print("\n[3/5] Updating todolist...")
        self.update_todolist(pending, completed, abandoned, skip_summary)
        
        # Process tasks
        print("[4/5] Processing auto-tasks...")
        # (Auto-processing logic would go here)
        
        # Update memory
        print("[5/5] Updating memory records...")
        if completed:
            self.update_memory(completed, skip_summary)
        
        print(f"\n{'='*50}")
        print("Processing complete!")
        print(f"Pending: {len(pending)} | Completed: {len(completed)}")
        print(f"Skipped (CI/CD): {len(skip_summary['workflow'])}")
        print(f"Skipped (User): {len(skip_summary['user_interaction'])}")
        print(f"{'='*50}\n")
        
        return pending, completed, abandoned
    
    def _load_completed_tasks(self):
        """Load completed tasks from memory"""
        return [
            {'id': 1555, 'title': 'ClawHub投票4个包', 'reward': '3 RTC', 
             'pr_link': '评论提交', 'status': '⏳ 审核中', 'processed_time': '2026-03-11 01:14'},
            {'id': 1611, 'title': '添加Emoji反应', 'reward': '1 RTC', 
             'pr_link': '评论提交', 'status': '⏳ 审核中', 'processed_time': '2026-03-11 01:30'},
            {'id': 1599, 'title': '矿机Dockerfile', 'reward': '3 RTC', 
             'pr_link': '[PR #823](https://github.com/Scottcjn/Rustchain/pull/823)', 
             'status': '✅ MERGED', 'processed_time': '2026-03-11 09:43'},
            {'id': 1605, 'title': 'CONTRIBUTING.md', 'reward': '1 RTC', 
             'pr_link': '[PR #355](https://github.com/Scottcjn/bottube/pull/355)', 
             'status': '✅ MERGED', 'processed_time': '2026-03-11 09:43'},
            {'id': 1613, 'title': 'Dependabot配置', 'reward': '3 RTC', 
             'pr_link': '[PR #836](https://github.com/Scottcjn/Rustchain/pull/836)', 
             'status': '⏳ 审核中', 'processed_time': '2026-03-11 15:46'},
            {'id': 1614, 'title': '负载测试套件', 'reward': '5 RTC', 
             'pr_link': '[PR #838](https://github.com/Scottcjn/Rustchain/pull/838)', 
             'status': '⏳ 审核中', 'processed_time': '2026-03-11 15:56'},
            {'id': 1612, 'title': 'Homebrew formula', 'reward': '5 RTC', 
             'pr_link': '[PR #1674](https://github.com/Scottcjn/rustchain-bounties/pull/1674)', 
             'status': '⏳ 审核中', 'processed_time': '2026-03-11 16:01'},
        ]


if __name__ == "__main__":
    processor = BountyProcessor()
    processor.run()