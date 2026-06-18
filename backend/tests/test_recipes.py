"""菜谱推荐测试。"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_recommend_recipes_default(auth_client):
    """测试默认菜谱推荐（无指定食材，使用库存）。"""
    resp = await auth_client.get("/api/v1/recipes/recommend")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    recipes = body["data"]
    assert isinstance(recipes, list)
    assert len(recipes) > 0
    # 应返回本地预设菜谱
    names = [r["name"] for r in recipes]
    assert "西红柿炒蛋" in names


async def test_recommend_recipes_with_ingredients(auth_client):
    """测试指定食材推荐菜谱。"""
    resp = await auth_client.get("/api/v1/recipes/recommend?ingredients=西红柿,鸡蛋,土豆,牛肉")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    recipes = body["data"]
    # 西红柿炒蛋应排在前面（匹配数高）
    assert recipes[0]["name"] == "西红柿炒蛋"
    assert recipes[0]["match_count"] == 2


async def test_recommend_recipes_limit(auth_client):
    """测试推荐数量限制。"""
    resp = await auth_client.get("/api/v1/recipes/recommend?limit=2")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["data"]) <= 2


async def test_get_local_recipe_by_id(auth_client):
    """测试获取本地菜谱详情。"""
    resp = await auth_client.get("/api/v1/recipes/local-0")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["data"]["name"] == "西红柿炒蛋"
    assert body["data"]["source"] == "local"
    assert len(body["data"]["steps"]) > 0
    assert len(body["data"]["ingredients"]) > 0


async def test_get_recipe_not_found(auth_client):
    """测试获取不存在的菜谱。"""
    resp = await auth_client.get("/api/v1/recipes/local-999")
    assert resp.status_code == 404
    body = resp.json()
    assert body["code"] == 40401


async def test_recipe_contains_required_fields(auth_client):
    """测试菜谱响应包含必需字段。"""
    resp = await auth_client.get("/api/v1/recipes/recommend?limit=1")
    body = resp.json()
    recipe = body["data"][0]
    assert "recipe_id" in recipe
    assert "name" in recipe
    assert "description" in recipe
    assert "cook_time" in recipe
    assert "calories" in recipe
    assert "servings" in recipe
    assert "steps" in recipe
    assert "ingredients" in recipe
    assert "source" in recipe
