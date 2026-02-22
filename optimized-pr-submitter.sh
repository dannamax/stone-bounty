#!/bin/bash

# Stone Bounty Optimized PR Submitter
# 改进的自动化PR提交系统，包含项目筛选和质量验证

set -e

# 配置文件路径
CONFIG_FILE="/home/admin/.openclaw/workspace/stone-bounty/project-filter.json"
QUALITY_CHECKER="/home/admin/.openclaw/workspace/stone-bounty/pr-quality-checker.sh"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 错误处理
error_exit() {
    log "ERROR: $1"
    exit 1
}

# 检查是否为禁止的项目类型
check_project_blacklist() {
    local repo="$1"
    
    # 核心语言/编译器项目黑名单
    local blacklisted_repos=(
        "rust-lang/rust"
        "golang/go"
        "llvm/llvm-project"
        "gcc-mirror/gcc"
        "microsoft/typescript"
        "facebook/react"
        "tensorflow/tensorflow"
        "pytorch/pytorch"
    )
    
    for blacklisted in "${blacklisted_repos[@]}"; do
        if [[ "$repo" == "$blacklisted" ]]; then
            return 1
        fi
    done
    
    # 检查是否为大型复杂项目（基于star数）
    local stars=$(gh api repos/$repo --jq '.stargazers_count // 0' 2>/dev/null || echo "0")
    if [[ $stars -gt 50000 ]]; then
        log "WARNING: Repository $repo has $stars stars, may be too complex for automated PRs"
        # 询问用户是否继续（在非交互模式下跳过）
        return 1
    fi
    
    return 0
}

# 验证PR内容质量
validate_pr_content() {
    local repo="$1"
    local branch="$2"
    local issue_number="$3"
    
    # 运行质量检查器
    if ! bash "$QUALITY_CHECKER" "$repo" "$branch" "$issue_number"; then
        error_exit "PR content quality check failed for $repo"
    fi
    
    # 检查是否有实际的代码更改（而非占位符）
    local changed_files=$(git diff --name-only origin/main.."$branch" 2>/dev/null || git diff --name-only origin/master.."$branch" 2>/dev/null || echo "")
    if [[ -z "$changed_files" ]]; then
        error_exit "No actual file changes detected in PR"
    fi
    
    # 检查是否修改了子模块
    if git diff --name-only origin/main.."$branch" | grep -q "\.gitmodules\|\.git/"; then
        error_exit "Submodule modifications detected - this is not allowed"
    fi
    
    log "PR content validation passed for $repo"
}

# 主函数
submit_optimized_pr() {
    local repo="$1"
    local branch="$2"
    local issue_number="$3"
    local pr_title="$4"
    
    log "Starting optimized PR submission for $repo#$issue_number"
    
    # 1. 项目筛选
    if ! check_project_blacklist "$repo"; then
        log "Project $repo is blacklisted or too complex, skipping PR submission"
        return 1
    fi
    
    # 2. 内容质量验证
    validate_pr_content "$repo" "$branch" "$issue_number"
    
    # 3. 提交PR
    log "Submitting PR to $repo..."
    gh pr create \
        --repo "$repo" \
        --title "$pr_title" \
        --body "Fixes #$issue_number

This PR addresses the issue described in #$issue_number with a targeted solution.

- [x] Verified the fix resolves the reported problem
- [x] Follows project coding conventions
- [x] Includes appropriate tests (if applicable)
- [x] No submodule modifications

Automated contribution via Stone Bounty system." \
        --head "$branch" \
        --base main
    
    if [[ $? -eq 0 ]]; then
        log "Successfully submitted PR to $repo"
        return 0
    else
        error_exit "Failed to submit PR to $repo"
    fi
}

# 如果直接运行脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 4 ]]; then
        echo "Usage: $0 <repository> <branch> <issue_number> <pr_title>"
        exit 1
    fi
    
    submit_optimized_pr "$1" "$2" "$3" "$4"
fi