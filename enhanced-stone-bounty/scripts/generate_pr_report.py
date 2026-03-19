#!/usr/bin/env python3
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import shutil

RECORDS_FILE = "memory/pr-records.json"
OUTPUT_FILE = f"memory/pr_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md"

# ===== 邮件配置 =====
SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465
EMAIL_ACCOUNT = "15110082921@163.com"
EMAIL_PASSWORD = "JJhrzcKP27ErkffC"
TO_EMAIL = "15110082921@163.com"
# =====================

def load_records():
    if not os.path.exists(RECORDS_FILE):
        return []
    with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_report(md_text):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(md_text)
    print(f"Report saved to {OUTPUT_FILE}")

def generate_html_report(records):
    html = []
    html.append("<h2>PR 处理清单报告</h2>")
    html.append(f"<p><strong>生成时间：</strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
    html.append("<table border='1' cellspacing='0' cellpadding='5' style='border-collapse:collapse;'>")
    html.append("<thead><tr>")
    html.append("<th>项目名称</th><th>Issue号</th><th>PR号</th><th>PR提交历史</th><th>提交PR时间</th><th>更新时间</th><th>当前状态</th>")
    html.append("</tr></thead><tbody>")
    for r in records:
        commits_html = "<br>".join(r["commits"])
        html.append(f"<tr>")
        html.append(f"<td>{r['project']}</td>")
        html.append(f"<td>#{r['issue_number']}</td>")
        html.append(f"<td><a href='{r['pr_url']}'>#{r['pr_number']}</a></td>")
        html.append(f"<td>{commits_html}</td>")
        html.append(f"<td>{r['pr_created_at']}</td>")
        html.append(f"<td>{r['pr_updated_at']}</td>")
        html.append(f"<td>{r['status']}</td>")
        html.append(f"</tr>")
    html.append("</tbody></table>")
    return "\n".join(html)

def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ACCOUNT
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html", "utf-8"))
    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ACCOUNT, [TO_EMAIL], msg.as_string())
        server.quit()
        print("✅ Email sent successfully")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    records = load_records()
    md = generate_html_report(records).replace("<h2>", "# ").replace("<br>", "\\n").replace("<", "&lt;").replace(">", "&gt;")
    save_report(md)

    subject = f"PR 处理清单报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    send_email(subject, generate_html_report(records))

    # === 真实清理（带日志） ===
    def do_cleanup(records):
        log_file = "memory/cleanup.log"
        with open(log_file, "a", encoding="utf-8") as log:
            for r in records:
                if r.get("status") in ["已打款", "已关闭"]:
                    if "Rustchain" in r["project"]:
                        dir_path = os.path.expanduser("~/rustchain-dannamax")
                    else:
                        dir_path = os.path.expanduser(f"~/{r['project'].split('/')[-1].lower()}-dannamax")
                    if os.path.exists(dir_path):
                        log.write(f"{datetime.now().isoformat()} - Removing {dir_path} for PR #{r['pr_number']} ({r['status']})\n")
                        print(f"[CLEANUP] Removing {dir_path} for PR #{r['pr_number']} ({r['status']})")
                        try:
                            shutil.rmtree(dir_path)
                            log.write(f"{datetime.now().isoformat()} - Removed successfully\n")
                        except Exception as e:
                            log.write(f"{datetime.now().isoformat()} - ERROR removing {dir_path}: {e}\n")
                            print(f"[CLEANUP ERROR] {e}")
        print(f"Cleanup log written to {log_file}")

    do_cleanup(records)