# GitHub 认证设置指南

## 为 Stone Bounty 系统配置您的 GitHub 账户

### 您的账户信息
- **GitHub 用户名**: `dannamax`
- **邮箱地址**: `15110082921@163.com`

### 步骤 1: 创建 GitHub Personal Access Token

1. 访问 [GitHub Token Settings](https://github.com/settings/tokens)
2. 点击 **"Generate new token"**
3. 选择 **"Fine-grained tokens"**
4. 配置令牌权限：
   - **Repository permissions**:
     - Contents: Read and write
     - Pull requests: Read and write  
     - Issues: Read and write
     - Metadata: Read-only
   - **Organization permissions** (如果需要):
     - Members: Read-only
5. 设置令牌有效期（建议 90 天）
6. 点击 **"Generate token"**
7. **立即复制令牌**（只显示一次！）

### 步骤 2: 安全存储令牌

```bash
# 在 stone-bounty 目录中创建令牌文件
cd stone-bounty
echo "您的_personal_access_token_粘贴在这里" > .github_token

# 设置安全权限
chmod 600 .github_token
```

### 步骤 3: 配置钱包地址

```bash
# 创建钱包地址文件（用于接收赏金）
echo "您的钱包地址" > .wallet_address
chmod 600 .wallet_address
```

### 步骤 4: 验证配置

```bash
# 运行设置脚本验证配置
./scripts/setup-github-auth.sh

# 测试 GitHub 连接
git config --get user.name    # 应该显示 dannamax
git config --get user.email   # 应该显示 15110082921@163.com
```

### 安全注意事项

⚠️ **重要安全提醒**:
- `.github_token` 和 `.wallet_address` 文件已被添加到 `.gitignore`
- 这些文件**永远不会**被提交到 Git 仓库
- 定期轮换您的 GitHub token（建议每 90 天）
- 如果怀疑令牌泄露，立即在 GitHub 上撤销它

### 故障排除

**如果遇到认证问题**:
1. 检查 `.github_token` 文件是否存在且权限正确 (`chmod 600`)
2. 验证令牌是否具有正确的权限范围
3. 确保没有多余的空格或换行符
4. 测试基本的 Git 操作：
   ```bash
   git ls-remote https://github.com/dannamax/any-repo.git
   ```

**令牌权限不足错误**:
- 确保令牌有 `repo` 权限（完整仓库访问）
- 对于组织仓库，可能需要额外的组织权限

完成这些步骤后，您的 Stone Bounty 系统就可以使用您的个人 GitHub 账户进行操作了！