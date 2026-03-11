#!/usr/bin/env python3
"""
Bounty Task Auto-Scheduler
自动化任务监控调度器 - 串行处理bounty任务

功能:
1. 自动读取 bounty.todolist 任务清单
2. 按优先级串行处理任务
3. 处理完成后自动继续下一个任务
4. 更新任务状态和记录

运行方式:
- 手动: python3 bounty_scheduler.py
- 自动: 通过 HEARTBEAT.md 触发
"""

import os
import re
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = "/home/admin/.openclaw/workspace"
TODOLIST_FILE = f"{WORKSPACE}/bounty.todolist"
PROCESSED_FILE = f"{WORKSPACE}/.bounty_processed.json"
MEMORY_FILE = f"{WORKSPACE}/memory/2026-03-11.md"
MAIN_MEMORY_FILE = f"{WORKSPACE}/MEMORY.md"

# 从文件读取 Token (不要硬编码!)
TOKEN_FILE = "/home/admin/.token"
if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, 'r') as f:
        GITHUB_TOKEN = f.read().strip()
else:
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

WALLET_ADDRESS = "RTC27a4b8256b4d3c63737b27e96b181223cc8774ae"
AGENT_NAME = "dannamax"


class BountyScheduler:
    """自动化任务调度器"""
    
    def __init__(self):
        self.processed = self.load_processed()
        self.stats = {"processed": 0, "skipped": 0, "failed": 0}
        
    def load_processed(self):
        """加载已处理的任务列表"""
        if os.path.exists(PROCESSED_FILE):
            with open(PROCESSED_FILE, 'r') as f:
                return set(json.load(f))
        return set()
    
    def save_processed(self):
        """保存已处理的任务列表"""
        with open(PROCESSED_FILE, 'w') as f:
            json.dump(list(self.processed), f)
    
    def parse_todolist(self):
        """解析 bounty.todolist 文件，提取待处理任务"""
        with open(TODOLIST_FILE, 'r') as f:
            content = f.read()
        
        tasks = []
        
        # 解析待处理任务部分
        pending_section = re.search(
            r'## 🔄 待处理任务队列.*?\n\|(?:.*?\|){6}\n((?:\|.*?\|){6}\n?)+',
            content, re.DOTALL
        )
        
        if pending_section:
            lines = pending_section.group(0).strip().split('\n')[2:]  # 跳过表头
            for line in lines:
                if line.strip() and '| - |' not in line:
                    parts = [p.strip() for p in line.split('|') if p.strip()]
                    if len(parts) >= 5:
                        try:
                            issue_num = int(parts[1].replace('#', ''))
                            title = parts[2]
                            reward = parts[3]
                            automation = parts[4]
                            tasks.append({
                                'issue': issue_num,
                                'title': title,
                                'reward': reward,
                                'automation': automation,
                                'priority': automation.count('⭐')
                            })
                        except:
                            continue
        
        # 按优先级排序
        tasks.sort(key=lambda x: x['priority'], reverse=True)
        return tasks
    
    def get_task_handler(self, task):
        """根据任务类型返回处理函数"""
        title = task['title'].lower()
        
        # 任务类型映射
        handlers = {
            'github action': self.handle_github_action,
            'dockerfile': self.handle_dockerfile,
            'contributing': self.handle_contributing,
            'openapi': self.handle_openapi,
            'swagger': self.handle_openapi,
            'cli': self.handle_cli,
            'test': self.handle_test,
            'docker': self.handle_dockerfile,
            'workflow': self.handle_github_action,
        }
        
        for keyword, handler in handlers.items():
            if keyword in title:
                return handler
        
        return None
    
    def handle_github_action(self, task):
        """处理 GitHub Action 任务"""
        print(f"  [Handler] GitHub Action workflow")
        # 实际处理逻辑在主处理器中
        return self.process_github_action_task(task)
    
    def handle_dockerfile(self, task):
        """处理 Dockerfile 任务"""
        print(f"  [Handler] Dockerfile")
        return self.process_dockerfile_task(task)
    
    def handle_contributing(self, task):
        """处理 CONTRIBUTING.md 任务"""
        print(f"  [Handler] CONTRIBUTING.md")
        return self.process_contributing_task(task)
    
    def handle_openapi(self, task):
        """处理 OpenAPI/Swagger 任务"""
        print(f"  [Handler] OpenAPI/Swagger")
        return self.process_openapi_task(task)
    
    def handle_cli(self, task):
        """处理 CLI 工具任务"""
        print(f"  [Handler] CLI tool")
        return self.process_cli_task(task)
    
    def handle_test(self, task):
        """处理测试任务"""
        print(f"  [Handler] Test")
        return self.process_test_task(task)
    
    def process_github_action_task(self, task):
        """实际处理 GitHub Action 任务"""
        # 简化处理：标记为需要手动处理
        print(f"  [Info] GitHub Action 任务需要根据具体仓库定制")
        print(f"  [Info] 建议：手动检查目标仓库并创建合适的 workflow")
        return False  # 返回 False 表示需要进一步处理
    
    def process_dockerfile_task(self, task):
        """处理 Dockerfile 任务"""
        print(f"  [Info] Dockerfile 任务需要根据具体项目定制")
        return False
    
    def process_contributing_task(self, task):
        """处理 CONTRIBUTING.md 任务"""
        print(f"  [Info] CONTRIBUTING.md 任务需要查找缺少该文件的仓库")
        return False
    
    def process_openapi_task(self, task):
        """处理 OpenAPI 任务"""
        print(f"  [Info] OpenAPI 任务需要分析现有 API 接口")
        return False
    
    def process_cli_task(self, task):
        """处理 CLI 工具任务"""
        print(f"  [Info] CLI 工具任务需要根据项目需求设计")
        return False
    
    def process_test_task(self, task):
        """处理测试任务"""
        print(f"  [Info] 测试任务需要分析现有代码并编写测试")
        return False
    
    def update_todolist_status(self, issue_num, status, pr_link="-"):
        """更新 todolist 中的任务状态"""
        with open(TODOLIST_FILE, 'r') as f:
            content = f.read()
        
        # 查找并更新任务状态
        # 这里简化处理，实际需要更复杂的解析
        print(f"  [Update] Task #{issue_num} -> {status}")
    
    def update_memory(self, task, pr_link, status):
        """更新 memory 记录"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M GMT+8")
        
        entry = f"""
