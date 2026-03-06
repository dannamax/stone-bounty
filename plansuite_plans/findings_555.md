# findings.md

## 关键发现
- 赏金 #555 需要实现两个新的 API 端点
- 必须使用 Flask test_client() 进行集成测试，不能使用 mock
- 需要遵循 tests/test_tipping.py 的测试模式
- SQL JOIN 查询需要在 subscriptions 表上执行

## 决策记录
- 选择直接实现完整的 API 端点而不是部分实现
- 决定创建独立的测试文件而不是修改现有文件
- 采用标准的 Flask 蓝图模式组织代码

## 验证命令/步骤
- python -m pytest tests/test_social_graph_api.py
- curl http://localhost:5000/api/social/graph
- curl http://localhost:5000/api/agents/test_agent/interactions

## 回滚步骤
- 删除新增的测试文件
- 移除 API 路由注册
- 恢复原始测试配置
