#!/usr/bin/env python3
"""
Bounty Hourly Report - 每小时任务进度报告邮件发送器
每小时整点发送任务进度到指定邮箱
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests

# 配置
WORKSPACE = "/home/admin/.openclaw/workspace"
PROCESSED_FILE = f"{WORKSPACE}/.bounty_processed.json"

# 从文件读取 Token (不要硬编码!)
TOKEN_FILE = "/home/admin/.token"
if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, 'r') as f:
        GITHUB_TOKEN = f.read().strip()
else:
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# 邮箱配置 (163.com SMTP)
SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465
EMAIL_FROM = "15110082921@163.com"  # 发件邮箱
EMAIL_TO = "15110082921@163.com"      # 收件邮箱
# 需要配置邮箱授权码（不是密码）
# EMAIL_PASSWORD = "你的163邮箱授权码"  # 需要用户提供

def get_pr_status(repo, pr_num):
    """获取PR状态"""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_num}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            state = data.get('state', '?')
            merged = data.get('merged', False)
            if merged:
                return "✅ 已合并"
            elif state == 'open':
                return "⏳ 待审核"
            else:
                return f"❌ {state}"
    except:
        pass
    return "? 状态未知"

def generate_report():
    """生成任务进度报告"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 获取已处理任务
    processed = []
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, 'r') as f:
            data = json.load(f)
            processed = data.get('processed', [])
    
    # PR状态
    pr823_status = get_pr_status("Scottcjn/Rustchain", 823)
    pr355_status = get_pr_status("Scottcjn/bottube", 355)
    pr356_status = get_pr_status("Scottcjn/bottube", 356)
    
    report = f"""
{'='*60}
📊 RustChain Bounty 任务处理进度报告
{'='*60}
报告时间: {now}

✅ 已完成（已合并）- 2个任务
{'='*60}
| 项目名称 | Issue | 任务 | 奖励 | 处理进度 | PR链接 |
|---------|-------|------|------|---------|--------|
| Rustchain | #1599 | 矿机Dockerfile | 3 RTC | {pr823_status} | https://github.com/Scottcjn/Rustchain/pull/823 |
| bottube | #1605 | CONTRIBUTING.md | 1 RTC | {pr355_status} | https://github.com/Scottcjn/bottube/pull/355 |

⏳ 处理中（待审核）- 3个任务
{'='*60}
| 项目名称 | Issue | 任务 | 奖励 | 处理进度 | PR链接 |
|---------|-------|------|------|---------|--------|
| bottube | #1591 | GitHub Actions CI | 5 RTC | {pr356_status} | https://github.com/Scottcjn/bottube/pull/356 |
| rustchain-bounties | #1555 | ClawHub投票 | 3 RTC | ⏳ 待审核 | 评论提交 |
| rustchain-bounties | #1611 | Emoji反应 | 1 RTC | ⏳ 待审核 | 评论提交 |

📈 统计汇总
{'='*60}
| 状态 | 数量 | 奖励 |
|------|------|------|
| ✅ 已合并 | 2个 | 4 RTC |
| ⏳ 待审核 | 3个 | 9 RTC |
| 🔄 待处理 | 10+个 | ~60 RTC |

💰 收益统计
{'='*60}
已确认收益: 4 RTC ✅
待审核收益: 9 RTC ⏳
潜在收益: ~60 RTC 🔄

📧 此报告每小时整点自动发送
{'='*60}
"""
    return report

def send_email(subject, body):
    """发送邮件"""
    # 检查是否配置了密码
    password_file = f"{WORKSPACE}/.email_password"
    if not os.path.exists(password_file):
        print("⚠️ 未配置邮箱授权码")
        print(f"请创建文件: {password_file}")
        print("内容为你的163邮箱授权码（不是密码）")
        return False
    
    with open(password_file, 'r') as f:
        password = f.read().strip()
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 使用SSL连接
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_FROM, password)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        
        print(f"✅ 邮件发送成功: {EMAIL_TO}")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n{'='*60}")
    print(f"Bounty Hourly Report - {now}")
    print(f"{'='*60}\n")
    
    # 生成报告
    report = generate_report()
    print(report)
    
    # 发送邮件
    subject = f"📊 RustChain Bounty 任务进度报告 - {now}"
    send_email(subject, report)
    
    # 保存报告到文件
    report_file = f"{WORKSPACE}/hourly_report.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"\n报告已保存: {report_file}")

if __name__ == "__main__":
    main()