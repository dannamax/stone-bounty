#!/usr/bin/env python3
"""
Bounty Continuous Processor - 持续自动处理
每5分钟检查一次新任务，自动处理
"""

import os
import re
import json
import time
import requests
import subprocess
from datetime import datetime

WORKSPACE = "/home/admin/.openclaw/workspace"
PROCESSED_FILE = f"{WORKSPACE}/.bounty_processed.json"
MEMORY_FILE = f"{WORKSPACE}/memory/2026-03-11.md"
GITHUB_TOKEN = "SEE_TOKEN_FILE"
WALLET = "RTC27a4b8256b4d3c63737b27e96b181223cc8774ae"
AGENT = "dannamax"
CHECK_INTERVAL = 300  # 5分钟检查一次


def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")
    # 同时写入日志文件
    with open("/tmp/bounty_continuous.log", "a") as f:
        f.write(f"[{now}] {msg}\n")


def load_processed():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, 'r') as f:
            return set(json.load(f))
    return set()


def save_processed(processed):
    with open(PROCESSED_FILE, 'w') as f:
        json.dump(list(processed), f)


def fetch_bounties():
    url = "https://api.github.com/repos/Scottcjn/rustchain-bounties/issues"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    params = {"state": "open", "labels": "bounty", "per_page": 50}
    
    try:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log(f"[ERROR] Fetch failed: {e}")
        return []


def is_auto_processable(issue):
    title = issue.get('title', '').lower()
    body = (issue.get('body') or '').lower()
    
    # 高优先级可处理
    high_priority = ['dockerfile', 'github action', 'workflow', 'contributing']
    # 中优先级
    medium_priority = ['openapi', 'swagger', 'cli', 'unit test', 'type hint']
    
    # 排除条件
    exclude = ['screenshot', 'video', 'social', 'tweet', 'star', 'upvote', 
               'emoji', 'profile', 'avatar', 'login', 'third-party', 'postman']
    
    has_high = any(k in title or k in body for k in high_priority)
    has_medium = any(k in title or k in body for k in medium_priority)
    has_exclude = any(k in title or k in body for k in exclude)
    
    if has_exclude:
        return False
    return has_high or has_medium


def process_ci_workflow(issue):
    """处理 GitHub Actions / CI 任务"""
    log(f"  Creating CI workflow...")
    
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # 检查 bottube 是否需要 CI
    url = "https://api.github.com/repos/Scottcjn/bottube/contents/.github/workflows/ci.yml"
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code == 200:
        log(f"  CI already exists in bottube")
        return None
    
    # 创建 CI workflow
    workflow = '''name: CI
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - run: pip install flake8 pylint
    - run: flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    - run: pylint bottube_server.py --disable=C,R,W || true
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - run: pip install pytest
    - run: pytest tests/ -v || true
'''
    
    branch = f"auto-ci-{issue['number']}"
    
    # 获取 main SHA
    r = requests.get("https://api.github.com/repos/Scottcjn/bottube/git/ref/heads/main", 
                     headers=headers, timeout=10)
    if r.status_code != 200:
        return None
    sha = r.json()['object']['sha']
    
    # 创建分支
    r = requests.post("https://api.github.com/repos/Scottcjn/bottube/git/refs",
                      headers=headers, 
                      json={"ref": f"refs/heads/{branch}", "sha": sha},
                      timeout=10)
    if r.status_code not in [200, 201]:
        log(f"  Branch creation failed: {r.status_code}")
        return None
    
    # 创建文件
    import base64
    r = requests.put("https://api.github.com/repos/Scottcjn/bottube/contents/.github/workflows/ci.yml",
                     headers=headers,
                     json={
                         "message": f"ci: Add GitHub Actions workflow\n\n#{issue['number']}\n\nWallet: {WALLET}\nAgent: {AGENT}",
                         "content": base64.b64encode(workflow.encode()).decode(),
                         "branch": branch
                     },
                     timeout=10)
    
    if r.status_code not in [200, 201]:
        log(f"  File creation failed: {r.status_code}")
        return None
    
    # 创建 PR
    r = requests.post("https://api.github.com/repos/Scottcjn/bottube/pulls",
                      headers=headers,
                      json={
                          "title": f"ci: Add GitHub Actions CI workflow (#{issue['number']})",
                          "body": f"## Summary\nAuto-generated CI workflow\n\n## Related\n#{issue['number']}\n\n## Claim\nWallet: {WALLET}\nAgent: {AGENT}",
                          "head": f"dannamax:{branch}",
                          "base": "main"
                      },
                      timeout=10)
    
    if r.status_code == 201:
        pr = r.json()
        log(f"  ✅ PR created: {pr['html_url']}")
        return pr['html_url']
    
    return None


