#!/usr/bin/env python3
import json
import os
from datetime import datetime
import requests

RECORDS_FILE = "memory/pr-records.json"
GITHUB_TOKEN = open("memory/.github_token").read().strip()
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
BASE_URL = "https://api.github.com"

def load_records():
    with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_records(records):
    with open(RECORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def fetch_comments(owner, repo, pr_number):
    url = f"{BASE_URL}/repos/{owner}/{repo}/issues/{pr_number}/comments"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()

def analyze_comments(comments, last_seen_iso):
    new_comments = [c for c in comments if c['created_at'] > last_seen_iso]
    if not new_comments:
        return None, "无新评论"
    summary = []
    for c in new_comments:
        body = c['body'].lower()
        if "label" in body and "bcos" in body:
            summary.append("需添加 BCOS 标签")
        if "spdx" in body or "license" in body:
            summary.append("需添加 SPDX 许可证头")
        if "test" in body:
            summary.append("需补充测试")
    return new_comments[0]['created_at'], "; ".join(summary) if summary else "有新问题待人工处理"

def main():
    records = load_records()
    for r in records:
        owner, repo = r['project'].split('/')
        pr_num = r['pr_number']
        comments = fetch_comments(owner, repo, pr_num)
        last_seen = r.get("last_comment_at", "1970-01-01T00:00:00Z")
        last_new, summary = analyze_comments(comments, last_seen)
        if last_new:
            r["last_comment_at"] = last_new
            r["comment_summary"] = summary
            if "需添加" in summary or "需补充" in summary:
                r["status"] = "需修正"
            else:
                r["status"] = "待人工处理"
    save_records(records)
    print("Comments monitored and records updated.")

if __name__ == "__main__":
    main()