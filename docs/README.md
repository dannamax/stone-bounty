# Stone Bounty - GitHub 赏金猎人系统

## 系统概述
Stone Bounty 是一个自动化系统，专门用于识别、分析并向带有赏金计划的 GitHub 仓库提交高质量贡献。系统专注于文档改进、小型 bug 修复和功能增强，并获得相应的货币奖励。

## 核心特性
- 🔍 **赏金发现**: 自动查找带有 bounty/reward 标签的问题
- 🎯 **智能过滤**: 避免复杂项目（已加入黑名单：rust-lang/rust, vuejs/vue 等）
- ✅ **质量控制**: 确保实际代码更改，而非模板注释
- 📊 **成功追踪**: 监控 PR 状态和赏金申领
- ⚠️ **紧急停止**: 高质量贡献的手动专用模式

## 策略原则
- 专注于小型、可实现的任务（文档、测试、小型修复）
- 避免需要 CLA 或深度专业知识的大型/复杂项目
- 所有 PR 提交前都需要人工审核
- 成功率目标：>25%（当前为 12.5%）

## 当前状态
- ✅ **活跃 PR**: Scottcjn/Rustchain #247 (75 RTC 等待审核)
- ✅ **已完成**: Scottcjn/Rustchain #139 (10 RTC 已申领)
- ⚠️ **紧急停止**: 所有自动化已禁用，仅限手动模式

## 安装与设置

### 1. 克隆技能仓库
```bash
git clone https://github.com/your-repo/stone-bounty.git
```

### 2. 安装依赖
```bash
cd stone-bounty && ./scripts/setup.sh
```

### 3. 配置认证信息
```bash
# 设置 GitHub Token
echo "your_github_token" > .github_token

# 设置钱包地址
echo "your_wallet_address" > .wallet_address
```

## 使用方法

### 监控新机会（需要人工审核）
```bash
./scripts/bounty_monitor.sh --manual-only
```

### 提交 PR（人工验证后）
```bash
./scripts/pr_submitter.sh --issue-url "https://github.com/repo/issue/123"
```

### 验证贡献质量
```bash
./scripts/validator.sh --pr-url "https://github.com/repo/pull/456"
```

## 配置说明

编辑 `config/automation_config.json` 来自定义行为：
- `emergency_stop_active`: true（推荐）
- `manual_only_mode`: true（质量必需）
- `max_daily_submissions`: 0（紧急模式下禁用）

## 安全指南
- 永远不要提交自动化/模板 PR
- 始终验证问题是否有明确的赏金金额
- 避免需要 CLA 协议的项目
- 专注于文档和小型改进
- 所有提交都需要人工审核

## 成功指标
- **目标成功率**: >25%
- **当前成功率**: 12.5% (1/8)
- **活跃赏金**: 1 (Rustchain #213)
- **总申领**: 10 RTC

## 最佳实践

### ✅ 应该做：
- 专注于 Rustchain 和类似的小型项目
- 对所有贡献进行人工审核
- 保持高质量标准

### ❌ 不应该做：
- 向黑名单中的大型项目提交
- 启用自动化批量提交
- 提交模板/占位符 PR

## 许可证
MIT 许可证 - 负责任地使用并贡献高质量工作。

---

这个技能包提供了一个负责任的赏金猎取框架，同时保持高质量标准，避免导致紧急停止模式的陷阱。