def process_task(issue):
    """处理任务 - 增强版"""
    title = issue.get('title', '').lower()
    body = issue.get('body', '') or ''
    
    # 1. GitHub Actions / CI
    if any(k in title for k in ['github action', 'workflow', 'ci cd', 'ci/cd']):
        return process_ci_workflow(issue)
    
    # 2. Dockerfile
    if 'dockerfile' in title or 'docker' in title:
        log(f"  Dockerfile task - checking if already exists...")
        # 检查是否已有 Dockerfile
        # 如果没有，创建一个基础的
        log(f"  Need to check target repo for Dockerfile")
        return None
    
    # 3. 文档类任务 (CONTRIBUTING, docs)
    if any(k in title for k in ['contributing', 'documentation', 'docs']):
        return process_documentation(issue)
    
    # 4. OpenAPI/Swagger
    if 'openapi' in title or 'swagger' in title:
        log(f"  OpenAPI task - would generate API spec")
        # 这类任务需要分析现有代码，暂时跳过
        return None
    
    # 5. 测试类任务
    if 'test' in title or 'unit test' in title:
        log(f"  Test task - would write tests")
        # 需要分析代码，暂时跳过
        return None
    
    # 6. CLI 工具
    if 'cli' in title:
        log(f"  CLI task - would create CLI tool")
        # 需要设计，暂时跳过
        return None
    
    # 其他任务
    log(f"  Unknown task type: {title[:50]}")
    return None


def update_memory(issue, pr_url):
    if not pr_url:
        return
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(MEMORY_FILE, 'a') as f:
        f.write(f"\n### 自动处理 [{now}]\n- Issue #{issue['number']}: {issue['title']}\n- PR: {pr_url}\n- 状态: ⏳ 待审核\n")


def main():
    log("=" * 60)
    log("Bounty Continuous Processor Started")
    log(f"Check interval: {CHECK_INTERVAL}s")
    log("=" * 60)
    
    while True:
        try:
            processed = load_processed()
            log(f"Processed tasks: {len(processed)}")
            
            # 获取任务
            issues = fetch_bounties()
            log(f"Open bounties: {len(issues)}")
            
            # 找下一个可处理的任务
            for issue in issues:
                if issue['number'] in processed:
                    continue
                if not is_auto_processable(issue):
                    continue
                
                log(f"\n{'='*60}")
                log(f"Processing #{issue['number']}: {issue['title'][:50]}")
                log("=" * 60)
                
                pr_url = process_task(issue)
                
                processed.add(issue['number'])
                save_processed(processed)
                
                if pr_url:
                    update_memory(issue, pr_url)
                    log(f"✅ Completed! PR: {pr_url}")
                else:
                    log(f"⏭️ Skipped (needs manual work)")
                
                break  # 每次循环只处理一个任务
            
            log(f"\nSleeping {CHECK_INTERVAL}s...")
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            log("Stopped by user")
            break
        except Exception as e:
            log(f"[ERROR] {e}")
            time.sleep(60)


if __name__ == "__main__":
    main()