### 自动处理记录 [{now}]

- Issue #{task['issue']}: {task['title']}
- 奖励: {task['reward']}
- PR链接: {pr_link}
- 状态: {status}

"""
        with open(MEMORY_FILE, 'a') as f:
            f.write(entry)
    
    def run(self):
        """主调度循环"""
        print(f"\n{'='*60}")
        print(f"Bounty Task Auto-Scheduler")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # 1. 解析任务列表
        print("[1/4] Parsing bounty.todolist...")
        tasks = self.parse_todolist()
        print(f"      Found {len(tasks)} pending tasks")
        
        if not tasks:
            print("\n[INFO] No pending tasks found.")
            return
        
        # 2. 筛选未处理的任务
        print("[2/4] Filtering unprocessed tasks...")
        unprocessed = [t for t in tasks if t['issue'] not in self.processed]
        print(f"      Unprocessed: {len(unprocessed)} tasks")
        
        if not unprocessed:
            print("\n[INFO] All tasks have been processed.")
            return
        
        # 3. 处理第一个任务（串行）
        task = unprocessed[0]
        print(f"\n[3/4] Processing Task #{task['issue']}...")
        print(f"      Title: {task['title']}")
        print(f"      Reward: {task['reward']}")
        print(f"      Priority: {task['automation']}")
        
        # 获取任务处理器
        handler = self.get_task_handler(task)
        
        if handler:
            try:
                result = handler(task)
                if result:
                    self.stats["processed"] += 1
                    self.processed.add(task['issue'])
                    print(f"      ✅ Task processed successfully")
                else:
                    self.stats["skipped"] += 1
                    print(f"      ⏭️ Task needs manual attention")
            except Exception as e:
                self.stats["failed"] += 1
                print(f"      ❌ Task failed: {e}")
        else:
            self.stats["skipped"] += 1
            print(f"      ⏭️ No auto-handler available for this task type")
        
        # 4. 保存状态
        print(f"\n[4/4] Saving state...")
        self.save_processed()
        
        # 打印统计
        print(f"\n{'='*60}")
        print(f"Scheduler Summary")
        print(f"{'='*60}")
        print(f"Processed: {self.stats['processed']}")
        print(f"Skipped:   {self.stats['skipped']}")
        print(f"Failed:    {self.stats['failed']}")
        print(f"Remaining: {len(unprocessed) - 1}")
        print(f"{'='*60}\n")
        
        return self.stats


def main():
    scheduler = BountyScheduler()
    scheduler.run()


if __name__ == "__main__":
    main()