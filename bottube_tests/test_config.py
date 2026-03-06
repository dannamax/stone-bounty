
# BoTTube Social Graph API Test Configuration
test_endpoints = [
    "/api/social/graph",
    "/api/agents/{name}/interactions"
]

database_tables = ["subscriptions"]
test_data_requirements = {
    "min_agents": 3,
    "min_subscriptions": 5,
    "test_scenarios": ["normal", "boundary", "error"]
}
